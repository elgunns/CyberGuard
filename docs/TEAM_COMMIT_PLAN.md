# Team Task Plan — CyberGuard

**Purpose:** This plan lists the work for each phase as small tasks. Each task has an owner, the files it touches, its dependencies and the way it is tested. Each task maps to one small, meaningful commit. Phases are committed after they are finished, not at the end of the project.

**Working rules**
- One logical change per commit. Keep commits small enough to review in one sitting.
- Stage only the files listed for the task (`git add <file>`). Never use `git add .` or `git add -A`, because that would stage `Reference/` and any local `.env`.
- Run the task's test command before committing. A change with a failing test is not committed.
- Commit messages follow `type(scope): summary`, in the imperative mood, under 72 characters. Types: `docs`, `chore`, `feat`, `fix`, `test`.
- Commits are made manually by the owner named in the task row.
- Each phase ends with a reviewed pull request, not a direct push to `main`. Reviewers are listed in `TEAM_RESPONSIBILITIES.md`.
- Excluded from version control: `Reference/`, the local project-rules file and `.env` (see `.gitignore` and decision D-10).

---

## Phase 1 — Repository inspection and architecture (documents only)

Owner names are first names, as used throughout the team documents (full names in `TEAM_RESPONSIBILITIES.md`). The project brief is kept in `Reference/`, which is excluded from version control, so it has no commit task.

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 1.1 | Add ignore rules for secrets, the original assignment and local files (`chore: add .gitignore for secrets and local files`) | Elgun | `.gitignore` | — | `git check-ignore -v .env Reference/x` reports both ignored |
| 1.2 | Original API analysis (`docs: add existing API analysis`) | Farid | `docs/EXISTING_API_ANALYSIS.md` | 1.1 | Re-run the original tests on a scratch copy: 20 passed |
| 1.3 | Requirements traceability matrix (`docs: add requirements traceability matrix`) | Farat | `docs/REQUIREMENTS_TRACEABILITY.md` | 1.2 | Count rows: 35; counts in summary match the table |
| 1.4 | Implementation roadmap: 12 phases, decisions D-01 to D-13 (`docs: add implementation roadmap`) | Elgun | `docs/IMPLEMENTATION_ROADMAP.md` | 1.3 | Each phase has owners, files, tests and exit criteria |
| 1.5 | Ownership table and folder layout (`docs: add team responsibilities and proposed structure`) | Farat | `docs/TEAM_RESPONSIBILITIES.md`, `docs/PROPOSED_PROJECT_STRUCTURE.md` | 1.4 | Every file in the structure appears in a phase |
| 1.6 | This task plan (`docs: add team task plan`) | Farid | `docs/TEAM_COMMIT_PLAN.md` | 1.5 | Every phase has tasks and test commands |

**Phase 1 check:** `git status` shows `Reference/` and the local project-rules file as excluded. Only the six files above are staged.

---

## Phase 2 — Project structure and PostgreSQL setup

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 2.1 | Add `.env.example` and extend `.gitignore` with Python caches, uploads and runtime files (`chore: add .env.example and extend .gitignore`) | Elgun | `.env.example`, `.gitignore` | 1.1, D-01, D-10 | `git check-ignore -v .env Reference/x` reports both ignored; `.env.example` has no real values |
| 2.2 | FastAPI and uvicorn (same pins as original), psycopg, python-dotenv, pytest, httpx (`chore: add Python requirements files`) | Elgun | `requirements.txt`, `requirements-dev.txt` | 2.1 | `pip install -r requirements-dev.txt` in a new venv |
| 2.3 | Reads environment and `.env`; a missing variable gives a clear error (`feat(config): load settings from environment`) | Farid | `backend/app/__init__.py`, `backend/app/config.py`, `backend/tests/conftest.py`, `backend/tests/test_config.py` | 2.2 | `python -m pytest backend/tests/test_config.py -q` |
| 2.4 | Tables for analyses, events, incidents and ai_outputs; connection helper (`feat(db): add PostgreSQL schema and connection helper`) | Elgun | `database/schema.sql`, `database/init_db.py`, `backend/app/db.py`, `backend/tests/test_db.py` | 2.3, local PostgreSQL and test database | `python database/init_db.py`, then `python -m pytest backend/tests/test_db.py -q` |
| 2.5 | App object, with error and success envelopes copied from the original and adapted (`feat(app): add FastAPI skeleton with error and response helpers`) | Elgun | `backend/app/main.py`, `backend/app/errors.py`, `backend/app/responses.py` | 2.4 | `python -m uvicorn backend.app.main:app` starts; `GET /docs` loads; `python -m pytest backend/tests -q` passes |

**Phase 2 exit check:** the test command passes on every member's computer.

---

## Phase 3 — Upload and validation

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 3.1 | Validate file extension and size; the 5 × 1024 × 1024 byte limit (D-13) is checked while streaming (`feat(upload): validate file extension and size`) | Elgun | `backend/app/services/upload_validator.py`, `backend/tests/test_upload.py` | 2.5 | `python -m pytest backend/tests/test_upload.py -q` (validator tests) |
| 3.2 | Log file and console handler; no secrets in logs (`feat(logging): configure Python logging`) | Farid | `backend/app/logging_config.py`, `backend/app/main.py` | 3.1 | Start the server; a rejected upload writes a line to the log file |
| 3.3 | Multipart upload, temporary save, analysis row with status `uploaded` (`feat(upload): add POST /api/v1/analyses endpoint`) | Elgun | `backend/app/routes/analyses.py`, `backend/app/services/upload_service.py`, `backend/app/repositories/analyses_repo.py`, `backend/app/main.py`, `backend/tests/test_upload.py` | 3.1, 3.2 | `python -m pytest backend/tests/test_upload.py -q`; rejected files leave nothing in `uploads/tmp/` |
| 3.4 | Add `python-multipart`, needed for file uploads (`requirements: add python-multipart for uploads`) | Elgun | `requirements.txt` | 3.3 | Endpoint accepts a file in the test |

---

## Phase 4 — Log parsing

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 4.1 | Three supported formats with examples (D-03) (`docs: define supported log formats`) | Elgun | `docs/LOG_FORMATS.md` | D-03 | Each example line matches its regex in 4.2 (checked in 4.2 tests) |
| 4.2 | Field extraction, skipped-line count, zero-event rejection (`feat(parser): parse the three supported log formats`) | Elgun | `backend/app/services/log_formats.py`, `backend/app/services/parser.py`, `backend/tests/test_parser.py`, `samples/auth_sample.log`, `samples/app_error_sample.log`, `samples/web_access_sample.log`, `samples/mixed_with_invalid_lines.log` | 4.1, 3.3 | `python -m pytest backend/tests/test_parser.py -q` |
| 4.3 | Events saved; temporary file deleted in a `finally` block (FR-16) (`feat(events): store parsed events and delete temp upload`) | Elgun | `backend/app/repositories/events_repo.py`, `backend/app/services/upload_service.py`, `backend/app/services/analysis_service.py`, `backend/tests/test_parser.py` | 4.2, 2.4 | `python -m pytest backend/tests/test_parser.py -q`; temporary folder is empty after success and after failure |

---

## Phase 5 — Detection rules and severity

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 5.1 | FR-06a with a sliding 2-minute window (`feat(detection): add failed-login burst rule`) | Elgun | `backend/app/services/detection_rules.py`, `samples/brute_force_sample.log`, `backend/tests/test_detection.py` | 4.3 | `python -m pytest backend/tests/test_detection.py -q` (4 vs 5 failures boundary) |
| 5.2 | FR-06d, classified Critical (FR-09b) (`feat(detection): add success-after-failures rule`) | Elgun | `backend/app/services/detection_rules.py`, `samples/success_after_failures_sample.log`, `backend/tests/test_detection.py` | 5.1 | Same test file; success after 5 failures creates an incident |
| 5.3 | FR-06b (normalized message) and FR-06c (per endpoint) (`feat(detection): add repeated application error and 5xx rules`) | Elgun | `backend/app/services/detection_rules.py`, `backend/tests/test_detection.py` | 5.2 | Same test file; normalization test and 5xx-per-endpoint test |
| 5.4 | Low, Medium, High and Critical bands (FR-09a) (`feat(severity): calculate incident severity`) | Elgun | `backend/app/services/severity.py`, `backend/tests/test_severity.py` | 5.3 | `python -m pytest backend/tests/test_severity.py -q` (boundaries 4, 5, 9, 10, 19, 20, 49, 50) |
| 5.5 | Incident rows with type, severity, timestamp, evidence and status `Open` (FR-07, FR-08) (`feat(incidents): store incidents with evidence`) | Elgun | `backend/app/repositories/incidents_repo.py`, `backend/app/services/analysis_service.py`, `database/schema.sql` (if changed), `backend/tests/test_detection.py` | 5.4 | `python -m pytest backend/tests -q -k detection` |

---

## Phase 6 — Incident management, dashboard statistics and history

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 6.1 | List with filters, detail and status-only PATCH; no manual POST or DELETE (D-02) (FR-10, FR-11, FR-13) (`feat(incidents): add list, detail and status endpoints`) | Elgun | `backend/app/routes/incidents.py`, `backend/app/repositories/incidents_repo.py`, `backend/app/main.py`, `backend/tests/test_incidents_api.py` | 5.5, D-01, D-02 | `python -m pytest backend/tests/test_incidents_api.py -q` |
| 6.2 | Totals and per-severity counts (FR-12) (`feat(stats): add dashboard statistics endpoint`) | Elgun | `backend/app/routes/stats.py`, `backend/app/repositories/stats_repo.py`, `backend/app/main.py`, `backend/tests/test_stats_api.py` | 6.1 | `python -m pytest backend/tests/test_stats_api.py -q` |
| 6.3 | List and detail of previous analyses (FR-17) (`feat(analyses): add analysis history endpoints`) | Elgun | `backend/app/routes/analyses.py`, `backend/app/repositories/analyses_repo.py`, `backend/tests/test_analyses_api.py` | 6.2 | `python -m pytest backend/tests/test_analyses_api.py -q` |

---

## Phase 7 — Frontend dashboard

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 7.1 | Responsive grid, fetch wrapper and text escaping helper (`feat(ui): add base styles and API helper`) | Farat | `frontend/css/styles.css`, `frontend/js/api.js`, `frontend/js/utils.js` | 6.3 (response shapes agreed) | Open `frontend/index.html` in a browser; no console errors |
| 7.2 | File picker, client-side check, error display (`feat(ui): add upload page`) | Farat | `frontend/index.html`, `frontend/js/upload.js` | 7.1 | Manual: upload a `.exe` and a 6 MB file; messages appear; the server still validates |
| 7.3 | Cards from `/api/v1/stats`, no hardcoded data (`feat(ui): add dashboard page`) | Farat | `frontend/index.html`, `frontend/js/dashboard.js` | 7.2, 6.2 | Manual: with the backend stopped, an error message is shown |
| 7.4 | Filters, detail view and status change (`feat(ui): add incident list and detail pages`) | Farat | `frontend/incident.html`, `frontend/js/incidents.js`, `frontend/js/incident-detail.js` | 7.3, 6.1 | Manual checklist in `TEST_REPORT.md` |
| 7.5 | Analysis history list (FR-17) (`feat(ui): add analysis history page`) | Farat | `frontend/analyses.html`, `frontend/js/analyses.js` | 7.4, 6.3 | Manual checklist; check 360 px, 768 px and 1920 px widths |

---

## Phase 8 — Frontend/backend integration

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 8.1 | Static files mounted after API routes (D-12) (`feat(integration): serve frontend from FastAPI`) | Elgun | `backend/app/main.py` | 7.5 | Open `http://127.0.0.1:8000/`; the dashboard loads |
| 8.2 | Same calls the UI makes, in the same order (`test(integration): add API tests for the UI flow`) | Farat | `backend/tests/test_integration_api.py` | 8.1 | `python -m pytest backend/tests/test_integration_api.py -q` |
| 8.3 | Field names corrected to match the final API shapes (`fix(ui): correct field names after integration`) | Farat | `frontend/js/*.js` (only files that changed) | 8.2 | Re-run 8.2 and the manual flow |

---

## Phase 9 — Gemini AI integration

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 9.1 | Sanitized evidence payload: no usernames, raw lines or full file (FR-20) (`feat(ai): build sanitized evidence payload`) | Farid | `backend/app/ai/sanitizer.py`, `backend/tests/test_sanitizer.py` | 6.1 | `python -m pytest backend/tests/test_sanitizer.py -q` |
| 9.2 | Gemini client with 20-second timeout; "AI unavailable" result; failure logged (FR-21, FR-23) (`feat(ai): add Gemini client with timeout and fallback`) | Farid | `backend/app/ai/gemini_client.py`, `backend/tests/test_ai_fallback.py`, `backend/app/config.py` (Gemini variables) | 9.1 | `python -m pytest backend/tests/test_ai_fallback.py -q` (no network) |
| 9.3 | Incident explanations and analysis summaries; outputs stored (FR-15, FR-18, FR-19) (`feat(ai): add incident explanations and summaries`) | Farid | `backend/app/ai/explanations.py`, `backend/app/ai/summaries.py`, `backend/app/repositories/ai_repo.py`, `backend/app/routes/incidents.py`, `backend/app/routes/analyses.py`, `backend/tests/test_ai_explanations.py` | 9.2 | `python -m pytest backend/tests/test_ai_explanations.py -q` |
| 9.4 | Live Gemini test, runs only when `GEMINI_API_KEY` is set (`test(ai): add live Gemini test (skipped by default)`) | Farid | `backend/tests/test_ai_live.py` | 9.3 | Default run shows 1 skipped; with the key set, passes once |

---

## Phase 10 — Telegram alerts, monitoring and health checker

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 10.1 | Telegram sender; 10-minute cooldown (FR-28a); once per incident ID (FR-28b) (`feat(alerts): add Telegram sender and cooldown`) | Farid | `backend/app/alerts/telegram.py`, `backend/app/alerts/cooldown.py`, `backend/tests/test_cooldown.py`, `backend/app/config.py` (Telegram variables) | 9.4 | `python -m pytest backend/tests/test_cooldown.py -q` (fake clock) |
| 10.2 | Critical incident and error alert rules (FR-22, FR-26, FR-27) (`feat(alerts): add critical incident and error alert rules`) | Farid | `backend/app/alerts/rules.py`, `backend/tests/test_alerts.py` | 10.1 | `python -m pytest backend/tests/test_alerts.py -q` (fake sender) |
| 10.3 | `GET /health` with backend and database status (FR-24) (`feat(health): add GET /health endpoint`) | Elgun | `backend/app/routes/health.py`, `backend/app/main.py`, `backend/tests/test_health.py` | 2.5 | `python -m pytest backend/tests/test_health.py -q` |
| 10.4 | Hook for the FR-26 counter; logs endpoint and error type (FR-23) (`feat(errors): count unhandled 500 errors for alerts`) | Elgun | `backend/app/errors.py`, `backend/tests/test_health.py` | 10.2, 10.3 | `python -m pytest backend/tests -q -k "error or health"` |
| 10.5 | Separate health checker: 60-second checks, 5-second timeout, alert after 3 failures (FR-25) (`feat(monitoring): add separate health checker script`) | Farid | `monitoring/health_checker.py`, `monitoring/tests/test_health_checker.py` | 10.3, 10.2 | `python -m pytest monitoring/tests -q`; then run the script against a stopped backend and check one alert (fake or supervised) |

---

## Phase 11 — Integration testing and security checks

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 11.1 | End-to-end pipeline: upload → parse → detect → AI (fake) → alert (fake) → stats (`test(e2e): add end-to-end pipeline test`) | Farid | `backend/tests/test_e2e.py` | 10.5 | `python -m pytest backend/tests/test_e2e.py -q` |
| 11.2 | Scan for keys, tokens and sample usernames in outgoing payloads (`chore(security): add secret and forbidden-string scan`) | Farid | `scripts/security_check.py` | 11.1 | `python scripts/security_check.py` exits 0 |
| 11.3 | Fixes for findings from 11.2 and the security checklist (`fix(security): apply findings from security check`) | Elgun (backend), Farat (UI) | Files changed by findings only | 11.2 | Re-run 11.1 and 11.2 |
| 11.4 | Results, evidence and untested items (`docs(test): add TEST_REPORT.md`) | Farid | `TEST_REPORT.md` | 11.3 | Each claim in the report points to a command or manual check |

---

## Phase 12 — Documentation and final preparation

| ID | Task (suggested commit) | Owner | Files | Depends on | How to test |
|---|---|---|---|---|---|
| 12.1 | Install, configure, run and test instructions, with each member's part (`docs: add README`) | Elgun (setup), Farat (UI section), Farid (monitoring and AI section) | `README.md` | 11.4 | Follow the README in a fresh clone on one computer |
| 12.2 | Final roadmap with actual status (`docs: add development plan`) | Farid | `DEVELOPMENT_PLAN.md` | 12.1 | Every phase marked Done or Partial with evidence |
| 12.3 | Final status for all 35 requirement rows (`docs: finalize requirements traceability`) | Farat | `docs/REQUIREMENTS_TRACEABILITY.md` | 12.2 | Every row has a status and evidence |
| 12.4 | Actual commit hashes and authors (`docs: finalize task plan`) | Elgun | `docs/TEAM_COMMIT_PLAN.md` | 12.3 | Compare with `git log --oneline` |

---

## Summary of tasks per phase

| Phase | Tasks |
|---|---|
| 1 | 6 |
| 2 | 5 |
| 3 | 4 |
| 4 | 3 |
| 5 | 5 |
| 6 | 3 |
| 7 | 5 |
| 8 | 3 |
| 9 | 4 |
| 10 | 5 |
| 11 | 4 |
| 12 | 4 |
| **Total** | **51** |

Each task is small and maps to one requirement group. The owner column matches `TEAM_RESPONSIBILITIES.md`. If a task grows beyond one logical change during implementation, split it before committing.
