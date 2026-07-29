"""EUDI-Nexus FastAPI entry point.

Boots MongoDB indexes, generates persistent CA, seeds Concept Paper chapters,
and mounts all /api/* routers.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# imports AFTER load_dotenv so MASTER_KEY is available
from database import bootstrap_indexes, close_client, get_db  # noqa: E402
from routers import (  # noqa: E402
    compliance,
    country,
    hub,
    issuer,
    jmap,
    mdoc,
    paper,
    trust,
    verifier,
    well_known,
)
from services.ca_generator import CAGenerator  # noqa: E402
from services.seed_paper import seed_chapters  # noqa: E402
from services.signer_singleton import SignerSingleton  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("eudi-nexus")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bootstrap_indexes()
    await CAGenerator.bootstrap()
    await SignerSingleton.instance()
    seeded = await seed_chapters()
    if seeded:
        logger.info("seeded %d chapters into concept paper", seeded)
    logger.info("EUDI-Nexus is up ✓ (issuer_url=%s)", os.environ.get("ISSUER_URL"))
    yield
    await close_client()


app = FastAPI(
    title="EUDI-Nexus",
    version="1.0.0",
    description=(
        "EU Digital Identity infrastructure platform — eIDAS 2.0 / EUDI Wallet reference "
        "implementation with SD-JWT VC + ISO 18013-5 mDoc, Multi-Country federation, and "
        "Compliance Cockpit."
    ),
    lifespan=lifespan,
)


api_router = APIRouter(prefix="/api")
api_router.include_router(paper.router)
api_router.include_router(issuer.router)
api_router.include_router(verifier.router)
api_router.include_router(trust.router)
api_router.include_router(compliance.router)
api_router.include_router(mdoc.router)
api_router.include_router(jmap.router)
api_router.include_router(country.router)
api_router.include_router(hub.router)
api_router.include_router(well_known.router, prefix="/.well-known")


@api_router.get("/")
async def root() -> dict:
    return {
        "service": "EUDI-Nexus",
        "version": "1.0.0",
        "spec": "eIDAS 2.0 / ARF v1.4",
        "endpoints": [
            "/api/paper/chapters",
            "/api/issuer/nonce",
            "/api/issuer/credential",
            "/api/verifier/verify",
            "/api/mdoc/issue",
            "/api/mdoc/verify",
            "/api/trust/ca/chain",
            "/api/compliance/metrics",
            "/api/country/list",
            "/api/hub/repos",
            "/api/.well-known/openid-credential-issuer",
        ],
    }


@api_router.get("/health")
async def health() -> dict:
    try:
        await get_db().command("ping")
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "operational" if db_ok else "degraded", "database": db_ok}


app.include_router(api_router)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
