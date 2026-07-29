"""OpenID4VCI Issuer — /nonce + /credential."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from database import get_db
from models import (
    CredentialOfferRequest,
    CredentialResponse,
    NonceResponse,
)
from services.audit_log import append_event
from services.proof_jwt_validator import ProofJWTValidator
from services.sd_jwt_builder import SDJWTBuilder
from services.status_list_client import StatusListClient

router = APIRouter(prefix="/issuer", tags=["Issuer (OpenID4VCI)"])


def _issuer_url() -> str:
    return os.environ.get("ISSUER_URL", "http://localhost:8001")


def _status_uri() -> str:
    return f"{_issuer_url()}/api/issuer/status-list/primary"


@router.post("/nonce", response_model=NonceResponse)
async def issue_nonce() -> NonceResponse:
    validator = ProofJWTValidator(expected_audience=_issuer_url())
    nonce, ttl = await validator.issue_nonce()
    return NonceResponse(c_nonce=nonce, c_nonce_expires_in=ttl)


@router.post("/credential", response_model=CredentialResponse)
async def issue_credential(req: CredentialOfferRequest) -> CredentialResponse:
    # Proof of Possession — the wallet's holder-binding JWT
    if req.proof_jwt:
        validator = ProofJWTValidator(expected_audience=_issuer_url())
        proof = await validator.validate(req.proof_jwt, req.holder_jwk)
        if not proof["valid"]:
            raise HTTPException(400, {"error": "invalid_proof", "reasons": proof["reasons"]})

    db = get_db()
    counter = await db.status_counter.find_one_and_update(
        {"_id": "primary"},
        {"$inc": {"next": 1}},
        upsert=True,
        return_document=True,
    )
    status_idx = counter["next"] if counter else 0

    builder = SDJWTBuilder(issuer=_issuer_url(), vct=req.vct)
    compact, count = await builder.issue(
        claims=req.subject_claims,
        holder_jwk=req.holder_jwk,
        status_index=status_idx,
        status_list_uri=_status_uri(),
    )

    await db.issued_credentials.insert_one(
        {
            "vct": req.vct,
            "status_index": status_idx,
            "country_code": req.country_code,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "compact_head": compact[:120],
        }
    )
    await StatusListClient().set_status(_status_uri(), status_idx, "active")

    await append_event(
        event_type="credential.issued",
        actor="issuer",
        subject=req.subject_claims.get("family_name"),
        payload={"vct": req.vct, "country": req.country_code, "status_idx": status_idx},
    )
    return CredentialResponse(credential=compact, disclosures_count=count, vct=req.vct)


@router.get("/status-list/{list_id}")
async def get_status_list(list_id: str) -> dict:
    """Return the status list bit vector (compressed b64)."""
    uri = f"{_issuer_url()}/api/issuer/status-list/{list_id}"
    doc = await get_db().status_list_docs.find_one({"uri": uri}, {"_id": 0})
    if not doc:
        return {"uri": uri, "bits_b64": "", "size": 0}
    return doc


@router.post("/status-list/{list_id}/revoke/{idx}")
async def revoke(list_id: str, idx: int) -> dict:
    uri = f"{_issuer_url()}/api/issuer/status-list/{list_id}"
    await StatusListClient().set_status(uri, idx, "revoked")
    await append_event(
        event_type="credential.revoked",
        actor="issuer",
        payload={"status_idx": idx, "list": list_id},
    )
    return {"revoked": True, "idx": idx}
