# Proposed Project Structure — CyberGuard

**Status:** Proposed structure, open for team review. No folders or application code have been created yet (Phase 1 covers documentation only).

---

## 1. Where the new project lives

| Location | Purpose | Git status |
|---|---|---|
| `C:\Users\ASUS\Desktop\CyberGuard\` (repository root) | **New CyberGuard project.** Will be pushed to a NEW GitHub repository | Git repo exists, no commits yet |
| `Reference/CyberGuard.docx` | Project proposal | Excluded from version control (see D-10) |
| `Reference/CyberGuard-api-main.zip` | Original zip, kept unchanged | Excluded from version control |
| `Reference/api-original/CyberGuard-api-main/` | Extracted copy of the original API. **Read-only** | Excluded from version control |
| `Reference/PROJECT_BRIEF.md` | Full project brief from the team | Excluded from version control |

**Why the project is at the repository root:** the team uses a separate final project directory that is uploaded to a new GitHub repository. Using the repository root as that directory keeps one clear project folder. The original API lives under `Reference/`, which is separate from the application code.

**Decision D-10:** add `Reference/` to `.gitignore` so the assignment files are never uploaded to the new repository. The alternative is to move `Reference/` out of the project folder before the first push. The team confirms the choice.

---

## 2. Proposed tree

Folders and files marked **(P#)** are created in that phase. Everything else is created in Phase 2 or later as noted.

```
CyberGuard/
│
├── README.md                           (P12)  how to install, configure, run, test
├── DEVELOPMENT_PLAN.md                 (P12)  final roadmap with status
├── TEST_REPORT.md                      (P11)  test results and untested items
├── .gitignore                          (P1, extended in P2)
├── .env.example                        (P2)   variable names with empty values, see §5
├── requirements.txt                    (P2)   runtime packages
├── requirements-dev.txt                (P2)   test packages (-r requirements.txt + pytest, httpx)
│
├── docs/
│   ├── EXISTING_API_ANALYSIS.md        (P1)
│   ├── REQUIREMENTS_TRACEABILITY.md    (P1)   requirement status, updated each phase
│   ├── TEAM_COMMIT_PLAN.md             (P1)   task and commit plan per phase
│   ├── IMPLEMENTATION_ROADMAP.md       (P1)
│   ├── TEAM_RESPONSIBILITIES.md        (P1)
│   ├── PROPOSED_PROJECT_STRUCTURE.md   (P1)   (this file)
│   └── LOG_FORMATS.md                  (P4)   the three supported formats with examples
│
├── backend/
│   ├── app/
│   │   ├── __init__.py                 (P2)
│   │   ├── main.py                     (P2 minimal; P8 serves frontend; P10 adds health)
│   │   ├── config.py                   (P2)   reads environment variables and .env
│   │   ├── db.py                       (P2)   PostgreSQL connection helper
│   │   ├── errors.py                   (P2 copied from original, adapted; P3 logging; P10 500 counter)
│   │   ├── responses.py                (P2 copied from original)
│   │   ├── logging_config.py           (P3)   Python logging setup
│   │   ├── routes/
│   │   │   ├── analyses.py             (P3 upload; P6 list and detail; P9 summary)
│   │   │   ├── incidents.py            (P6 list, detail, status; P9 explanation)
│   │   │   ├── stats.py                (P6)   dashboard statistics
│   │   │   └── health.py               (P10)  GET /health
│   │   ├── services/
│   │   │   ├── upload_validator.py     (P3)   extension and size checks
│   │   │   ├── upload_service.py       (P3 save; P4 delete after parse)
│   │   │   ├── log_formats.py          (P4)   regular expressions for each format
│   │   │   ├── parser.py               (P4)   reads lines, counts skipped lines
│   │   │   ├── detection_rules.py      (P5)   FR-06a to FR-06d
│   │   │   ├── severity.py             (P5)   FR-09a and FR-09b
│   │   │   └── analysis_service.py     (P5)   runs the whole pipeline for one upload
│   │   ├── repositories/               (SQL access only, no business logic)
│   │   │   ├── analyses_repo.py        (P3)
│   │   │   ├── events_repo.py          (P4)
│   │   │   ├── incidents_repo.py       (P5)
│   │   │   ├── stats_repo.py           (P6)
│   │   │   └── ai_repo.py              (P9)
│   │   ├── ai/                         (P9)
│   │   │   ├── gemini_client.py        HTTP calls, timeout, error handling
│   │   │   ├── sanitizer.py            builds the safe payload (FR-20)
│   │   │   ├── explanations.py         FR-18
│   │   │   └── summaries.py            FR-19
│   │   └── alerts/                     (P10)
│   │       ├── telegram.py             sends messages through the Bot API
│   │       ├── rules.py                when to alert (Critical, 500s, AI failures)
│   │       └── cooldown.py             10-minute and once-per-ID suppression
│   └── tests/
│       ├── conftest.py                 (P2)   test database fixtures, fake clients
│       ├── test_config.py              (P2)
│       ├── test_db.py                  (P2)
│       ├── test_upload.py              (P3)
│       ├── test_parser.py              (P4)
│       ├── test_detection.py           (P5)
│       ├── test_severity.py            (P5)
│       ├── test_incidents_api.py       (P6)
│       ├── test_stats_api.py           (P6)
│       ├── test_analyses_api.py        (P6)
│       ├── test_integration_api.py     (P8)
│       ├── test_sanitizer.py           (P9)
│       ├── test_ai_fallback.py         (P9)
│       ├── test_ai_explanations.py     (P9)
│       ├── test_ai_live.py             (P9, optional, skipped without key)
│       ├── test_alerts.py              (P10)
│       ├── test_cooldown.py            (P10)
│       ├── test_health.py              (P10)
│       └── test_e2e.py                 (P11)
│
├── database/
│   ├── schema.sql                      (P2)   CREATE TABLE statements
│   └── init_db.py                      (P2)   applies schema.sql to the database
│
├── frontend/                           (P7; no build tools)
│   ├── index.html                      dashboard + upload section
│   ├── analyses.html                   analysis history
│   ├── incident.html                   incident details + AI explanation
│   ├── css/
│   │   └── styles.css                  responsive layout (grid and flexbox)
│   └── js/
│       ├── api.js                      one place that calls the backend
│       ├── utils.js                    escaping and formatting helpers
│       ├── upload.js
│       ├── dashboard.js
│       ├── incidents.js
│       ├── incident-detail.js
│       └── analyses.js
│
├── monitoring/
│   ├── health_checker.py               (P10)  separate process, every 60 seconds
│   └── tests/
│       └── test_health_checker.py      (P10)
│
├── samples/                            (realistic test inputs; no real data)
│   ├── auth_sample.log                 (P4)
│   ├── app_error_sample.log            (P4)
│   ├── web_access_sample.log           (P4)
│   ├── mixed_with_invalid_lines.log    (P4)
│   ├── brute_force_sample.log          (P5)
│   └── success_after_failures_sample.log (P5)
│
└── scripts/                            (optional)
    └── security_check.py               (P11)  scans for secrets and forbidden strings
```

Runtime-created folders (not committed; listed in `.gitignore`):

```
uploads/tmp/        temporary uploads, deleted after parsing (FR-16)
```

---

## 3. Layer responsibilities

To keep the code easy to explain, each layer has one job.

| Layer | Job | May call | Must not |
|---|---|---|---|
| `routes/` | Receive HTTP requests, validate basic input, return the response envelope | `services/`, `repositories/` | Contain SQL or detection logic |
| `services/` | Business logic: validation, parsing, rules, severity | `repositories/`, `ai/`, `alerts/` | Know about HTTP request objects |
| `repositories/` | SQL queries only | `db.py` | Contain business rules |
| `ai/` | Gemini calls and sanitization | `config.py` | Receive raw logs or usernames (enforced by `sanitizer.py` and tests) |
| `alerts/` | Telegram messages and cooldowns | `config.py` | Include raw log lines in messages |
| `monitoring/` | Separate health-check process | HTTP only | Import backend code (it must run outside the FastAPI process) |
| `frontend/` | Display and user actions | Backend API only, through `api.js` | Contain secrets or hardcoded incident data |

**Why `monitoring/` does not import backend code:** the proposal requires the health checker to run separately, so it can notice when the whole backend process is down.

---

## 4. `.gitignore`

First version created in Phase 1. Phase 2 extends it with the project-specific entries below.

```
# Local-only project rules (not part of the submission)
CLAUDE.md

# Secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.coverage
htmlcov/

# Project runtime
uploads/
*.tmp

# Editors
.vscode/
.idea/

# Original assignment (read-only, not part of the new project)
Reference/

# Packaging
*.zip
```

---

## 5. `.env.example` (to be created in Phase 2)

Variable names and empty placeholder values only. Real values go only into a local `.env` file that is git-ignored.

```
# Database (PostgreSQL)
DATABASE_URL=
TEST_DATABASE_URL=

# Google Gemini (Phase 9)
GEMINI_API_KEY=
# Proposed model: Gemini 3.5 Flash-Lite (fallback: Gemini 2.5 Flash). To be verified in Phase 9.
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_TIMEOUT_SECONDS=20

# Telegram (Phase 10)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Health checker (Phase 10)
HEALTH_URL=http://127.0.0.1:8000/health
HEALTH_INTERVAL_SECONDS=60

# Upload limits (Phase 3)
MAX_UPLOAD_MB=5
```

Notes:
- `GEMINI_MODEL` has no default in code (project requirement). `.env.example` holds the proposed model name, which is not a secret (D-06). The proposal's model names are recorded in `IMPLEMENTATION_ROADMAP.md` §1, D-06.
- Each member copies `.env.example` to `.env` locally. The real `.env` is never committed.

---

## 6. Dependencies (`requirements.txt`, planned)

| Package | Why | Added in |
|---|---|---|
| `fastapi==0.162.5` | Web framework (same pin as original API) | P2 |
| `uvicorn==0.54.0` | Server (same pin as original API) | P2 |
| `psycopg[binary]` | PostgreSQL driver (D-04) | P2 |
| `python-dotenv` | Reads `.env` for local development | P2 |
| `python-multipart` | Required by FastAPI for file uploads | P3 |
| `httpx` | Calls Gemini and Telegram. Also used by the health checker and by test clients | P9 |

`requirements-dev.txt` adds `pytest>=8.0` and `httpx>=0.27`. Version pins for new packages are set in the phase that adds them, after checking the current release.

---

## 7. Naming and code conventions

- Python: `snake_case` for files and functions, `PascalCase` for classes. Type hints on function signatures. Short docstrings.
- JavaScript: `camelCase` for functions and variables, `kebab-case` for file names.
- JSON fields returned by the API: `camelCase`, to match the original API (`sourceIp`, `createdAt`).
- Database columns: `snake_case` (PostgreSQL convention).
- One responsibility per file. If a file grows beyond about 300 lines, split it and record the reason in the commit message.

---

## 8. Items for team review

1. Root-as-project layout and `Reference/` handling are decided (D-10).
2. Confirm the `backend/`, `frontend/`, `monitoring/`, `database/`, `samples/` folders.
3. Confirm the layer rules in §3, especially that `monitoring/` must not import backend code.
4. Confirm the `.env.example` variable list and the rule that `GEMINI_MODEL` has no default.
5. Confirm the JSON naming convention in §7 (matches the original API).
