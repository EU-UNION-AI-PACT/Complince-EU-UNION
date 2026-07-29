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
        slug="openwallet-foundation/sd-jwt-python",
        url="https://github.com/openwallet-foundation/sd-jwt-python",
        category="SD-JWT VC",
        description="Reference SD-JWT Python implementation",
        role="library",
    ),
    OSSRepo(
        slug="stalwart-labs/mail-server",
        url="https://github.com/stalwart-labs/mail-server",
        category="JMAP",
        description="Stalwart JMAP + IMAP + SMTP server (Rust)",
        role="mail-server",
    ),
    OSSRepo(
        slug="italia/spid-graphics",
        url="https://github.com/italia/spid-graphics",
        category="SPID/CIE",
        description="AGID SPID assets & docs",
        role="reference",
    ),
    OSSRepo(
        slug="e-id-admin/eidch-onboarding-integration",
        url="https://github.com/e-id-admin/eidch-onboarding-integration",
        category="Swiyu",
        description="Swiss E-ID onboarding integration (SDK)",
        role="library",
    ),
    OSSRepo(
        slug="dif/didcomm-messaging",
        url="https://github.com/decentralized-identity/didcomm-messaging",
        category="DIDComm",
        description="DIF DIDComm v2 protocol",
        role="protocol",
    ),
    OSSRepo(
        slug="oauth-wg/draft-ietf-oauth-status-list",
        url="https://github.com/oauth-wg/draft-ietf-oauth-status-list",
        category="Status List",
        description="IETF Token Status List draft",
        role="spec",
    ),
    OSSRepo(
        slug="oauth-wg/draft-ietf-oauth-sd-jwt-vc",
        url="https://github.com/oauth-wg/draft-ietf-oauth-sd-jwt-vc",
        category="SD-JWT VC",
        description="IETF SD-JWT VC draft",
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
