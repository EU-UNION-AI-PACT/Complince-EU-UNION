"""AGID SPID / CIE adapter — Codice Fiscale hash."""
from __future__ import annotations

from typing import Any

from adapters.base import CountryConfig, sha256_hex
from services.sd_jwt_verifier import SDJWTVerifierV2
from services.status_list_client import StatusListClient


class SpidCieAdapter:
    config = CountryConfig(
        code="IT",
        name="Italy (SPID / CIE)",
        flag="🇮🇹",
        scheme="SPID / CIE",
        trust_framework="AGID / eIDAS",
        supported_formats=["sd-jwt"],
        loa_mapping={"spidL1": "low", "spidL2": "substantial", "spidL3": "high"},
        reference_url="https://github.com/italia",
        id_hash_algorithm="SHA-256 over Codice Fiscale",
        implemented=True,
    )

    def __init__(self) -> None:
        self._sd_verifier = SDJWTVerifierV2(StatusListClient())

    async def verify(
        self,
        presentation: str,
        *,
        format: str,
        audience: str | None,
        nonce: str | None,
    ) -> dict[str, Any]:
        if format != "sd-jwt":
            return {"valid": False, "reasons": ["SPID / CIE requires SD-JWT VC"]}
        result = await self._sd_verifier.verify(presentation, audience=audience, nonce=nonce)
        disclosed = result.get("disclosed_claims", {})
        cf = disclosed.get("codice_fiscale") or disclosed.get("codiceFiscale")
        if cf:
            disclosed["codice_fiscale_hash"] = self.hash_national_id(cf)
            disclosed.pop("codice_fiscale", None)
            disclosed.pop("codiceFiscale", None)
        return result

    def hash_national_id(self, national_id: str) -> str:
        return sha256_hex(national_id.strip().upper())
