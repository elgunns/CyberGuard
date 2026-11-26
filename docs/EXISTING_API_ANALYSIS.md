# Existing API Analysis — CyberGuard API (Assignment 2)

**Status:** Phase 1 analysis (documents only). Open decisions are listed in §8.
**Scope:** Full inspection of `Reference/CyberGuard-api-main.zip`, extracted to `Reference/api-original/CyberGuard-api-main/`. The original is kept **read-only**. No original file was modified; all test runs used a scratch copy.

---

## 1. What the API is

A FastAPI prototype for an incident-management system. It uses **in-memory mock data** (resets on restart), **mock Bearer tokens** with two roles (user and admin), and **ownership-based access control**. It has **no database, no upload, no log parsing, no detection, no AI, no alerts and no health endpoint.**

| Item | Value |
|---|---|
| Framework | FastAPI, uvicorn (pinned: `fastapi==0.162.5`, `uvicorn==0.54.0`) |
| Dev deps | `pytest>=8.0`, `httpx>=0.27` |
| Python | 3.10+ (uses `X \| None` syntax) |
| Persistence | None. Module-level dict `INCIDENTS` in `app/mock_data.py` |
| Auth | Hardcoded tokens in `app/auth.py` |
| Tests | `tests/test_api.py`, 20 tests |

### 1.1 Test result (verified)

The original tests were run on a **scratch copy** so no cache folders were created in `Reference/`:

```
pip install -r requirements-dev.txt   (in a fresh venv)
pytest -q
....................  20 passed, 1 warning in 1.56s
```

The only warning is a deprecation notice from Starlette about `httpx`. It is harmless for the assignment, but the final project should check the version pin when it sets up its own test dependencies.

---

## 2. Folder structure (original)

```
CyberGuard-api-main/
├── .gitignore.txt          ← misnamed (see §4.3)
├── CONTRIBUTORS.md
├── README.md
├── requirements.txt        fastapi, uvicorn
├── requirements-dev.txt    -r requirements.txt + pytest, httpx
├── app/
│   ├── main.py             FastAPI app; registers error handlers and routers
│   ├── auth.py             Mock Bearer-token auth (USERS dict, get_current_user dependency)
│   ├── errors.py           ApiError + global exception handlers → JSON error envelope
│   ├── mock_data.py        SEED incidents (5) + in-memory INCIDENTS dict + id counter
│   ├── responses.py        success_response() envelope
│   ├── validation.py       validate_incident() hand-written field checks
│   └── routes/
│       ├── greeting.py     GET /api/v1/greeting  (public HTML page)
│       └── incidents.py    CRUD on /api/v1/incidents + ownership checks
└── tests/
    └── test_api.py         20 pytest tests using FastAPI TestClient
```

---

## 3. Endpoints

| Method | Path | Auth | Behaviour |
|---|---|---|---|
| GET | `/api/v1/greeting` | none | HTML page: project description, team table, endpoint list, **mock tokens** |
| GET | `/api/v1/incidents` | Bearer | List with `page`, `perPage` (1–100), `status`, `severity` filters. Users see own incidents; admin sees all. Returns `meta.total/page/perPage` |
| GET | `/api/v1/incidents/{id}` | Bearer | Get one. 404 if missing, 403 if not owner (non-admin) |
| POST | `/api/v1/incidents` | Bearer | Create (201). Status defaults to `Open`. 409 if an unresolved incident with the same title and IP already exists for the owner |
| PUT | `/api/v1/incidents/{id}` | Bearer | **Full replace** of `title`, `severity`, `status` (all required), plus optional `description`, `sourceIp`. 403 if not owner |
| DELETE | `/api/v1/incidents/{id}` | Bearer | Hard delete. 403 if not owner |

### 3.1 Response and error envelopes

- Success: `{"success": true, "message": "...", "data": ..., "meta": {...}?}`
- Error: `{"success": false, "error": {"code": "...", "message": "...", "details": [...]?}}`
- Codes used: `UNAUTHORIZED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404), `VALIDATION_ERROR` (400), `CONFLICT` (409), `METHOD_NOT_ALLOWED` (405), `INTERNAL_ERROR` (500).

This envelope design is **good and reusable** (see §6).

### 3.2 Data model (incident)

`id, title, description, severity (Low|Medium|High|Critical), status (Open|Investigating|Resolved), sourceIp, ownerId, createdAt, updatedAt`

---

## 4. Analysis of the five items the team asked about

Each item below gives **options and trade-offs only**. None of them has been decided.

### 4.1 Mock Bearer-token auth and roles

**Facts**
- Three hardcoded tokens: `user-a-token`, `user-b-token`, `admin-token` (`app/auth.py`).
- Ownership rules: users see and change only their own incidents; admin sees all.
- The proposal (FR-01 to FR-29) has **no authentication or user-accounts requirement.** The proposal's audience is "students, administrators, developers" using a local tool.
- FR-29 requires secrets to come from environment variables. Hardcoded tokens are the opposite pattern, though they are test values, not real secrets.
- The greeting page (`app/routes/greeting.py`, `TOKENS` list) **publishes all three tokens on a public HTML page.** That is acceptable for a classroom prototype but must not carry into the final app.
- Ownership does not fit our data model. In CyberGuard an incident belongs to an **analysis** of an uploaded file, not to a user account.

**Options**

| Option | What it means | Pros | Cons |
|---|---|---|---|
| **A. Keep** | Keep users, roles and ownership as in the assignment. Move the tokens to `.env` | Matches the API assignment most closely. Keeps the role logic that was graded | Adds user concepts the proposal never asks for. Ownership must be linked to analyses. Extra code for Phases 3–8 |
| **B. Simplify** | Remove per-user ownership. Keep one access token read from an environment variable (e.g. `CYBERGUARD_API_TOKEN`) for write operations. Reads are open to the local dashboard | Small amount of code. Still protects write endpoints. Fits a local demo tool | Not a real login system. One shared token |
| **C. Remove** | No authentication at all. Document that CyberGuard is a local, single-user educational tool | Least code. Simplest for beginners and the demo | No protection if the server is exposed. Must be clearly stated in the README and security section |

**Decision (D-01): Option C, remove authentication.** No FR requires it, and a write token would have to live in frontend JavaScript, which violates FR-29. The grade narrative for the API assignment should be discussed with the course instructor if needed.

---

### 4.2 Manual POST and DELETE on incidents

**Facts**
- FR-08: incidents are created **by detection rules**, with evidence and an analysis link.
- FR-10/FR-11: users view incidents and change **status only**. Nothing in the proposal asks users to delete incidents.
- The assignment's `POST` creates an incident from user input. The `DELETE` removes one.
- The `PUT` requires all three main fields, which does not match FR-11 (status change alone). Pagination and filtering (`page`, `perPage`, `status`, `severity`) are useful and match FR-13.

**Options**

| Option | POST | DELETE | PUT | Pros | Cons |
|---|---|---|---|---|---|
| **A. Remove both** | Removed | Removed | Replaced by a status-only endpoint, e.g. `PATCH /api/v1/incidents/{id}/status` | Matches the proposal exactly. Fewer endpoints. Incidents stay trustworthy (only from rules) | Less of the assignment's CRUD is visible. A grader may expect CRUD |
| **B. Keep POST as "manual incident"** | Kept, marked as manual (`source: "manual"`) | Removed | Status-only | Keeps CRUD feel. Useful for testing the dashboard without uploads | Mixes user-entered and rule-generated data. Extra validation to keep both kinds apart |
| **C. Keep all, restricted to admin** | Admin only | Admin only | Status-only for owners, full for admin | Keeps the assignment behaviour | Needs the auth decision in §4.1 first. Still allows deleting evidence, which conflicts with incident traceability |
| **D. Soft delete** | — | Sets `deleted: true` instead of removing | — | Keeps audit trail | Extra complexity. Proposal does not ask for it |

**Decision (D-02): Option A.** Manual POST and DELETE are removed; incidents come only from detection rules. A status-only `PATCH` endpoint is kept for FR-11, because the existing `PUT` requires too many fields.

**Decision (D-15): analyses cannot be deleted.** No FR requires it (FR-17 is view-only), so there is no delete endpoint and the cascade question does not apply.

---

### 4.3 `.gitignore.txt` is misnamed

**Facts**
- The original file is `CyberGuard-api-main/.gitignore.txt`. Git ignores it, so the `.gitignore` rules do not apply to that repository.
- Its contents are: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `.env`, `.pytest_cache/`, `.vscode/`, `.idea/`.
- The README says `.gitignore` exists. That claim is wrong for the original repository.

**Decision (D-10): done.** `Reference/` is excluded in the new `.gitignore`.

**Recommendation (rules for the new repository):**
- Do **not** rename the file inside `Reference/`. That folder is read-only.
- In the **new** repository, the team created a first `.gitignore` in Phase 1 (rules for the local project-rules file, `Reference/` and `.env`). Phase 2 extends it, starting from the same entries and adding: `Reference/`, `uploads/` (temporary uploads), `*.log` copies created during tests, `.pytest_cache/`, `.coverage`, `htmlcov/`, `node_modules/`, `dist/`, `*.zip`.
- Keep `.env` and `.env.*` ignored, but allow `.env.example` to be committed (`!.env.example`).

---

### 4.4 Automated tests: PostgreSQL and mocks for Gemini and Telegram

**Facts**
- The assignment uses FastAPI's `TestClient`. There is no database.
- The proposal requires PostgreSQL persistence (FR-15), real Gemini calls (FR-18/19) and Telegram alerts (FR-22, FR-25–28).
- Tests must never send real messages or use the real Gemini quota. Automated tests must also run on any team member's computer.

**PostgreSQL — options**

| Option | How | Pros | Cons |
|---|---|---|---|
| **A. Separate test database** (recommended for discussion) | Each member creates a `cyberguard_test` database locally. A test env variable (e.g. `TEST_DATABASE_URL`) points to it. Tests create tables once per session and clean rows between tests | Same engine as production, so SQL behaviour matches. Simple to explain | Each member must set up PostgreSQL and the test database locally |
| **B. SQLite for tests** | Use SQLite in pytest | No setup | Different SQL dialect. Can miss PostgreSQL-specific bugs. Conflicts with the "PostgreSQL" requirement for testing |
| **C. Docker test container** | `docker compose` starts a throwaway PostgreSQL | Clean and reproducible | Docker must be installed. Adds a tool the course did not require. Overengineering risk |

**Gemini — mocking approach**
- Put every Gemini call behind one small client module (e.g. `ai/gemini_client.py`) with a clear interface, such as `explain_incident(payload) -> str`.
- Tests replace that client with a **fake** that returns canned text, or that raises an error to test FR-21 (AI failure handling) and FR-27 (three consecutive failures).
- An optional **live test** may call the real API, but it is skipped unless `GEMINI_API_KEY` is set. It is never part of the default test run.
- The 20-second timeout (FR-21) is tested with a fake that sleeps, or with a fake that raises `TimeoutError`.

**Telegram — mocking approach**
- Same pattern: `alerts/telegram.py` exposes a `send_alert(message)` function. Tests inject a fake sender that records messages in a list.
- Cooldown logic (FR-28a/b) is tested with a **fake clock** (a function that returns a controllable time) so tests run instantly and deterministically.
- A live test is optional and skipped unless `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set.

**Decision (D-05): Option A**, a separate `cyberguard_test` database on each member's machine. The planned approach for Gemini and Telegram is the fake-client pattern, described in Phases 2 and 9 of the roadmap.

---

### 4.5 Gemini model name must come from an environment variable

**Facts**
- The proposal names the model as "Gemini 3.5 Flash-Lite; fallback Gemini 2.5 Flash". Model names change, so the exact API identifier must be confirmed when Phase 9 begins.
- The assignment has no AI code, so nothing to reuse here.

**Decision (D-06):** `GEMINI_MODEL` is read from the environment and has no default in code. The proposed model name is the value in `.env.example`, because it is not a secret.

**Proposed approach (in line with the brief):**
- `.env.example` sets `GEMINI_MODEL` to the proposed model name, with the fallback model in a comment.
- `config.py` reads `GEMINI_MODEL`. It has **no default in code**.
- If `GEMINI_API_KEY` or `GEMINI_MODEL` is missing, the AI feature is marked "unavailable". The rule-based analysis still works (FR-21).
- Phase 9 verifies the exact model identifier against Google's current documentation before the first real call. This check is listed in `IMPLEMENTATION_ROADMAP.md`.

---

## 5. Requirement coverage summary

Full table: `REQUIREMENTS_TRACEABILITY.md`.

| Status | Count (of 35 table rows) | Requirements |
|---|---|---|
| Partial (API-level only) | 6 | FR-08, FR-10, FR-11, FR-13, FR-23, FR-29 (intent only, see traceability note) |
| Not started | 29 | All others |

**Honest summary:** The API covers roughly the *incident-viewing and status* part of the proposal, on mock data. It does not cover upload, parsing, detection, persistence, AI, alerts or monitoring. Most of the proposal's "Must" requirements are still ahead.

---

## 6. What we can reuse (copy, do not edit the original)

| Original file | Reuse? | Notes |
|---|---|---|
| `app/errors.py` | **Yes, with changes** | The global error-handler pattern and JSON envelope are good. Add logging (FR-23) and remove the `Exception` catch-all from the response, keeping the generic message |
| `app/responses.py` | **Yes** | Small, clear success envelope |
| `app/validation.py` | **Partly** | The `ipaddress` check for source IP is useful. The hand-written checks duplicate what Pydantic (already installed with FastAPI) does more cleanly. Also contains `read_json_body()`, which is **never used** (dead code) |
| `app/routes/incidents.py` | **Ideas only** | Pagination, `status`/`severity` filters and the list-response `meta` are worth keeping. Ownership checks are removed (D-01), and manual POST and DELETE are removed (D-02) |
| `app/auth.py` | **No (D-01)** | Authentication is removed from the final app |
| `app/mock_data.py` | **No** | Violates the brief's "no hardcoded demonstration data" rule. Replace with database seeding of sample data only if needed for the demo, and keep that separate from application code |
| `app/routes/greeting.py` | **No** | Replaced by the dashboard. Its layout is a design reference only |
| `tests/test_api.py` | **Pattern only** | Good fixture style (`autouse` reset, grouped tests). Tests themselves target the mock API and must be rewritten |
| `requirements.txt` | **Yes** | The FastAPI and uvicorn pins can be reused |
| `requirements-dev.txt` | **Yes** | pytest and httpx |
| `.gitignore.txt` | **Contents only** | See §4.3 |

---

## 7. Defects and quality issues found during inspection

Each item was checked by reading the code. Items marked **verified** were also reproduced on the scratch copy.

| # | Severity | Finding | Where | Verified? |
|---|---|---|---|---|
| D1 | Medium | `POST /api/v1/incidents` with `"status": null` returns **201** and stores `status: null`. The status field then has a value outside `Open/Investigating/Resolved`. Cause: `data.get("status", "Open")` returns `None` when the key exists with a null value. | `routes/incidents.py` `create_incident` | **Verified** (returned `'status': None`) |
| D2 | Low | Greeting page prints all mock tokens and student IDs publicly. | `routes/greeting.py` `TOKENS`, `TEAM` | By code reading |
| D3 | Low | Unfinished TODO left in the code: "replace with your real names, student IDs…". | `routes/greeting.py` line 21 | By code reading |
| D4 | Low | No logging anywhere. The generic 500 handler swallows the exception without recording it, so FR-23 cannot be met as written. | `errors.py` `unexpected_error_handler` | By code reading |
| D5 | Low | Dead code: `read_json_body()` is never called. | `validation.py` | Verified by search |
| D6 | Low | `PUT` requires all of `title`, `severity`, `status`. A status-only change is impossible. | `routes/incidents.py` | By code reading |
| D7 | Info | README claims a `.gitignore` exists. The file is `.gitignore.txt`. | README, repo root | By file listing |
| D8 | Info | Tests rely on module-level global state (`INCIDENTS`). This is fine for a prototype but must not be copied into the final design. | `mock_data.py` | By code reading |

---

## 8. Decisions (from this analysis)

1. **Auth:** Decided: Option C, remove authentication (D-01).
2. **Manual incident endpoints:** Decided: Option A, remove manual POST and DELETE; keep status-only PATCH (D-02).
3. **PostgreSQL tests:** Decided: Option A, separate `cyberguard_test` database (D-05).
4. **Gemini and Telegram mocks:** planned approach is the fake-client pattern in §4.4.
5. **Gemini model:** Decided: `GEMINI_MODEL` from the environment, no code default; proposed name in `.env.example` (D-06). The identifier is to be verified in Phase 9.
6. **Assignment CRUD endpoints:** resolved by D-01 and D-02. The final API keeps list, detail and status update. Discuss the grade narrative with the course instructor if needed.
7. **`Reference/` in git:** Decided: excluded through `.gitignore` (D-10).
8. **Analysis deletion:** Decided: analyses cannot be deleted; no delete endpoint (D-15).
9. **Gemini data policy:** Decided: accepted, because only sanitized evidence is sent (D-14).

Next: `IMPLEMENTATION_ROADMAP.md` lists the phases and the decisions that block them.
