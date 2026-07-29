"""Country adapter registry — 11 fully implemented adapters (all with LDP-VC where applicable)."""
from __future__ import annotations

from adapters.base import CountryAdapter, CountryConfig
from adapters.eu_arf import EUARFAdapter
from adapters.france_connect import FranceConnectAdapter
from adapters.real_impls import (
    AamvaMdlAdapter,
    BankIdSEAdapter,
    GovBrAdapter,
    IdPortenNOAdapter,
    MitIdDKAdapter,
    MyGovIdIEAdapter,
    PortugalAdapter,
)
from adapters.spid_cie import SpidCieAdapter
from adapters.swiyu import SwiyuAdapter

CONFIGS: list[CountryConfig] = [
    CountryConfig(
        code="PT",
        name="Portugal (Autenticação.gov)",
        flag="🇵🇹",
        scheme="Autenticação.gov",
        trust_framework="AMA / eIDAS",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"AL1": "low", "AL2": "substantial", "AL3": "high"},
        reference_url="https://www.autenticacao.gov.pt/",
        id_hash_algorithm="SHA-256 over NIC",
        implemented=True,
    ),
    CountryConfig(
        code="SE",
        name="Sweden (BankID)",
        flag="🇸🇪",
        scheme="BankID",
        trust_framework="Finansiell ID-Teknik / eIDAS",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"basic": "substantial", "advanced": "high"},
        reference_url="https://www.bankid.com/",
        id_hash_algorithm="SHA-256 over Personnummer (digits only)",
        implemented=True,
    ),
    CountryConfig(
        code="NO",
        name="Norway (ID-porten)",
        flag="🇳🇴",
        scheme="ID-porten",
        trust_framework="Digdir",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"idporten-loa-substantial": "substantial", "idporten-loa-high": "high"},
        reference_url="https://docs.digdir.no/",
        id_hash_algorithm="SHA-256 over Fødselsnummer (digits only)",
        implemented=True,
    ),
    CountryConfig(
        code="DK",
        name="Denmark (MitID)",
        flag="🇩🇰",
        scheme="MitID",
        trust_framework="Digitaliseringsstyrelsen",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"low": "low", "substantial": "substantial", "high": "high"},
        reference_url="https://www.mitid.dk/",
        id_hash_algorithm="SHA-256 over CPR (digits only)",
        implemented=True,
    ),
    CountryConfig(
        code="IE",
        name="Ireland (MyGovID)",
        flag="🇮🇪",
        scheme="MyGovID",
        trust_framework="Department of Social Protection",
        supported_formats=["sd-jwt", "ldp-vc"],
        loa_mapping={"basic": "low", "verified": "substantial", "assured": "high"},
        reference_url="https://www.mygovid.ie/",
        id_hash_algorithm="SHA-256 over PPSN",
        implemented=True,
    ),
    CountryConfig(
        code="BR",
        name="Brazil (gov.br)",
        flag="🇧🇷",
        scheme="gov.br",
        trust_framework="ITI / ICP-Brasil",
        supported_formats=["sd-jwt", "mdoc", "ldp-vc"],
        loa_mapping={"bronze": "low", "prata": "substantial", "ouro": "high"},
        reference_url="https://acesso.gov.br/",
        id_hash_algorithm="SHA-256 over CPF (digits only)",
        implemented=True,
    ),
    CountryConfig(
        code="US",
        name="United States (AAMVA mDL)",
        flag="🇺🇸",
        scheme="AAMVA mDL",
        trust_framework="ISO 18013-5 / AAMVA",
        supported_formats=["mdoc"],
        loa_mapping={"low": "low", "moderate": "substantial", "high": "high"},
        reference_url="https://www.aamva.org/",
        id_hash_algorithm="SHA-256 over DL number (upper)",
        implemented=True,
    ),
]


def build_registry() -> dict[str, CountryAdapter]:
    reg: dict[str, CountryAdapter] = {
        "EU": EUARFAdapter(),
        "FR": FranceConnectAdapter(),
        "IT": SpidCieAdapter(),
        "CH": SwiyuAdapter(),
    }
    ctor_map = {
        "PT": PortugalAdapter,
        "SE": BankIdSEAdapter,
        "NO": IdPortenNOAdapter,
        "DK": MitIdDKAdapter,
        "IE": MyGovIdIEAdapter,
        "BR": GovBrAdapter,
        "US": AamvaMdlAdapter,
    }
    for cfg in CONFIGS:
        reg[cfg.code] = ctor_map[cfg.code](cfg)
    return reg


REGISTRY: dict[str, CountryAdapter] = build_registry()
