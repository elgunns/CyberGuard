# Implementation Roadmap — CyberGuard

**Status:** Phase 1 document. Phase 2 starts once the team confirms decisions D-01 to D-13 (§1).

This roadmap splits the work into the 12 phases defined in the team brief. Each phase lists its objectives, owners, files, dependencies, tests and exit criteria. Paths refer to `PROPOSED_PROJECT_STRUCTURE.md`.

**Working rules that apply to every phase:**
- One phase at a time. A phase is reported as finished before the next one starts.
- Before a phase: state objectives, owners, files and dependencies.
- After a phase: run tests, report results, list completed and incomplete requirements, and list what the team should review.
- A feature is reported as working only with evidence: a test run or a documented manual check.
- Tests never call the real Gemini or Telegram APIs; they use fakes.
- Application code contains no hardcoded demonstration data. Sample log files live in `samples/`.
- The team commits after each phase, manually, one logical change per commit (see `TEAM_COMMIT_PLAN.md`).

---

## 0. Phase dependency order

```
P1 Analysis (this)
  └─► P2 Structure + PostgreSQL
        └─► P3 Upload + validation
              └─► P4 Parsing (+ temp-file deletion)
                    └─► P5 Detection rules + severity
                          └─► P6 Incidents API + stats + history
                                ├─► P7 Frontend (UI)  ──┐
                                └─────────────────────── ├─► P8 Integration
                                                         │
                          P6 ─► P9 Gemini AI ◄───────────┘
                                  └─► P10 Telegram + monitoring + health checker
                                        └─► P11 Integration tests + security checks
                                              └─► P12 Documentation + packaging
```

P7 can be built in parallel with P4–P6 by Farat, but **no real integration happens before the API it calls exists.** Phase 7 must not use hardcoded demo data.

---

## 1. Decisions that block implementation

Each decision must be made before the phase shown. Options are in `EXISTING_API_ANALYSIS.md` where noted.

| ID | Decision | Needed before | Options | Status |
|---|---|---|---|---|
| D-01 | Authentication: keep, simplify or remove the mock tokens | P2 | A keep · B simplify (one env token for writes) · C remove | **Decided:** C, remove authentication. No FR requires it, and a write token would live in frontend JavaScript (violates FR-29). |
| D-02 | Manual incident POST/DELETE and status-only update | P6 | See `EXISTING_API_ANALYSIS.md` §4.2 | **Decided:** A, remove manual POST and DELETE; incidents come only from detection rules; keep status-only PATCH (FR-11). |
| D-03 | Supported log formats (required by FR-03, FR-05, FR-06c) | P4 | Proposed: 3 documented formats — see §2 Phase 4 | **Decided:** A, the three proposed formats. |
| D-04 | Database access style | P2 | A `psycopg` 3 with plain SQL in `database/schema.sql` (recommended for beginners, matches "SQL our team knows") · B SQLAlchemy ORM + Alembic | **Decided:** A, psycopg 3 with plain SQL; schema in a `.sql` init script. |
| D-05 | PostgreSQL in tests | P2 | A separate `cyberguard_test` database (recommended) · B SQLite (not recommended) · C Docker container | **Decided:** A, separate `cyberguard_test` database on each member's machine. |
| D-06 | Gemini model name and free-tier data policy | P9 | Environment variable `GEMINI_MODEL` with no default in code (required). **Decided:** `GEMINI_MODEL` from the environment, no code default; the proposed model name is the value in `.env.example` (not a secret), **to be verified in Phase 9**. The free-tier data policy is accepted (D-14). |
| D-07 | Telegram "chat" vs "channel" naming | P10 | Use `TELEGRAM_CHAT_ID` everywhere (proposal's FR-29 wording) | **Decided:** `TELEGRAM_CHAT_ID`. |
| D-08 | Where the health checker runs during demo | P10 | A team member's computer, not the one running the backend (proposal assumption) | **Decided:** separate computer for the demo; the same machine is allowed during development. |
| D-09 | Incident type names and the link between incidents and analyses | P5 | Proposed types: `FAILED_LOGIN_BURST`, `LOGIN_SUCCESS_AFTER_FAILURES`, `REPEATED_APP_ERROR`, `REPEATED_SERVER_ERROR` | **Decided:** the four proposed types; each incident is linked to its analysis ID. |
| D-10 | Keep `Reference/` out of the new repository | P2 | Add `Reference/` to `.gitignore` (recommended) · move it outside the project folder | **Decided:** `Reference/` is excluded through `.gitignore`. Done. |
| D-11 | Frontend testing approach | P7 | A manual checklist + HTML/JS structure checks (recommended) · Playwright browser tests (heavier) | **Decided:** A, manual checklist plus structure checks. |
| D-12 | How the browser reaches the API | P8 | A FastAPI serves the frontend folder as static files (recommended: no CORS) · separate static server with CORS | **Decided:** A, FastAPI serves the frontend as static files (no CORS). |
| D-13 | Size limit definition (5 MB) | P3 | 5 × 1024 × 1024 bytes (proposed) | **Decided:** A, 5 × 1024 × 1024 bytes; the UI message says "5 MB". |
| D-14 | Gemini free-tier data policy | P9 | Accept the free-tier policy, because only sanitized evidence is sent (FR-20) | **Decided:** accepted. No raw logs, raw lines or usernames ever leave the backend. |
| D-15 | Deletion of analyses and the cascade question | P6 | Allow deletion (cascade to incidents) · no delete endpoint | **Decided:** analyses cannot be deleted. No FR requires it (FR-17 is view-only), so there is no delete endpoint and the cascade question does not apply. |

---

## 2. Phase details

### Phase 1 — Repository inspection and architecture  (this phase)

- **Objectives:** Inspect the proposal and the original API. Produce the analysis documents. Set up the team rules. No application code.
- **Owners:** Shared (Elgun reviews backend notes, Farid reviews monitoring notes, Farat reviews frontend notes).
- **Files produced:** `.gitignore`, `docs/EXISTING_API_ANALYSIS.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/TEAM_RESPONSIBILITIES.md`, `docs/PROPOSED_PROJECT_STRUCTURE.md`, `docs/TEAM_COMMIT_PLAN.md`.
- **Extracted:** `Reference/api-original/CyberGuard-api-main/` (read-only).
- **Tests:** Original API test suite run on a scratch copy: **20 passed**. Read-only check: original folder contains no cache files.
- **Exit criteria:** Team has reviewed all documents and confirmed (or amended) the decisions D-01 to D-13.

---

### Phase 2 — Project structure and PostgreSQL setup

- **Objectives**
  - Create the new project skeleton in the repository root (see `PROPOSED_PROJECT_STRUCTURE.md`).
  - Extend `.gitignore` (first version created in Phase 1), add `.env.example` and `requirements.txt` / `requirements-dev.txt`.
  - Load configuration from environment variables and `.env` (FR-29, part).
  - Create the PostgreSQL schema for analyses, parsed events, incidents and AI outputs (FR-15, setup part).
  - Set up the test database and fixtures.
- **Owners:** Elgun (lead: database, config, test setup). Farid: review of `.env.example` (Gemini and Telegram variable names). Farat: review of folder layout.
- **Files:** `.gitignore`, `.env.example`, `requirements.txt`, `requirements-dev.txt`, `backend/app/__init__.py`, `backend/app/main.py` (minimal: app object only), `backend/app/config.py`, `backend/app/db.py`, `backend/app/errors.py` and `backend/app/responses.py` (copied from the original, adapted), `database/schema.sql`, `database/init_db.py`, `backend/tests/conftest.py`, `backend/tests/test_config.py`, `backend/tests/test_db.py`.
- **Dependencies:** D-01, D-04, D-05, D-10 decided. PostgreSQL 16 or newer installed locally on each member's computer.
- **Dependency packages (proposed):** `fastapi`, `uvicorn` (pinned as in the original), `psycopg[binary]`, `python-dotenv`, `pytest`, `httpx`.
- **Tests**
  - `test_config.py`: missing required variable gives a clear error; `.env.example` contains no real secret values (checks that values are empty or placeholder).
  - `test_db.py`: connects to the test database, creates tables from `schema.sql`, inserts and reads one row in each table, drops tables afterwards.
  - Command: `python -m pytest backend/tests -q`
- **Exit criteria:** tests pass on every member's computer; `.gitignore` excludes `.env`, `Reference/`, cache files and virtual environments; `schema.sql` creates all tables without manual steps.

---

### Phase 3 — Upload and validation

- **Objectives**
  - `POST /api/v1/analyses` accepts a multipart upload (`file` field).
  - Check extension (`.log` or `.txt`, case-insensitive) — FR-02a.
  - Check size ≤ 5 × 1024 × 1024 bytes (the UI says "5 MB") — FR-02b (D-13). Check the size while streaming so a huge file is not read fully into memory.
  - Save the file to a temporary folder (`uploads/tmp/`, git-ignored) and create an `analyses` row with status `uploaded`.
  - Reject empty files with a clear message.
  - First use of logging (FR-23 part): log every rejected upload with reason.
- **Owners:** Elgun (API, validation, storage). Farid: `logging_config.py`. Farat: no work in this phase.
- **Files:** `backend/app/routes/analyses.py`, `backend/app/services/upload_validator.py`, `backend/app/services/upload_service.py`, `backend/app/repositories/analyses_repo.py`, `backend/app/logging_config.py`, `backend/tests/test_upload.py`, `samples/` (empty-file and wrong-extension test inputs are created by tests, not stored in the repo).
- **New dependency:** `python-multipart` (required by FastAPI for file uploads).
- **Dependencies:** P2 complete. D-13 decided.
- **Tests**
  - `.log` accepted, `.txt` accepted, `.LOG` accepted, `.exe` rejected, `.log.exe` rejected, no extension rejected.
  - Exactly 5 MB accepted; 5 MB + 1 byte rejected with message naming the limit.
  - Empty file rejected.
  - Rejected uploads leave no file in `uploads/tmp/`.
  - Command: `python -m pytest backend/tests/test_upload.py -q`
- **Exit criteria:** all upload tests pass; rejected files are never written to disk; each rejection returns a 400 error with `code` and a readable `message`.

---

### Phase 4 — Log parsing

- **Objectives**
  - Define three documented log formats (D-03) and one example line for each, in `docs/LOG_FORMATS.md`.
  - Parse each readable line into fields: timestamp, event description, severity level, username, source IP, outcome, and (for web logs) endpoint and status code, when present (FR-05).
  - Count and report skipped lines (FR-04).
  - Reject a file with zero recognizable lines with a clear error (FR-03).
  - Store parsed events in PostgreSQL (`events` table).
  - Delete the temporary file after parsing, success or failure (FR-16).
- **Owners:** Elgun.
- **Files:** `backend/app/services/log_formats.py`, `backend/app/services/parser.py`, `backend/app/repositories/events_repo.py`, `backend/app/services/upload_service.py` (extended to delete), `docs/LOG_FORMATS.md`, `samples/auth_sample.log`, `samples/app_error_sample.log`, `samples/web_access_sample.log`, `samples/mixed_with_invalid_lines.log`, `backend/tests/test_parser.py`.
- **Proposed formats (for D-03 decision):**
  1. **Authentication (syslog-style)**: `Jan 10 10:00:01 host sshd[1234]: Failed password for alice from 203.0.113.10 port 22 ssh2` and `Accepted password for alice from 203.0.113.10 port 22 ssh2`.
  2. **Application error**: `2026-01-10 10:00:01 ERROR [payment] Connection to database timed out (code 1042)`.
  3. **Web server (common log format)**: `203.0.113.5 - - [10/Jan/2026:10:00:01 +0000] "GET /api/orders HTTP/1.1" 503 512`.
- **Dependencies:** P3 complete. D-03 decided.
- **Tests**
  - Each format parses its example line correctly.
  - `mixed_with_invalid_lines.log` reports the exact number of skipped lines.
  - A file with only garbage is rejected (FR-03).
  - Temp file is gone after parsing (success and failure).
  - Usernames and IPs are extracted when present and left empty when absent.
  - Command: `python -m pytest backend/tests/test_parser.py -q`
- **Exit criteria:** tests pass; sample files parse as documented; parsed-event count is stored in the database.

---

### Phase 5 — Detection rules and severity

- **Objectives**
  - Implement the four rules: FR-06a (failed logins per IP, 2 min), FR-06b (repeated normalized app error, 5 min), FR-06c (5xx per endpoint, 5 min), FR-06d (success after 5 failures, 2 min).
  - Mark matching events as suspicious (FR-07).
  - Calculate severity from occurrence count (FR-09a) and the Critical rule (FR-09b).
  - Create incidents with type, severity, timestamp, evidence (related event IDs and short details) and status `Open` (FR-08).
  - Link incidents to their analysis.
- **Owners:** Elgun.
- **Files:** `backend/app/services/detection_rules.py`, `backend/app/services/severity.py`, `backend/app/services/analysis_service.py`, `backend/app/repositories/incidents_repo.py`, `backend/tests/test_detection.py`, `backend/tests/test_severity.py`, extra sample files in `samples/` for each rule (e.g. `samples/brute_force_sample.log`, `samples/success_after_failures_sample.log`).
- **Dependencies:** P4 complete. D-09 decided. Sliding-window definitions from `REQUIREMENTS_TRACEABILITY.md` ("Requirements the team must clarify") confirmed.
- **Tests**
  - Threshold boundaries: 4 failures (no incident), 5 (Low), 9 (Low), 10 (Medium), 19 (Medium), 20 (High), 49 (High), 50 (Critical).
  - Failures spread over more than 2 minutes do not trigger FR-06a.
  - Success from same IP after 5 failures → incident of the FR-06d type, classified Critical (FR-09b).
  - Same app error with different timestamps, numbers and IPs is normalized to one group (FR-06b).
  - Web lines with status 500–599 counted per endpoint (FR-06c).
  - Command: `python -m pytest backend/tests/test_detection.py backend/tests/test_severity.py -q`
- **Exit criteria:** every rule has a boundary test; each incident row contains type, severity, timestamp, evidence and status `Open`.

---

### Phase 6 — Incident management, dashboard statistics and history

- **Objectives**
  - `GET /api/v1/incidents` with filters by severity and status (FR-13) and pagination.
  - `GET /api/v1/incidents/{id}` with evidence (FR-10).
  - `PATCH /api/v1/incidents/{id}/status` to change to Open, Investigating or Resolved (FR-11). Status-only.
  - `GET /api/v1/stats` returns total events, suspicious events, incidents per severity and recent analyses (FR-12).
  - `GET /api/v1/analyses` and `GET /api/v1/analyses/{id}` for history (FR-17).
  - Apply decisions D-01 (no authentication) and D-02 (no manual POST or DELETE; status-only PATCH).
- **Owners:** Elgun (API). Farat reviews the response shapes so the UI can use them.
- **Files:** `backend/app/routes/incidents.py`, `backend/app/routes/stats.py`, `backend/app/routes/analyses.py` (extended), `backend/app/repositories/stats_repo.py`, `backend/app/errors.py` (extended with any new error codes), `backend/tests/test_incidents_api.py`, `backend/tests/test_stats_api.py`, `backend/tests/test_analyses_api.py`.
- **Dependencies:** P5 complete. D-01, D-02 decided.
- **Tests:** filter combinations; 404 for unknown ID; status change saved and visible on next read; invalid status rejected with 400; stats counts match the sample file analysis; history lists analyses newest first.
- **Exit criteria:** every endpoint documented in `README.md` has at least one test; response envelope follows `errors.py`/`responses.py` format.

---

### Phase 7 — Frontend dashboard

- **Objectives (HTML, CSS, vanilla JavaScript only)**
  - Upload page: file picker, client-side extension and size check for quick feedback (server still validates), progress text, clear error display (FR-01).
  - Dashboard: cards for total events, suspicious events, incidents per severity, recent analyses (FR-12) — **data from the API**, not hardcoded.
  - Incident list with severity and status filters (FR-13) and status change control (FR-11).
  - Incident details page showing evidence (FR-10) and the AI explanation area (filled in Phase 9).
  - Analysis history list (FR-17).
  - Responsive layout 360 px to 1920 px with no horizontal scroll (FR-14).
  - All text from logs or the API is inserted with `textContent` (never `innerHTML`) to prevent cross-site scripting.
- **Owners:** Farat (lead). Elgun reviews API calls.
- **Files:** `frontend/index.html`, `frontend/analyses.html`, `frontend/incident.html`, `frontend/css/styles.css`, `frontend/js/api.js` (one fetch wrapper), `frontend/js/utils.js` (escape and format helpers), `frontend/js/upload.js`, `frontend/js/dashboard.js`, `frontend/js/incidents.js`, `frontend/js/incident-detail.js`, `frontend/js/analyses.js`.
- **Dependencies:** P6 endpoints defined (shapes agreed). Can start earlier with agreed JSON shapes.
- **Tests (D-11, recommended):** manual checklist in `TEST_REPORT.md` covering each page at 360 px, 768 px and 1920 px; check that no page contains hardcoded incident data (a simple script searches for known sample IDs or titles); HTML validation of each page.
- **Exit criteria:** every page works against a running backend or shows a clear empty or error state when the backend is down.

---

### Phase 8 — Frontend/backend integration

- **Objectives**
  - Connect every page to the real endpoints (upload → analysis → dashboard → incident → status change).
  - Serve the frontend from FastAPI (D-12) so no CORS configuration is needed.
  - Show backend errors (400, 404, 500) as readable messages.
- **Owners:** Farat and Elgun together. Farid reviews the end-to-end flow.
- **Files:** `backend/app/main.py` (mount static files), `frontend/js/api.js` (base URL), `backend/tests/test_integration_api.py` (uses the same calls as the UI).
- **Dependencies:** P6 and P7 complete.
- **Tests:** API calls in `test_integration_api.py` mirror the UI's requests; manual run: upload `samples/mixed_with_invalid_lines.log` and check counts appear on the dashboard.
- **Exit criteria:** the full manual flow works with no mock data, and the test file passes.

---

### Phase 9 — Gemini AI integration

- **Objectives**
  - Read `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment (D-06). No default model in code; the proposed model name is the value in `.env.example`.
  - Build the sanitized evidence payload (FR-20): rule name, counts, time window, severity, masked IP (proposed: first two octets kept, rest replaced by `x`), normalized error message with usernames and IPs removed. **Never** raw lines, full files or usernames.
  - Incident explanation (FR-18): why suspicious, risks, at least two investigation steps, based only on the payload.
  - Analysis summary (FR-19): ≤ about 150 words.
  - 20-second timeout. On failure or timeout, return an "AI unavailable" status and keep the analysis (FR-21). Log the failure (FR-23).
  - Record AI outputs in the `ai_outputs` table (FR-15).
  - Confirm the exact Gemini model identifier from Google's current documentation before the first real call (D-06).
- **Owners:** Farid (lead). Elgun reviews the database link and endpoint.
- **Files:** `backend/app/ai/gemini_client.py`, `backend/app/ai/sanitizer.py`, `backend/app/ai/explanations.py`, `backend/app/ai/summaries.py`, `backend/app/repositories/ai_repo.py`, `backend/app/routes/incidents.py` (explain endpoint), `backend/app/routes/analyses.py` (summary endpoint), `backend/tests/test_sanitizer.py`, `backend/tests/test_ai_fallback.py`, `backend/tests/test_ai_explanations.py`, `backend/tests/test_ai_live.py` (optional, skipped without key).
- **Dependencies:** P6 complete (incidents and analyses exist).
- **Tests**
  - Sanitizer: a payload built from `samples/` never contains any username or raw line from the sample (test uses a list of forbidden strings taken from the sample file).
  - Fake Gemini client returns canned text → explanation saved.
  - Fake client raises an error → response says "AI unavailable", analysis still available, failure logged.
  - Fake client sleeps longer than 20 s (timeout set small in test) → timeout handled.
  - Missing `GEMINI_API_KEY` → AI marked unavailable without any network call.
  - Live test runs only when `GEMINI_API_KEY` is set; never in the default run.
- **Exit criteria:** all default tests pass with no network access; the live test passes once, and the result is recorded in `TEST_REPORT.md`.

---

### Phase 10 — Telegram alerts, monitoring and health checker

- **Objectives**
  - Telegram sender with one function `send_alert(text)` (FR-22, FR-25–27).
  - Alert rules: Critical incident created (FR-22); 5 HTTP 500 errors in a rolling 5-minute window (FR-26); 3 consecutive AI failures (FR-27).
  - Cooldown: same operational category suppressed for 10 minutes (FR-28a); Critical incident notification at most once per incident ID (FR-28b). The operational cooldown must not suppress Critical incident notifications for different IDs.
  - `GET /health` returns status of backend and database (FR-24).
  - Separate `monitoring/health_checker.py`: calls `/health` every 60 s with a 5-second timeout; sends a Telegram alert after 3 consecutive failures (FR-25). The demo runs it on a separate computer (D-08); the same machine is allowed during development.
  - Count unhandled 500 errors for FR-26 (hook in `errors.py`).
- **Owners:** Farid (Telegram, rules, cooldown, health checker). Elgun (`/health` endpoint, 500 counter hook).
- **Files:** `backend/app/alerts/telegram.py`, `backend/app/alerts/rules.py`, `backend/app/alerts/cooldown.py`, `backend/app/routes/health.py`, `backend/app/errors.py` (hook), `monitoring/health_checker.py`, `backend/tests/test_alerts.py`, `backend/tests/test_cooldown.py`, `backend/tests/test_health.py`, `monitoring/tests/test_health_checker.py`.
- **Dependencies:** P9 complete (AI failure counter), P6 complete (incidents).
- **Tests**
  - Fake sender records messages; no real Telegram call in default tests.
  - Fake clock: 10-minute cooldown boundary (9 min 59 s suppressed; 10 min 1 s sent).
  - Two Critical incidents in the same minute → two alerts; the same incident ID twice → one alert.
  - 4 HTTP 500s → no alert; 5 within 5 minutes → one alert.
  - Health checker with a fake HTTP transport: 2 failures → no alert; 3 in a row → alert; success resets the count.
  - `/health` returns 503 (or status `error`) when the database is unreachable (test by using a wrong DB URL in a test).
- **Exit criteria:** all default tests pass without network access; a live Telegram message is sent once in a supervised demo and the result is recorded in `TEST_REPORT.md`.

---

### Phase 11 — Integration testing and security checks

- **Objectives**
  - End-to-end test: upload sample → parse → detect → AI (fake) → Telegram (fake) → dashboard API returns the expected counts.
  - Security checks (see checklist below).
  - Produce `TEST_REPORT.md` with results, failures and anything not tested.
- **Owners:** Farid (lead on integration testing). Shared review.
- **Files:** `backend/tests/test_e2e.py`, `TEST_REPORT.md`, `scripts/security_check.py` (optional, scans for secrets and forbidden strings), any fixes in earlier modules.
- **Security checklist**
  - No secret values in the repository (search for keys and tokens; `.env` not tracked).
  - `.env` git-ignored; `.env.example` has empty values.
  - Upload size and extension checks cannot be bypassed (`.LOG`, `.log.exe`, very large file, very long filename).
  - All database queries use parameters, not string formatting.
  - Log content shown in the browser is escaped (`textContent`).
  - Error responses never include stack traces.
  - Gemini payloads contain no usernames or raw lines (test from Phase 9 re-run).
  - Telegram messages contain no raw log lines.
- **Dependencies:** P2–P10 complete.
- **Exit criteria:** all default tests pass; the security checklist is ticked with evidence; anything not tested is listed in `TEST_REPORT.md`.

---

### Phase 12 — Documentation and final preparation

- **Objectives**
  - `README.md`: how to install, configure `.env`, run the backend, run the health checker, run tests, and use the dashboard. Each member's part explained (FR list per owner).
  - `DEVELOPMENT_PLAN.md`: final version of this roadmap with actual status.
  - `REQUIREMENTS_TRACEABILITY.md`: all 35 rows updated with Done / Partial / Not done and the evidence.
  - `TEST_REPORT.md`: final test results.
  - `TEAM_COMMIT_PLAN.md`: confirmed list of commits as made.
  - Build the ZIP excluding `.env`, virtual environments, cache files, `uploads/`, and `Reference/`.
  - Demo script for the presentation.
- **Owners:** Shared. Elgun: backend README sections. Farat: frontend section. Farid: monitoring and AI section.
- **Exit criteria:** a fresh clone can follow the README to run the app and the tests; ZIP contents checked against the required list in the brief.

---

## 3. Summary of testing commands (for each phase)

| Phase | Command | Needs |
|---|---|---|
| 2+ | `python -m pytest backend/tests -q` | Local PostgreSQL + test database |
| 3 | `python -m pytest backend/tests/test_upload.py -q` | P2 |
| 4 | `python -m pytest backend/tests/test_parser.py -q` | P3 |
| 5 | `python -m pytest backend/tests/test_detection.py backend/tests/test_severity.py -q` | P4 |
| 6 | `python -m pytest backend/tests -q -k "incidents or stats or analyses"` | P5 |
| 7 | Manual checklist in `TEST_REPORT.md` + HTML checks | P6 |
| 8 | `python -m pytest backend/tests/test_integration_api.py -q` + manual run | P7 |
| 9 | `python -m pytest backend/tests -q` (live test skipped) | P6 |
| 10 | `python -m pytest backend/tests monitoring/tests -q` | P9 |
| 11 | `python -m pytest -q` (all) + security checklist | P2–P10 |
| 12 | Fresh-clone check of the README | All |

---

## 4. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Log formats not agreed in time | Phases 4–5 stall | Decide D-03 before Phase 4 starts; keep the format list short |
| PostgreSQL not installed on a member's computer | Tests cannot run for that member | Phase 2 setup guide, with a check script |
| Gemini model name changes | AI calls fail | Model is an environment variable (D-06); fallback model listed in `.env.example` |
| Gemini free-tier data policy | Data privacy concern | Only sanitized evidence is sent (FR-20). Policy accepted (D-14) |
| Telegram rate limits during demo | Alerts delayed or dropped | Cooldown (FR-28) and fake sender in tests |
| Elgun carries most of the backend load (Phases 3–6 and 9–10 touch his files) | Schedule risk | Split Phase 9 and 10 tasks to Farid as listed; Elgun reviews rather than writes those |
| Original API assignment confused with the new project | Grading or upload mistakes | Keep `Reference/` out of the new repository (D-10) |
| Mock tokens reused in new code | Security weakness | No authentication in the new project (D-01); no tokens are carried over |

---

## 5. Items for team review in Phase 1

1. Decisions D-01 to D-13 are recorded as decided in §1. Phases 2–10 depend on them.
2. Confirm the three log formats in §2 Phase 4 are acceptable for the demo, or propose alternatives.
3. Confirm the owner split in `TEAM_RESPONSIBILITIES.md`.
4. Confirm the phase structure in `PROPOSED_PROJECT_STRUCTURE.md`.
5. Confirm that Phase 2 can start.
