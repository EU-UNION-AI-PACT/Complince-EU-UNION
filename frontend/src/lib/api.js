import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API_BASE = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ---- Concept Paper ----
export const listChapters = () => api.get("/paper/chapters").then((r) => r.data);
export const getChapter = (slug) => api.get(`/paper/chapters/${slug}`).then((r) => r.data);
export const searchChapters = (q) => api.get(`/paper/search`, { params: { q } }).then((r) => r.data);

// ---- Issuer / Verifier ----
export const fetchNonce = () => api.post("/issuer/nonce").then((r) => r.data);
export const issueCredential = (body) => api.post("/issuer/credential", body).then((r) => r.data);
export const revokeCredential = (idx) => api.post(`/issuer/status-list/primary/revoke/${idx}`).then((r) => r.data);
export const verifyPresentation = (body) => api.post("/verifier/verify", body).then((r) => r.data);

// ---- mDoc ----
export const issueMdoc = (body) => api.post("/mdoc/issue", body).then((r) => r.data);
export const verifyMdoc = (body) => api.post("/mdoc/verify", body).then((r) => r.data);
export const createEngagement = () => api.post("/mdoc/engagement").then((r) => r.data);

// ---- Trust ----
export const getCaChain = () => api.get("/trust/ca/chain").then((r) => r.data);
export const parseLotl = (xml) => api.post("/trust/lotl/parse", { xml }).then((r) => r.data);

// ---- Compliance ----
export const getMetrics = () => api.get("/compliance/metrics").then((r) => r.data);
export const getAuditLog = () => api.get("/compliance/audit-log").then((r) => r.data);
export const verifyAuditChain = () => api.get("/compliance/audit-log/verify").then((r) => r.data);
export const runErasure = (subject_hash) =>
  api.post("/compliance/gdpr/erasure", { subject_hash, reason: "GDPR Art. 17" }).then((r) => r.data);
export const getAiActTransparency = () => api.get("/compliance/ai-act/transparency").then((r) => r.data);
export const dsaPdfUrl = () => `${API_BASE}/compliance/dsa/report.pdf`;

// ---- Countries ----
export const listCountries = () => api.get("/country/list").then((r) => r.data);
export const countryVerify = (body) => api.post("/country/verify", body).then((r) => r.data);

// ---- Hub ----
export const listRepos = () => api.get("/hub/repos").then((r) => r.data);

// ---- Discovery ----
export const wellKnown = () => api.get("/.well-known/openid-credential-issuer").then((r) => r.data);
export const jwks = () => api.get("/.well-known/jwks.json").then((r) => r.data);

export default api;
