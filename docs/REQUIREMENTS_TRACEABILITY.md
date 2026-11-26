# Requirements Traceability — CyberGuard

Source: `Reference/CyberGuard.docx` (functional requirements table and monitoring section).
Compared against: the existing API in `Reference/api-original/` (see `EXISTING_API_ANALYSIS.md`).

**Status key**

| Code | Meaning |
|---|---|
| **Not started** | Nothing in the existing API meets this requirement |
| **Partial** | The existing API has a related piece that must be changed or extended |
| **Done** | Implemented and tested in the new project (no requirement is done yet; Phase 1 covers documentation only) |

**Priority** is taken from the proposal (Must / Should / Could).

**Phase** is the phase in `IMPLEMENTATION_ROADMAP.md` where the requirement is built. **Owner** is the person responsible (see `TEAM_RESPONSIBILITIES.md`).

---

## Requirement table

| ID | Priority | Requirement (short) | Existing API status | Evidence in API | Phase | Owner | Planned new files (see PROPOSED_PROJECT_STRUCTURE) |
|---|---|---|---|---|---|---|---|
| FR-01 | Must | Upload a `.log` or `.txt` file via web UI | Not started | No upload endpoint | 3 (API), 7 (UI) | Elgun (API), Farat (UI) | `backend/app/routes/upload.py`, `frontend/js/upload.js` |
| FR-02a | Must | Reject wrong extension with a reason | Not started | — | 3 | Elgun | `backend/app/services/upload_validator.py` |
| FR-02b | Must | Reject files over 5 MB with a reason | Not started | — | 3 | Elgun | `backend/app/services/upload_validator.py` |
| FR-03 | Must | Reject file with no parseable events, with a clear error | Not started | — | 4 | Elgun | `backend/app/services/parser.py` |
| FR-04 | Should | Skip unparseable lines, report count, continue | Not started | — | 4 | Elgun | `backend/app/services/parser.py` |
| FR-05 | Must | Extract timestamp, event, severity, username, IP, outcome | Not started | — | 4 | Elgun | `backend/app/services/parser.py`, `backend/app/services/log_formats.py` |
| FR-06a | Must | 5+ failed logins from same IP within 2 minutes | Not started | — | 5 | Elgun | `backend/app/services/detection_rules.py` |
| FR-06b | Should | 5+ same normalized app error within 5 minutes | Not started | — | 5 | Elgun | `backend/app/services/detection_rules.py` |
| FR-06c | Could | 5+ HTTP 5xx for same endpoint within 5 minutes | Not started | — | 5 | Elgun | `backend/app/services/detection_rules.py` |
| FR-06d | Should | Successful login from same IP after 5+ failures within 2 minutes | Not started | — | 5 | Elgun | `backend/app/services/detection_rules.py` |
| FR-07 | Must | Mark matching events as suspicious, others non-suspicious | Not started | — | 5 | Elgun | `backend/app/services/detection_rules.py` |
| FR-08 | Must | Create incident with type, severity, timestamp, evidence, status Open | **Partial** | `incidents.py` creates title, severity, status (default Open), createdAt. No type, no evidence list, no analysis link | 5 | Elgun | `backend/app/models/incident.py` (new model) |
| FR-09a | Must | Severity from occurrence count: Low 5–9, Medium 10–19, High 20–49, Critical 50+ | Not started | Severity is set manually by the user | 5 | Elgun | `backend/app/services/severity.py` |
| FR-09b | Should | Critical for FR-06d pattern | Not started | — | 5 | Elgun | `backend/app/services/severity.py` |
| FR-10 | Must | List incidents and open one to see details and evidence | **Partial** | `GET /api/v1/incidents` and `GET /{id}` exist, on mock data, no evidence field | 6 (API), 7 (UI) | Elgun, Farat | `backend/app/routes/incidents.py`, `frontend/incident.html` |
| FR-11 | Must | Change status to Open / Investigating / Resolved and save | **Partial** | `PUT` changes status, but also requires title and severity; no status-only update | 6 | Elgun | `backend/app/routes/incidents.py` |
| FR-12 | Must | Dashboard: total events, suspicious events, incidents per severity, recent analyses | Not started | — | 6 (stats API), 7 (UI) | Elgun, Farat | `backend/app/routes/stats.py`, `frontend/js/dashboard.js` |
| FR-13 | Could | Filter incident list by severity and status | **Partial** | `status` and `severity` query filters exist on `GET /api/v1/incidents` | 6 (API), 7 (UI) | Elgun, Farat | `backend/app/routes/incidents.py` |
| FR-14 | Could | Layout works from 360 px to 1920 px with no horizontal scroll | Not started | Greeting page is responsive but is not the dashboard | 7 | Farat | `frontend/css/styles.css` |
| FR-15 | Must | Store analyses, events, incidents, AI outputs in PostgreSQL | Not started | In-memory dict only | 2 (setup), 3–6 (tables used) | Elgun | `backend/app/db.py`, `database/schema.sql` |
| FR-16 | Must | Delete uploaded file after parsing; never store full file in DB | Not started | — | 4 | Elgun | `backend/app/services/upload_service.py` |
| FR-17 | Could | List previous analyses and open any | Not started | — | 6 (API), 7 (UI) | Elgun, Farat | `backend/app/routes/analyses.py` |
| FR-18 | Must | AI explanation of a selected incident: why suspicious, risks, ≥2 investigation steps, evidence-based only | Not started | — | 9 | Farid | `backend/app/ai/gemini_client.py`, `backend/app/ai/explanations.py` |
| FR-19 | Should | AI summary of one analysis, ≤ ~150 words, incidents per severity and key findings | Not started | — | 9 | Farid | `backend/app/ai/summaries.py` |
| FR-20 | Must | Sanitized evidence payload; no whole file, raw lines or usernames to AI | Not started | — | 9 | Farid | `backend/app/ai/sanitizer.py` |
| FR-21 | Must | If AI fails or times out (20 s), show incidents with "AI unavailable" message, keep analysis, log failure | Not started | — | 9 | Farid | `backend/app/ai/gemini_client.py` |
| FR-22 | Must | Telegram alert on Critical incident (incident ID, analysis ID, type, severity, time) | Not started | — | 10 | Farid | `backend/app/alerts/telegram.py`, `backend/app/alerts/rules.py` |
| FR-23 | Must | Log unhandled exceptions and AI failures with timestamp, endpoint, error type | **Partial** | Global handler returns JSON 500 but logs nothing (`errors.py`) | 10 (logging), 3 (first use) | Farid (logging), Elgun (handler) | `backend/app/logging_config.py`, `backend/app/errors.py` |
| FR-24 | Must | `GET /health` returns backend and database status | Not started | No health endpoint | 10 | Elgun (endpoint) | `backend/app/routes/health.py` |
| FR-25 | Must | Separate health-checker script, every 60 s, Telegram alert after 3 failures | Not started | — | 10 | Farid | `monitoring/health_checker.py` |
| FR-26 | Must | Telegram alert on 5 HTTP 500 errors within a rolling 5-minute window | Not started | — | 10 | Farid | `backend/app/alerts/rules.py` |
| FR-27 | Must | Telegram alert on 3 consecutive AI request failures or timeouts | Not started | — | 10 | Farid | `backend/app/alerts/rules.py` |
| FR-28a | Should | Suppress duplicate operational alerts of same category for 10 minutes | Not started | — | 10 | Farid | `backend/app/alerts/cooldown.py` |
| FR-28b | Should | Send Critical incident notification at most once per incident ID | Not started | — | 10 | Farid | `backend/app/alerts/cooldown.py` |
| FR-29 | Must | Read Telegram token, chat ID, Gemini key, DB credentials from environment or git-ignored `.env`; never in frontend, source or logs | **Partial** | Only `.env` is listed in the misnamed `.gitignore.txt`. No config code | 2 (DB), 9 (Gemini), 10 (Telegram) | Elgun (DB), Farid (AI and Telegram) | `backend/app/config.py`, `.env.example`, `.gitignore` |

---

## Summary

| Status | Count (of 35 rows) | Rows |
|---|---|---|
| Partial | 6 | FR-08, FR-10, FR-11, FR-13, FR-23, FR-29 |
| Not started | 29 | all other rows |
| Done | 0 | none yet |

**Note on FR-29:** the original project has a `.env` entry, but it sits in a file named `.gitignore.txt`, which Git does not read. The entry is recorded as partial only because it shows the intent; no configuration code exists.

**Note on partial items:** "partial" means the **idea or data shape** exists in the API. None of the partial items can be counted as implemented in the new project until the new code and its tests exist.

---

## Requirements the team must clarify before the matching phase

These are gaps or ambiguities in the proposal itself. They are listed here so the team can decide before implementation.

| Req | Gap | Needed before | Proposed resolution (for team decision) |
|---|---|---|---|
| FR-03, FR-05 | The proposal says "authentication, application error and web server logs" but gives no line formats | Phase 4 | Decided (D-03): the three documented formats, one example line each (see `IMPLEMENTATION_ROADMAP.md`) |
| FR-06b | "Normalized application error" is not defined | Phase 5 | Normalize by removing timestamps, numbers, IP addresses and usernames, then compare the rest |
| FR-06c | Requires endpoint and status code | Phase 5 | Only web-server log lines carry both. Rule runs only on those lines |
| FR-06a, FR-06d | "Within 2 minutes" — sliding window or fixed bucket? | Phase 5 | Sliding window per IP, measured from event timestamps (not upload time) |
| FR-06d | "Follows at least 5 failures" — how far back? | Phase 5 | The 5 failures must fall in the 2 minutes before the success |
| FR-09a | Occurrence count: counted over the whole file, or per window? | Phase 5 | Count the events in the window that triggered the rule |
| FR-02b | "5 MB" — 5 × 1024 × 1024 bytes or 5,000,000? | Phase 3 | Decided (D-13): 5 × 1024 × 1024 bytes; the UI message says "5 MB" |
| FR-20 | "Masked source IP" — how? | Phase 9 | Keep the first two octets, replace the rest with `x` (e.g. `203.0.x.x`) |
| FR-22 vs §Monitoring | Proposal says "development team" in FR-22 but "team channel" in the Monitoring section | Phase 10 | Decided (D-07): one Telegram chat; the variable is `TELEGRAM_CHAT_ID` everywhere |
| FR-29 | Section "Keeping secrets safe" says "channel ID", FR-29 says "chat ID" | Phase 10 | Decided (D-07): same as above |
| FR-19 | "About 150 words" — how strictly is it enforced? | Phase 9 | Ask the model for ≤ 150 words and truncate at 170 words if it overshoots |
| Proposal (tech) | Gemini free tier may use submitted data | Phase 9 | Send only sanitized, synthetic-safe data (already required by FR-20). Decided (D-14): accepted; no raw logs, raw lines or usernames leave the backend |
| Proposal (tech) | Exact Gemini model identifier | Phase 9 | Confirm against Google's current documentation before the first call |
| Proposal | No auth requirement, yet the API assignment has one | Phase 2 | Decided (D-01): authentication removed; see `EXISTING_API_ANALYSIS.md` §4.1 |

---

## Open verification items

- **FR-14:** responsive behaviour can only be verified by testing at 360 px, 768 px and 1920 px widths (manual + browser dev tools). Automated checks are limited.
- **FR-22, FR-25–28:** Telegram delivery can only be checked with a real bot. The automated tests use a fake sender. A live demonstration is recorded in `TEST_REPORT.md` when the team runs it.
- **FR-21:** the 20-second timeout must be tested with a fake that sleeps, not with a real Gemini outage.
