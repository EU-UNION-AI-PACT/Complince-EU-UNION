# EUDI-Nexus — Product Requirements Document

## Original Problem Statement

Web-App (React + TypeScript + FastAPI + MongoDB) — Vollständige eIDAS 2.0 / EUDI-Wallet Referenz-Infrastruktur-Plattform mit Concept Paper Portal + Reference Implementation Sandbox + Compliance Cockpit. Cyberpunk-Institutional Design. No-Mocks-Policy strikt.

Sprint-Roadmap 1-9 mit Architektur-Locks: SD-JWT VC + ISO 18013-5 mDoc, ES256/384/EdDSA, `cnf.jwk` Pflicht + KB-JWT bei Presentations, AES-256-GCM Envelope-Storage, persistente 3-Level-CA, CBOR Tag 18/24/0 strikt, c_nonce TTL 300s + One-Time-Use, Status-List mit LRU-Cache.

## User Personas

1. **eIDAS 2.0 Government Architects** — evaluieren Referenz-Architektur für nationale Wallet-Implementations
2. **EUDI-Wallet Developer** — brauchen funktionierende Beispiele für SD-JWT VC Issuance/Verification und ISO 18013-5 mDoc
3. **Compliance-Officer** — DSGVO, EU AI Act Art. 13/14, DSA-Reports auf Knopfdruck
4. **Solution Architects** in Mitgliedstaaten — Adapter-Interfaces für nationale Vertrauens-Frameworks

## Core Requirements (static)

- SD-JWT VC Issuer mit RFC 7515 R‖S JWS, `_sd`-Digests, KB-JWT, Status List
- ISO 18013-5 mDoc mit COSE_Sign1 (Tag 18), MSO Payload (Tag 24), RFC 3339 UTC (Tag 0)
- Persistente 3-Level Certificate Authority (Root → Intermediate → Signer), AES-256-GCM
- ETSI TS 119 612 LOTL Parser
- RFC 5280 X.509 Chain-Validator
- Multi-Country Adapter Protocol (CountryAdapter) mit DSGVO-konformem ID-Hashing
- Compliance-Cockpit mit SHA-256 hash-chained Audit-Log
- Concept Paper Portal (5 Kapitel MDX + Volltextsuche + Bookmarks)
- Reference Sandbox mit Live-Issue → Present → Verify Flow
- i18n DE/EN
- Cyberpunk-Institutional Design (Deep-Slate/Amber/Electric-Blue, Inter+IBM Plex Serif+JetBrains Mono)

## What's been implemented (2026-02-XX — Sprint 1-5 MVP)

### Backend (FastAPI + Motor/MongoDB)
- ✅ `KeyStorageManager` — AES-256-GCM Envelope-Encryption, Fail-Fast bei fehlendem MASTER_KEY
- ✅ `SignerSingleton` — Race-safe ES256 (P-256) Issuer Key (persistiert in Mongo)
- ✅ `IssuerSigner` — RFC 7515 R‖S JWS via `decode_dss_signature`
- ✅ `SDJWTBuilder` — Disclosures + `_sd` Hashing + `cnf.jwk` + Status-List-Pointer
- ✅ `SDJWTVerifierV2` — Signature + Time-Claims + Disclosure-Verify + KB-JWT + Status-List
- ✅ `ProofJWTValidator` — c_nonce mit TTL 300s, One-Time-Use via `find_one_and_delete`
- ✅ `StatusListClient` — 2-bit per credential, LRU 5min Cache, zlib+base64
- ✅ `CAGenerator` — Persistente 3-Level CA (P-256, X.509 v3 mit EKU 1.0.18013.5.1.2)
- ✅ `TrustValidator` — RFC 5280 X.509 Chain-Check
- ✅ `LotlParser` — ETSI TS 119 612 XML mit lxml, Namespaces korrekt
- ✅ `MDocIssuerSingleton` — CBOR Tag 18/24/0, COSE_Sign1, MSO mit valueDigests
- ✅ `MDocVerifier` — issuerAuth Signature + Chain + Digest-Match
- ✅ `MDocEngagement` — Ephemeral eDeviceKey (P-256)
- ✅ `AuditLog` — SHA-256 hash-chained + JWS signature per Entry
- ✅ `JmapAuthBridge` — Mock-Bridge für Emergent Cloud (Stalwart-Config unter `/app/stalwart/config/config.toml` dokumentiert)
- ✅ 11 Country Adapter — 4 Real (EU/FR/IT/CH), 7 Stubs (PT/SE/NO/DK/IE/BR/US)
- ✅ Compliance-Cockpit: `/metrics`, `/audit-log`, `/audit-log/verify`, `/ai-act/transparency`, `/dsa/report.pdf`, `/gdpr/erasure`
- ✅ `.well-known/openid-credential-issuer` + `/jwks.json`
- ✅ CI Scripts: `validate_spec_tags.py` (Gate 2) + `security_static_scan.py` (Gate 3)
- ✅ Concept Paper Seed — 5 Kapitel (Executive Summary, Architektur, JMAP, Multi-Country, Compliance)
- ✅ 34/34 pytest Backend-Tests grün

### Frontend (React + shadcn/ui + Tailwind)
- ✅ Landing Page — Hero mit 4 Cyberpunk-Institutional Bildern, 6-Säulen-Grid, Cross-Border CTA
- ✅ Concept Paper Portal — 5 Kapitel, Volltextsuche, Bookmarks in LocalStorage, IBM Plex Serif Body
- ✅ Reference Sandbox — 3 Tabs (SD-JWT, mDoc, Country), Live-Flow mit browser-native SubtleCrypto P-256, JSON-Viewer
- ✅ Compliance Cockpit — Bento-Grid mit Metriken, hash-chained Audit-Log Table, AI Act Panel, GDPR Erasure, DSA PDF Export
- ✅ Trust Pipeline — 3-Level CA-Chain Viewer mit expandierbaren PEM-Zertifikaten, LOTL-XML Parser
- ✅ Federation — Alle 11 Länder mit Adapter-Details, LoA-Mapping, GDPR-Hash-Info
- ✅ Developer Hub — 10 OSS-Repos gefiltert nach Kategorie
- ✅ i18n DE/EN via i18next mit Language-Toggle
- ✅ Mermaid Dark-Theme Renderer in Concept Paper
- ✅ react-markdown mit GFM + Mermaid Code-Block-Extraktion

### Design (Cyberpunk-Institutional)
- ✅ Deep-Slate `#090d16` Base + Amber `#f59e0b` + Electric-Blue `#3b82f6` + Emerald für Status-OK
- ✅ Fonts: Inter (UI) + IBM Plex Serif (Body/Headlines) + JetBrains Mono (Code/Hashes)
- ✅ SVG-Grain Overlay, Amber Glow für Critical Markers
- ✅ Trace-beam Hover-Effects, Custom Scrollbars
- ✅ Motion via framer-motion für Landing Reveals

## Prioritized Backlog / What Comes Next

### P0 (kritisch für Production)
- [ ] Auth-Layer (nur `/api/compliance/*` und `/api/issuer/*` schützen; z.B. Emergent Google Auth)
- [ ] Rate-Limiting auf `/api/compliance/gdpr/erasure` und `/api/issuer/credential`
- [ ] Sprint 6 (JMAP + Wallet-Auth) on-prem Stalwart-Deployment testen (aktuell nur Config dokumentiert)

### P1 (nach 1st Finish, wenn User bestätigt)
- [ ] Sprint 7: Restliche 7 Country-Adapter (PT/SE/NO/DK/IE/BR/US) mit realer Signature-Verification
- [ ] Sprint 8: `loa.downgrade`-Detection Live-Panel + Human-Overwrite-Endpoint (AI Act Art. 14)
- [ ] Sprint 9: OpenAPI-Docs vollständig + Postman Collection Export + GitHub Live-Sync für Repo-Registry
- [ ] Volltextsuche im Concept Paper: Highlighting der Query in den Resultaten
- [ ] QR-Code Rendering für Credential Offer (URI-Scheme `openid-credential-offer://`)
- [ ] W3C VC-DM 2.0 mit URDNA2015 Canonicalization für Swiyu (aktuell strukturelle JSON-Prüfung)

### P2 (nice-to-have)
- [ ] Frontend E2E-Tests via Playwright
- [ ] CI/CD Workflow `eudi_compliance_gates.yml` in GitHub Actions
- [ ] Postman Collection Export als `.json`
- [ ] Kubernetes Helm-Chart

## Test Reports
- `/app/test_reports/iteration_1.json` — 34/34 backend tests passing after 1 bug fix (mdoc engagement)

## Architecture Locks (nicht verhandeln)
- ES256 primär; ES384/ES512 für LoA-High; EdDSA nur für W3C VC-DM 2.0
- CBOR Tag 18 (COSE_Sign1) + 24 (bstr.cbor) + 0 (tdate)
- `.env` `MASTER_KEY` 32-byte base64 — Fail-Fast bei Fehlen
- Persistente 3-Level CA (Root → Intermediate → Signer)
- c_nonce TTL 300s + `find_one_and_delete` One-Time-Use
- Status-List mit Signature + LRU 5min
