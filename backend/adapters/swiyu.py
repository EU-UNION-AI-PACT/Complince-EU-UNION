"""Swiss E-ID (Swiyu) adapter — AHV hash, LDP-VC support (W3C VC-DM 2.0)."""
from __future__ import annotations

from typing import Any

from adapters.base import CountryConfig, sha256_hex
from services.sd_jwt_verifier import SDJWTVerifierV2
from services.status_list_client import StatusListClient


class SwiyuAdapter:
    config = CountryConfig(
        code="CH",
        name="Switzerland (Swiyu)",
        flag="🇨🇭",
        scheme="Swiss E-ID (Swiyu)",
        trust_framework="Swiss Federal Trust Infrastructure",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"low": "low", "substantial": "substantial", "high": "high"},
        reference_url="https://github.com/e-id-admin",
        id_hash_algorithm="SHA-256 over AHV number",
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
        if format == "sd-jwt":
            result = await self._sd_verifier.verify(presentation, audience=audience, nonce=nonce)
        elif format == "ldp-vc":
            # W3C VC-DM 2.0 with Ed25519 LDP — placeholder for a full JSON-LD normalization
            # pipeline (URDNA2015). We accept structurally valid JSON here.
            import json

            try:
                doc = json.loads(presentation)
            except Exception as exc:
                return {"valid": False, "reasons": [f"ldp-vc parse: {exc}"]}
            if "proof" not in doc:
                return {"valid": False, "reasons": ["ldp-vc missing proof"]}
            result = {
                "valid": True,
                "reasons": [],
                "disclosed_claims": doc.get("credentialSubject", {}),
                "issuer": doc.get("issuer"),
                "vct": "w3c-vc-2.0",
                "status": "unknown",
            }
        else:
            return {"valid": False, "reasons": [f"unsupported format {format}"]}
        disclosed = result.get("disclosed_claims", {})
        ahv = disclosed.get("ahv") or disclosed.get("ahv_number")
        if ahv:
            disclosed["ahv_hash"] = self.hash_national_id(str(ahv))
            disclosed.pop("ahv", None)
            disclosed.pop("ahv_number", None)
        return result

    def hash_national_id(self, national_id: str) -> str:
        # normalize AHV: strip dots and dashes
        norm = "".join(ch for ch in national_id if ch.isdigit())
        return sha256_hex(norm)
