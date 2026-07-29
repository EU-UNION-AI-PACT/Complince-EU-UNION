"""CountryAdapter Protocol — every EU/EFTA/partner nation implements this."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class CountryConfig:
    code: str
    name: str
    flag: str
    scheme: str
    trust_framework: str
    supported_formats: list[str]
    loa_mapping: dict[str, str]
    reference_url: str
    id_hash_algorithm: str = "SHA-256"
    implemented: bool = False


class CountryAdapter(Protocol):
    config: CountryConfig

    async def verify(
        self,
        presentation: str,
        *,
        format: str,
        audience: str | None,
        nonce: str | None,
    ) -> dict[str, Any]: ...

    def hash_national_id(self, national_id: str) -> str: ...


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
