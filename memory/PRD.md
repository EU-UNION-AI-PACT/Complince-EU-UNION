# EUDI-Nexus — Product Requirements Document

## Original Problem Statement
Web-App (React + FastAPI + MongoDB) — eIDAS 2.0 / EUDI-Wallet Referenz-Infrastruktur mit Concept Paper Portal + Reference Sandbox + Compliance Cockpit. SD-JWT VC + ISO 18013-5 mDoc. No-Mocks-Policy strikt. Cyberpunk-Institutional Design.

## Iteration History

### Iteration 1 — Sprint 1-5 MVP (Foundation + SD-JWT + mDoc)
- All crypto services: SD-JWT builder/verifier, mDoc issuer/verifier, persistent 3-level CA, LOTL parser, X.509 chain validator, hash-chained audit log
- 5 concept paper chapters, live sandbox, compliance cockpit, trust pipeline, federation, developer hub
- 4 real country adapters (EU/FR/IT/CH), 7 stubs
- **34/34 backend tests passing**

### Iteration 2 — Sprint 7-9 + Emergent Google Auth
- **Sprint 7**: All 7 stub adapters (PT/SE/NO/DK/IE/BR/US) upgraded to real signature verification with DSGVO-hashing of national IDs (Personnummer, Fødselsnummer, CPR, PPSN, CPF, DL#). All 11 adapters now `implemented=true`.
- **Sprint 8**: LoA-Downgrade-Detection service (`services/oversight.py`) — hooks into every successful verification, maintains per-subject-fingerprint LoA history in Mongo, emits `loa.downgrade` audit events on regression. Human-oversight override endpoint (`POST /api/compliance/oversight/override`) with `accept`/`reject`/`escalate` decisions, audit-logged. Frontend `<DowngradePanel />` in the Compliance page.
- **Sprint 9**: `GET /api/hub/repos/live` — GitHub public-API sync with 1h LRU cache (stars/forks/last_commit/reachability). `GET /api/hub/postman-collection` — on-the-fly OpenAPI → Postman v2.1 conversion. `<DeveloperHub />` shows LIVE badges + a Postman-download button.
- **Emergent Google Auth**: `POST /api/issuer/credential` and `POST /api/compliance/gdpr/erasure` protected via `Depends(require_user)`. Bearer-token flow (Kubernetes ingress overrides CORS wildcards, so we use localStorage + Authorization header instead of cookies). `/api/auth/session` returns `session_token` in JSON body for client-side storage.
- **49/49 backend tests passing** — no critical bugs.
- Code review fixes applied: (1) `/api/auth/logout` now honors Bearer, (2) `create_session` upserts by `session_token`, (3) `OverrideRequest.decision` uses `Literal[...]` → 422 for invalid values (not 500), (4) `subject_fingerprint` uses NFC + casefold() for deterministic locale-independent hashing.

### Iteration 3 — Admin Portal (`/admin`)
- **Role-based access**: `role` field on `users` collection. `require_admin` dependency. Nav-item "Admin" only visible to admin role.
- **Idempotent seeding**: `services/admin_seed.py` reads `ADMIN_EMAILS` env var (comma-separated). Bootstrap: first user to sign in becomes admin if no admins configured and no other users exist.
- **`GET /api/admin/overview`**: aggregate snapshot — adapters, CA docs, audit chain integrity, credential count, downgrade counts, user counts.
- **`GET /api/admin/users`**: user + role listing.
- **Frontend `/admin`** with 4 tabs:
  1. **Overview** — 6 real-time stat cards + user table with role badges
  2. **AI Act Art. 14 Oversight** — reuses `<DowngradePanel />`
  3. **GDPR Art. 17** — real erasure form (Bearer-gated, confirm-before-execute) + tamper-evident history of past erasure events
  4. **GitHub Live-Sync** — 10 repos, per-repo status (LIVE / http-error), aggregate stars, cache-refresh button
- **Every cell** is bound to a real backend endpoint. No hardcoded emails. No fake events. No client-side auth bypass. Complies with the No-Mocks-Policy.

## Architecture Locks
- ES256 primary; ES384/ES512 for LoA-High; EdDSA optional for W3C VC-DM 2.0
- SD-JWT VC (RFC 9215) + ISO 18013-5 mDoc parallel
- CBOR Tag 18 (COSE_Sign1) + 24 (bstr.cbor) + 0 (tdate) — strict
- AES-256-GCM Envelope Key Storage — fail-fast on missing `MASTER_KEY`
- Persistent 3-Level CA (Root → Intermediate → Signer) — never regenerated
- c_nonce TTL 300s + `find_one_and_delete` One-Time-Use
- Status List with signature + LRU 5min cache
- Audit log: SHA-256 prev_hash + JWS `typ=audit+jwt` signature per entry

## Backlog (P0 / P1 / P2)

### P0 (production hardening — recommended before real-world use)
- [ ] Populate `ADMIN_EMAILS` in production `.env` (or leverage first-user bootstrap)
- [ ] Rate-limit `/api/issuer/credential` and `/api/compliance/gdpr/erasure`
- [ ] Also protect `/api/issuer/nonce` with `Depends(require_user)` (currently public — flagged in iteration-2 review as nonce-pool-exhaustion vector)
- [ ] `AamvaMdlAdapter` currently trusts platform-local CA for cross-border mDL — document as reference-only or wire real AAMVA trust anchors
- [ ] Sprint 6 (JMAP + Wallet-Auth) on-prem Stalwart deployment testing

### P1 (nice-to-have next)
- [ ] `?download=1` variant of `/api/hub/postman-collection` with `Content-Disposition: attachment`
- [ ] Optional GITHUB_TOKEN env for higher API rate limits (60 → 5000 req/h)
- [ ] Volltextsuche im Concept Paper mit Query-Highlighting
- [ ] QR-Code Renderer für Credential-Offer URIs (`openid-credential-offer://…`)
- [ ] W3C VC-DM 2.0 mit URDNA2015 canonicalization für Swiyu

### P2
- [ ] Playwright E2E test suite (frontend)
- [ ] GitHub Actions CI/CD `.github/workflows/eudi_compliance_gates.yml`
- [ ] Kubernetes Helm-Chart
- [ ] Frontend admin: user role management (promote/demote via UI)

## Test Reports
- `/app/test_reports/iteration_1.json` — Sprint 1-5 MVP (34/34)
- `/app/test_reports/iteration_2.json` — Sprint 7-9 + Auth (49/49)

## Env Vars (`/app/backend/.env`)
- `MONGO_URL` — MongoDB connection
- `DB_NAME` — Mongo database name
- `MASTER_KEY` — 32-byte base64 AES-256 key (fail-fast if missing)
- `ISSUER_URL` — public backend URL (used as `aud` in proof JWTs)
- `ISSUER_ID` — DID / issuer identifier
- `CORS_ORIGINS` — comma-separated (default `*` — production should whitelist)
- `ADMIN_EMAILS` — comma-separated emails to promote to admin on login (empty → first-user bootstrap)
- `STALWART_BASE_URL` — reference-only, on-prem Stalwart JMAP sidecar
