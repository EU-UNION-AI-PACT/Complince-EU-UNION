"""OpenID4VP Verifier."""
from __future__ import annotations

from fastapi import APIRouter

from models import VerifyRequest, VerifyResponse
from services.audit_log import append_event
from services.sd_jwt_verifier import SDJWTVerifierV2
from services.status_list_client import StatusListClient

router = APIRouter(prefix="/verifier", tags=["Verifier (OpenID4VP)"])


@router.post("/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest) -> VerifyResponse:
    verifier = SDJWTVerifierV2(StatusListClient())
    result = await verifier.verify(req.presentation, audience=req.audience, nonce=req.nonce)
    # simple LoA heuristic based on VCT
    loa = None
    vct = result.get("vct") or ""
    if "pid" in vct or "mdl" in vct:
        loa = "high"
    elif "email" in vct:
        loa = "substantial"
    result["loa"] = loa
    result["trust_chain"] = [result.get("issuer") or "unknown"]
    await append_event(
        event_type="presentation.verified",
        actor="verifier",
        subject=result.get("disclosed_claims", {}).get("family_name"),
        payload={"valid": result["valid"], "reasons": result["reasons"], "vct": vct},
    )
    return VerifyResponse(**result)
