"""Developer hub — OSS repo registry (static + live GitHub badges optional)."""
from __future__ import annotations

from fastapi import APIRouter

from models import OSSRepo

router = APIRouter(prefix="/hub", tags=["Developer Hub"])


REGISTRY: list[OSSRepo] = [
    OSSRepo(
        slug="eu-digital-identity-wallet/architecture-and-reference-framework",
        url="https://github.com/eu-digital-identity-wallet/architecture-and-reference-framework",
        category="ARF",
        description="EUDI Architecture & Reference Framework v1.4",
        role="reference",
    ),
    OSSRepo(
        slug="eu-digital-identity-wallet/eudi-lib-jvm-sdjwt-kt",
        url="https://github.com/eu-digital-identity-wallet/eudi-lib-jvm-sdjwt-kt",
        category="SD-JWT VC",
        description="Kotlin SD-JWT VC library (issuer + verifier)",
        role="library",
    ),
    OSSRepo(
        slug="openwallet-foundation-labs/sd-jwt-python",
        url="https://github.com/openwallet-foundation-labs/sd-jwt-python",
        category="SD-JWT VC",
        description="Reference SD-JWT Python implementation",
        role="library",
    ),
    OSSRepo(
        slug="stalwart-labs/stalwart",
        url="https://github.com/stalwart-labs/stalwart",
        category="JMAP",
        description="Stalwart JMAP + IMAP + SMTP server (Rust)",
        role="mail-server",
    ),
    OSSRepo(
        slug="italia/spid-sp-access-button",
        url="https://github.com/italia/spid-sp-access-button",
        category="SPID/CIE",
        description="AGID SPID SP access button (official assets)",
        role="reference",
    ),
    OSSRepo(
        slug="e-id-admin/eidch-integration-guides",
        url="https://github.com/e-id-admin/eidch-integration-guides",
        category="Swiyu",
        description="Swiss E-ID (Swiyu) integration guides",
        role="library",
    ),
    OSSRepo(
        slug="decentralized-identity/didcomm-messaging",
        url="https://github.com/decentralized-identity/didcomm-messaging",
        category="DIDComm",
        description="DIF DIDComm v2 protocol",
        role="protocol",
    ),
    OSSRepo(
        slug="oauth-wg/oauth-status-list",
        url="https://github.com/oauth-wg/oauth-status-list",
        category="Status List",
        description="IETF OAuth Working Group — Token Status List draft",
        role="spec",
    ),
    OSSRepo(
        slug="oauth-wg/draft-ietf-oauth-sd-jwt-vc",
        url="https://github.com/oauth-wg/draft-ietf-oauth-sd-jwt-vc",
        category="SD-JWT VC",
        description="IETF OAuth WG — SD-JWT VC draft",
        role="spec",
    ),
    OSSRepo(
        slug="eu-digital-identity-wallet/eudi-app-android-wallet-ui",
        url="https://github.com/eu-digital-identity-wallet/eudi-app-android-wallet-ui",
        category="Wallet",
        description="EUDI Reference Wallet UI (Android)",
        role="app",
    ),
]


@router.get("/repos", response_model=list[OSSRepo])
async def list_repos() -> list[OSSRepo]:
    return REGISTRY
