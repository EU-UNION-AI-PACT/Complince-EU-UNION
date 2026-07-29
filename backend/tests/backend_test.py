"""
EUDI-Nexus backend regression tests.

Covers Sprint 1-5 endpoints: paper, issuer (SD-JWT VC + one-time nonce),
verifier, mDoc (ISO 18013-5), trust, compliance, country adapters,
well-known discovery.

Env:
  BASE_URL     — from REACT_APP_BACKEND_URL (HTTP entry point)
  ISSUER_URL   — from backend/.env (aud in proof-JWT)
"""
from __future__ import annotations

import base64
import json
import os
import time
from typing import Any

import pytest
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://mdoc-issuer.preview.emergentagent.com").rstrip("/")
# ISSUER_URL matches the value in backend/.env (used as `aud` for proof JWTs)
ISSUER_URL = os.environ.get("ISSUER_URL", "https://fa61e2da-c1aa-4cff-90fc-a761ac9856ca.preview.emergentagent.com")

API = f"{BASE_URL}/api"


# ---------------------------------------------------------------------------
# Helpers — ES256 proof-JWT signing (cryptography)
# ---------------------------------------------------------------------------
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64u_json(obj: dict) -> str:
    return _b64u(json.dumps(obj, separators=(",", ":")).encode())


def _make_es256_key() -> tuple[ec.EllipticCurvePrivateKey, dict]:
    sk = ec.generate_private_key(ec.SECP256R1())
    nums = sk.public_key().public_numbers()
    x = nums.x.to_bytes(32, "big")
    y = nums.y.to_bytes(32, "big")
    jwk = {"kty": "EC", "crv": "P-256", "x": _b64u(x), "y": _b64u(y)}
    return sk, jwk


def _sign_proof_jwt(sk: ec.EllipticCurvePrivateKey, jwk: dict, nonce: str, aud: str) -> str:
    header = {"typ": "openid4vci-proof+jwt", "alg": "ES256", "jwk": jwk}
    payload = {"aud": aud, "iat": int(time.time()), "nonce": nonce}
    signing_input = f"{_b64u_json(header)}.{_b64u_json(payload)}".encode()
    der_sig = sk.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_sig)
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return f"{signing_input.decode()}.{_b64u(raw)}"


# ---------------------------------------------------------------------------
# Session fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def s() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class TestHealth:
    def test_health(self, s):
        r = s.get(f"{API}/health", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"
        assert data["database"] is True


# ---------------------------------------------------------------------------
# Concept Paper
# ---------------------------------------------------------------------------
class TestPaper:
    def test_chapters(self, s):
        r = s.get(f"{API}/paper/chapters", timeout=15)
        assert r.status_code == 200
        chapters = r.json()
        assert isinstance(chapters, list)
        assert len(chapters) >= 5, f"expected >=5 chapters, got {len(chapters)}"
        slugs = {c["slug"] for c in chapters}
        # Slug spelling: architektur (DE)
        assert any("architek" in sl.lower() for sl in slugs)

    def test_chapter_architektur(self, s):
        # Try both possible slugs
        for slug in ("architektur", "architecture"):
            r = s.get(f"{API}/paper/chapters/{slug}", timeout=15)
            if r.status_code == 200:
                body = r.json()
                assert body.get("body")
                return
        pytest.fail("architektur chapter not found under expected slugs")

    def test_search(self, s):
        r = s.get(f"{API}/paper/search", params={"q": "eIDAS"}, timeout=15)
        assert r.status_code == 200
        results = r.json()
        assert isinstance(results, list)
        assert len(results) >= 1, "search for 'eIDAS' returned no results"


# ---------------------------------------------------------------------------
# Issuer — nonce + credential + one-time-use
# ---------------------------------------------------------------------------
class TestIssuer:
    def test_nonce_fresh(self, s):
        r1 = s.post(f"{API}/issuer/nonce", json={}, timeout=15)
        r2 = s.post(f"{API}/issuer/nonce", json={}, timeout=15)
        assert r1.status_code == 200 and r2.status_code == 200
        d1, d2 = r1.json(), r2.json()
        assert d1["c_nonce_expires_in"] == 300
        assert d1["c_nonce"] != d2["c_nonce"]

    def test_credential_unknown_nonce_rejected(self, s):
        sk, jwk = _make_es256_key()
        proof = _sign_proof_jwt(sk, jwk, nonce="bogus-nonce-not-in-db", aud=ISSUER_URL)
        payload = {
            "vct": "eu.europa.ec.eudi.pid.1",
            "subject_claims": {"family_name": "Mustermann", "given_name": "Erika",
                               "birth_date": "1980-01-01", "email": "e@x.eu"},
            "holder_jwk": jwk,
            "proof_jwt": proof,
            "country_code": "EU",
        }
        r = s.post(f"{API}/issuer/credential", json=payload, timeout=20)
        assert r.status_code == 400
        detail = r.json().get("detail", {})
        reasons = detail.get("reasons") if isinstance(detail, dict) else []
        assert any("nonce" in str(x).lower() for x in reasons or []), f"expected nonce reason: {r.text}"

    def test_e2e_issue_and_verify(self, s):
        # 1) nonce
        n = s.post(f"{API}/issuer/nonce", json={}, timeout=15).json()["c_nonce"]

        # 2) proof jwt
        sk, jwk = _make_es256_key()
        proof = _sign_proof_jwt(sk, jwk, nonce=n, aud=ISSUER_URL)

        # 3) issue credential
        req = {
            "vct": "eu.europa.ec.eudi.pid.1",
            "subject_claims": {
                "family_name": "Mustermann",
                "given_name": "Erika",
                "birth_date": "1980-01-01",
                "email": "erika@example.eu",
            },
            "holder_jwk": jwk,
            "proof_jwt": proof,
            "country_code": "EU",
        }
        r = s.post(f"{API}/issuer/credential", json=req, timeout=25)
        assert r.status_code == 200, f"issue failed: {r.status_code} {r.text}"
        cred = r.json()
        assert cred["disclosures_count"] >= 4
        assert cred["credential"].count("~") >= 4  # 4 disclosures -> tilde delim

        # 4) verify (no audience/nonce -> no KB-JWT required, per review contract)
        pres = cred["credential"]
        vr = s.post(f"{API}/verifier/verify",
                    json={"presentation": pres},
                    timeout=20)
        assert vr.status_code == 200
        vres = vr.json()
        assert vres["valid"] is True, f"verify failed: {vres}"
        disclosed = vres["disclosed_claims"]
        for k in ("family_name", "given_name", "birth_date", "email"):
            assert k in disclosed, f"missing disclosed {k}: {disclosed}"

        # stash for downstream
        pytest.issued_credential = pres

    def test_nonce_one_time_use(self, s):
        # Get a nonce, use it once, try again with same nonce
        n = s.post(f"{API}/issuer/nonce", json={}).json()["c_nonce"]
        sk, jwk = _make_es256_key()
        proof = _sign_proof_jwt(sk, jwk, nonce=n, aud=ISSUER_URL)

        req = {
            "vct": "eu.europa.ec.eudi.pid.1",
            "subject_claims": {"family_name": "A", "given_name": "B",
                               "birth_date": "2000-01-01", "email": "a@b.c"},
            "holder_jwk": jwk,
            "proof_jwt": proof,
            "country_code": "EU",
        }
        r1 = s.post(f"{API}/issuer/credential", json=req, timeout=20)
        assert r1.status_code == 200

        # Reuse same nonce+proof
        r2 = s.post(f"{API}/issuer/credential", json=req, timeout=20)
        assert r2.status_code == 400
        detail = r2.json().get("detail", {})
        reasons = detail.get("reasons", []) if isinstance(detail, dict) else []
        assert any("nonce" in str(x).lower() for x in reasons), f"expected nonce replay reject: {r2.text}"


# ---------------------------------------------------------------------------
# Verifier — mangled presentation
# ---------------------------------------------------------------------------
class TestVerifier:
    def test_mangled_presentation(self, s):
        r = s.post(f"{API}/verifier/verify",
                   json={"presentation": "not.a.jwt~junk~", "audience": ISSUER_URL},
                   timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert len(data["reasons"]) >= 1

    def test_truncated_presentation(self, s):
        r = s.post(f"{API}/verifier/verify",
                   json={"presentation": "abc", "audience": ISSUER_URL},
                   timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False


# ---------------------------------------------------------------------------
# Trust — CA chain persistence + LOTL parse
# ---------------------------------------------------------------------------
class TestTrust:
    def test_ca_chain(self, s):
        r = s.get(f"{API}/trust/ca/chain", timeout=15)
        assert r.status_code == 200
        chain = r.json()
        assert len(chain) == 3
        for cert in chain:
            for f in ("fingerprint_sha256", "subject", "issuer", "pem"):
                assert f in cert, f"missing {f} in {cert}"

    def test_ca_chain_persistent(self, s):
        c1 = s.get(f"{API}/trust/ca/chain").json()
        c2 = s.get(f"{API}/trust/ca/chain").json()
        fp1 = [c["fingerprint_sha256"] for c in c1]
        fp2 = [c["fingerprint_sha256"] for c in c2]
        assert fp1 == fp2, "CA fingerprints changed between calls (not persistent!)"

    def test_lotl_parse(self, s):
        minimal_xml = """<?xml version="1.0" encoding="UTF-8"?>
<TrustServiceStatusList xmlns="http://uri.etsi.org/02231/v2#">
  <SchemeInformation>
    <SchemeTerritory>EU</SchemeTerritory>
    <SchemeOperatorName>
      <Name xml:lang="en">EC</Name>
    </SchemeOperatorName>
    <TSLSequenceNumber>42</TSLSequenceNumber>
    <ListIssueDateTime>2025-01-01T00:00:00Z</ListIssueDateTime>
    <NextUpdate><dateTime>2025-06-01T00:00:00Z</dateTime></NextUpdate>
  </SchemeInformation>
</TrustServiceStatusList>"""
        r = s.post(f"{API}/trust/lotl/parse", json={"xml": minimal_xml}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["anchor_count"] >= 0
        assert data["territory"] == "EU"
        assert data["sequence_number"] == 42
        assert data["scheme_operator"]


# ---------------------------------------------------------------------------
# mDoc (ISO 18013-5)
# ---------------------------------------------------------------------------
class TestMDoc:
    device_jwk = {"kty": "EC", "crv": "P-256", "x": _b64u(b"\x01" * 32), "y": _b64u(b"\x02" * 32)}

    def test_issue_verify_e2e(self, s):
        sk, jwk = _make_es256_key()
        payload = {
            "doctype": "org.iso.18013.5.1.mDL",
            "namespaces": {
                "org.iso.18013.5.1": {
                    "family_name": "Doe",
                    "given_name": "Jane",
                    "birth_date": "1990-05-15",
                    "issuing_country": "DE",
                }
            },
            "device_public_key": jwk,
            "country_code": "EU",
        }
        r = s.post(f"{API}/mdoc/issue", json=payload, timeout=20)
        assert r.status_code == 200, r.text
        issued = r.json()
        assert issued["digest_count"] == 4
        assert issued["doctype"] == "org.iso.18013.5.1.mDL"
        mdoc_hex = issued["mdoc_hex"]
        assert len(mdoc_hex) > 0 and all(c in "0123456789abcdefABCDEF" for c in mdoc_hex)

        # Verify CBOR structure has tags 18, 24, 0 by byte-scanning the raw CBOR.
        # CBOR tags: 0 -> 0xc0, 18 -> 0xd2, 24 -> 0xd8 0x18 (see RFC 8949).
        raw = bytes.fromhex(mdoc_hex)
        assert b"\xd2" in raw, "CBOR Tag 18 (COSE_Sign1) not present in mDoc bytes"
        assert b"\xd8\x18" in raw, "CBOR Tag 24 (bstr.cbor) not present in mDoc bytes"
        assert b"\xc0" in raw, "CBOR Tag 0 (tdate) not present in mDoc bytes"
        import cbor2  # ensure lib available for parsers
        _ = cbor2.loads(raw)  # sanity: full decode succeeds

        # Verify mDoc
        vr = s.post(f"{API}/mdoc/verify", json={"mdoc_hex": mdoc_hex}, timeout=20)
        assert vr.status_code == 200, vr.text
        vres = vr.json()
        assert vres["valid"] is True, vres
        assert vres["doctype"] == "org.iso.18013.5.1.mDL"
        assert vres["device_key_present"] is True
        assert "org.iso.18013.5.1" in vres["disclosed_namespaces"]

    def test_verify_random_bytes(self, s):
        r = s.post(f"{API}/mdoc/verify", json={"mdoc_hex": "deadbeefcafe1234"}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["valid"] is False
        assert len(data["reasons"]) >= 1

    def test_verify_bad_hex(self, s):
        r = s.post(f"{API}/mdoc/verify", json={"mdoc_hex": "not-hex!!"}, timeout=15)
        assert r.status_code == 400

    def test_engagement(self, s):
        r = s.post(f"{API}/mdoc/engagement", json={}, timeout=15)
        assert r.status_code == 200
        eng = r.json()
        assert "engagement_id" in eng and "device_engagement_hex" in eng
        eid = eng["engagement_id"]

        r2 = s.get(f"{API}/mdoc/engagement/{eid}", timeout=15)
        assert r2.status_code == 200
        eng2 = r2.json()
        assert eng2["engagement_id"] == eid
        assert eng2["device_engagement_hex"] == eng["device_engagement_hex"]

    def test_engagement_not_found(self, s):
        r = s.get(f"{API}/mdoc/engagement/does-not-exist-xxx", timeout=15)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------------
class TestCompliance:
    def test_metrics(self, s):
        r = s.get(f"{API}/compliance/metrics", timeout=15)
        assert r.status_code == 200
        m = r.json()
        for f in ("total_credentials_issued", "total_presentations_verified",
                  "verification_success_rate", "active_loa_high",
                  "active_loa_substantial", "active_loa_low",
                  "downgrade_incidents", "ai_act_transparency_events",
                  "gdpr_erasure_requests"):
            assert f in m, f"missing metric {f}"
            assert isinstance(m[f], (int, float))

    def test_audit_log_hash_chain(self, s):
        r = s.get(f"{API}/compliance/audit-log", timeout=15)
        assert r.status_code == 200
        events = r.json()
        assert isinstance(events, list) and len(events) >= 1
        for ev in events[:5]:
            for f in ("prev_hash", "hash", "signature"):
                assert f in ev, f"missing {f} in audit event"

    def test_audit_verify(self, s):
        r = s.get(f"{API}/compliance/audit-log/verify", timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert d.get("valid") is True
        assert d.get("checked", 0) > 0

    def test_ai_act_transparency(self, s):
        r = s.get(f"{API}/compliance/ai-act/transparency", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert isinstance(d.get("regulation"), str)
        assert "system_role" in d
        assert "human_oversight_hook" in d
        assert isinstance(d.get("events"), list)

    def test_dsa_pdf(self, s):
        r = s.get(f"{API}/compliance/dsa/report.pdf", timeout=30)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert len(r.content) > 500
        assert r.content[:4] == b"%PDF"

    def test_gdpr_erasure_missing_subject(self, s):
        r = s.post(f"{API}/compliance/gdpr/erasure",
                   json={"subject_hash": "TEST_ghost_hash_zzz", "reason": "GDPR Art. 17"},
                   timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["deleted"] == 0


# ---------------------------------------------------------------------------
# Country adapters
# ---------------------------------------------------------------------------
class TestCountry:
    def test_list_countries(self, s):
        r = s.get(f"{API}/country/list", timeout=15)
        assert r.status_code == 200
        cs = r.json()
        assert len(cs) == 11, f"expected 11 countries, got {len(cs)}"
        by_code = {c["code"]: c for c in cs}
        for code in ("EU", "FR", "IT", "CH"):
            assert by_code[code]["implemented"] is True, f"{code} should be implemented"
        for code in ("PT", "SE", "NO", "DK", "IE", "BR", "US"):
            assert by_code[code]["implemented"] is False, f"{code} should be stub"

    def test_get_country_eu(self, s):
        r = s.get(f"{API}/country/EU", timeout=15)
        assert r.status_code == 200
        assert r.json()["code"] == "EU"

    def test_get_country_unknown(self, s):
        r = s.get(f"{API}/country/XX", timeout=15)
        assert r.status_code == 404

    def test_verify_stub_country_pt(self, s):
        r = s.post(f"{API}/country/verify",
                   json={"country_code": "PT", "presentation": "abc~", "format": "sd-jwt"},
                   timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["valid"] is False
        assert any("not yet wired" in x for x in d["reasons"])

    def test_verify_unknown_country(self, s):
        r = s.post(f"{API}/country/verify",
                   json={"country_code": "ZZ", "presentation": "x", "format": "sd-jwt"},
                   timeout=15)
        assert r.status_code == 404

    def test_verify_eu_with_valid_credential(self, s):
        # Issue a fresh credential then verify via EU adapter
        n = s.post(f"{API}/issuer/nonce", json={}).json()["c_nonce"]
        sk, jwk = _make_es256_key()
        proof = _sign_proof_jwt(sk, jwk, nonce=n, aud=ISSUER_URL)
        req = {
            "vct": "eu.europa.ec.eudi.pid.1",
            "subject_claims": {"family_name": "X", "given_name": "Y",
                               "birth_date": "2000-01-01", "email": "y@x.eu"},
            "holder_jwk": jwk,
            "proof_jwt": proof,
            "country_code": "EU",
        }
        cred = s.post(f"{API}/issuer/credential", json=req, timeout=20).json()["credential"]

        r = s.post(f"{API}/country/verify",
                   json={"country_code": "EU", "presentation": cred, "format": "sd-jwt"},
                   timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["valid"] is True, f"EU adapter verify failed: {d}"


# ---------------------------------------------------------------------------
# Hub + Well-known
# ---------------------------------------------------------------------------
class TestHub:
    def test_repos(self, s):
        r = s.get(f"{API}/hub/repos", timeout=15)
        assert r.status_code == 200
        repos = r.json()
        assert len(repos) >= 10
        for rp in repos:
            for f in ("slug", "url", "category", "description", "role"):
                assert f in rp


class TestWellKnown:
    def test_openid_issuer_metadata(self, s):
        r = s.get(f"{API}/.well-known/openid-credential-issuer", timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["credential_issuer"]
        assert d["credential_endpoint"].endswith("/api/issuer/credential")
        assert d["nonce_endpoint"].endswith("/api/issuer/nonce")
        configs = d["credential_configurations_supported"]
        for k in ("eu.europa.ec.eudi.pid.1", "eu.europa.ec.eudi.mdl.1", "eu.europa.ec.eudi.email.1"):
            assert k in configs
        keys = d["jwks"]["keys"]
        assert len(keys) >= 1
        assert keys[0]["kty"] == "EC"
        assert keys[0]["crv"] == "P-256"

    def test_jwks(self, s):
        r = s.get(f"{API}/.well-known/jwks.json", timeout=15)
        assert r.status_code == 200
        keys = r.json()["keys"]
        assert len(keys) >= 1
        assert keys[0]["kty"] == "EC"

    def test_jwks_matches_issuer(self, s):
        j1 = s.get(f"{API}/.well-known/openid-credential-issuer").json()["jwks"]["keys"][0]
        j2 = s.get(f"{API}/.well-known/jwks.json").json()["keys"][0]
        assert j1.get("x") == j2.get("x")
        assert j1.get("y") == j2.get("y")
