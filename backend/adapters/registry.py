"""Country adapter registry — 11 countries with 4 real + 7 stub implementations."""
from __future__ import annotations

from adapters.base import CountryAdapter, CountryConfig, sha256_hex
from adapters.eu_arf import EUARFAdapter
from adapters.france_connect import FranceConnectAdapter
from adapters.spid_cie import SpidCieAdapter
from adapters.swiyu import SwiyuAdapter


class _StubAdapter:
    """Concrete Country config but returns a structured `not implemented` reply."""

    def __init__(self, config: CountryConfig) -> None:
        self.config = config

    async def verify(self, presentation, *, format, audience, nonce):
        return {
            "valid": False,
            "reasons": [f"adapter {self.config.code} not yet wired — protocol interface only"],
            "disclosed_claims": {},
        }

    def hash_national_id(self, national_id: str) -> str:
        return sha256_hex(national_id.strip())


STUB_COUNTRIES: list[CountryConfig] = [
    CountryConfig(
        code="PT",
        name="Portugal (Autenticação.gov)",
        flag="🇵🇹",
        scheme="Autenticação.gov",
        trust_framework="AMA / eIDAS",
        supported_formats=["sd-jwt"],
        loa_mapping={"AL1": "low", "AL2": "substantial", "AL3": "high"},
        reference_url="https://www.autenticacao.gov.pt/",
        id_hash_algorithm="SHA-256 over NIC",
    ),
    CountryConfig(
        code="SE",
        name="Sweden (BankID)",
        flag="🇸🇪",
        scheme="BankID",
        trust_framework="Finansiell ID-Teknik / eIDAS",
        supported_formats=["sd-jwt"],
        loa_mapping={"basic": "substantial", "advanced": "high"},
        reference_url="https://www.bankid.com/",
        id_hash_algorithm="SHA-256 over Personnummer",
    ),
    CountryConfig(
        code="NO",
        name="Norway (ID-porten)",
        flag="🇳🇴",
        scheme="ID-porten",
        trust_framework="Digdir",
        supported_formats=["sd-jwt"],
        loa_mapping={"idporten-loa-substantial": "substantial", "idporten-loa-high": "high"},
        reference_url="https://docs.digdir.no/",
        id_hash_algorithm="SHA-256 over Fødselsnummer",
    ),
    CountryConfig(
        code="DK",
        name="Denmark (MitID)",
        flag="🇩🇰",
        scheme="MitID",
        trust_framework="Digitaliseringsstyrelsen",
        supported_formats=["sd-jwt"],
        loa_mapping={"low": "low", "substantial": "substantial", "high": "high"},
        reference_url="https://www.mitid.dk/",
        id_hash_algorithm="SHA-256 over CPR",
    ),
    CountryConfig(
        code="IE",
        name="Ireland (MyGovID)",
        flag="🇮🇪",
        scheme="MyGovID",
        trust_framework="Department of Social Protection",
        supported_formats=["sd-jwt"],
        loa_mapping={"basic": "low", "verified": "substantial", "assured": "high"},
        reference_url="https://www.mygovid.ie/",
        id_hash_algorithm="SHA-256 over PPSN",
    ),
    CountryConfig(
        code="BR",
        name="Brazil (gov.br)",
        flag="🇧🇷",
        scheme="gov.br",
        trust_framework="ITI / ICP-Brasil",
        supported_formats=["sd-jwt", "mdoc"],
        loa_mapping={"bronze": "low", "prata": "substantial", "ouro": "high"},
        reference_url="https://acesso.gov.br/",
        id_hash_algorithm="SHA-256 over CPF",
    ),
    CountryConfig(
        code="US",
        name="United States (mDL)",
        flag="🇺🇸",
        scheme="AAMVA mDL",
        trust_framework="ISO 18013-5 / AAMVA",
        supported_formats=["mdoc"],
        loa_mapping={"low": "low", "moderate": "substantial", "high": "high"},
        reference_url="https://www.aamva.org/",
        id_hash_algorithm="SHA-256 over DL Number",
    ),
]


def build_registry() -> dict[str, CountryAdapter]:
    reg: dict[str, CountryAdapter] = {
        "EU": EUARFAdapter(),
        "FR": FranceConnectAdapter(),
        "IT": SpidCieAdapter(),
        "CH": SwiyuAdapter(),
    }
    for cfg in STUB_COUNTRIES:
        reg[cfg.code] = _StubAdapter(cfg)
    return reg


REGISTRY: dict[str, CountryAdapter] = build_registry()
