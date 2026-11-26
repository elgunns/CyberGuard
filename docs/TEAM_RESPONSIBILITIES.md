# Team Responsibilities — CyberGuard

**Status:** Proposed work split, open for team confirmation (§6). Based on the team's split in the project brief and on the requirement counts in `REQUIREMENTS_TRACEABILITY.md`.

**Team (Digital Defenders, ADA University, CSCI 3509):**

| Member | Area | Main phases |
|---|---|---|
| **Farat Babayev** | Frontend dashboard (HTML, CSS, vanilla JS) | P7, P8 (lead), review P2 and P6 |
| **Elgun Atayev** | Backend REST API, PostgreSQL, parsing, detection, incidents | P2 (lead), P3–P6 (lead), P8 (support), P9–P10 (reviewer) |
| **Farid Guliyev** | Gemini AI, Telegram, monitoring, health checker, integration testing | P9 (lead), P10 (lead), P11 (lead), P3 logging setup |
| **All three** | Architecture decisions, integration, code review, system testing, documentation and demo | All phases (review), P11, P12 |

---

## 1. Ownership by requirement

Each requirement has **one owner** who writes the code and tests. Others review.

| Requirement | Owner | Reviewer | Note |
|---|---|---|---|
| FR-01 upload (API) | Elgun | Farid | |
| FR-01 upload (form) | Farat | Elgun | |
| FR-02a, FR-02b | Elgun | Farid | |
| FR-03, FR-04, FR-05 | Elgun | Farid | |
| FR-06a–d, FR-07 | Elgun | Farid | Detection is core logic; Farid reviews the boundary tests |
| FR-08, FR-09a, FR-09b | Elgun | Farid | |
| FR-10, FR-11, FR-13 (API) | Elgun | Farat | |
| FR-10, FR-11, FR-13 (UI) | Farat | Elgun | |
| FR-12 (API) | Elgun | Farat | |
| FR-12 (dashboard UI) | Farat | Elgun | |
| FR-14 | Farat | Elgun | Responsive testing |
| FR-15 (database schema) | Elgun | Farid | |
| FR-16 | Elgun | Farid | |
| FR-17 (API and UI) | Elgun (API), Farat (UI) | Each other | |
| FR-18, FR-19 (AI) | Farid | Elgun | |
| FR-18, FR-19 (display in UI) | Farat | Farid | |
| FR-20, FR-21 | Farid | Elgun | Security-sensitive: all three review the sanitizer |
| FR-22 | Farid | Elgun | |
| FR-23 (logging setup) | Farid | Elgun | |
| FR-23 (exception handler) | Elgun | Farid | |
| FR-24 (`/health` endpoint) | Elgun | Farid | |
| FR-25 (health checker) | Farid | Elgun | |
| FR-26, FR-27, FR-28a, FR-28b | Farid | Elgun | |
| FR-29 (database config) | Elgun | Farid | |
| FR-29 (Gemini and Telegram config) | Farid | Elgun | |
| Integration tests (P8, P11) | Farid (P11), Farat and Elgun (P8) | All | |

---

## 2. Workload check

Counts come from the 35-row table in `REQUIREMENTS_TRACEABILITY.md`, counting the **primary owner** of each row. Rows FR-23 and FR-29 are shared and are counted separately.

| Member | Primary rows owned | Shared rows | Phases led | Assessment |
|---|---|---|---|---|
| Elgun | 22 | FR-23, FR-29 | P2, P3, P4, P5, P6 | **Heaviest load.** Owns upload, parsing, detection, incidents, and the database. Most of the critical path (P2–P6) runs through him |
| Farat | 1 (FR-14) | UI parts of FR-01, FR-10, FR-11, FR-12, FR-13, FR-17 | P7, P8 | Few primary rows, but the frontend is a large amount of work. Can start the P7 layout early |
| Farid | 10 (FR-18 to FR-22, FR-25 to FR-28b) | FR-23, FR-29 | P9, P10, P11 | Later phases, so he may be idle during P2–P6. Recommended: he takes P3 logging, reviews P4–P6 tests, and writes the sample log files used by detection tests |

**Recommendation to reduce Elgun's critical path (for discussion):**
- Farid writes the sample log files for P4 and P5 (`samples/`), with Elgun's format decisions (D-03, D-09).
- Farid writes the boundary tests for detection rules (P5), working from the thresholds in the proposal, while Elgun writes the rule code.
- Farat takes the upload form (FR-01 UI) and the analysis history page (FR-17 UI) as early as P3–P6 allow.
- Farid takes the database query layer for AI and alert records (`repositories/ai_repo.py`), since those tables are his.

These are suggestions. The team decides the final split.

---

## 3. Shared responsibilities

| Area | Who | When |
|---|---|---|
| Architecture decisions (D-01 to D-13 in the roadmap) | All three, in one meeting | Before P2 |
| Code reviews | Each change reviewed by at least one other member before its commit | Every phase |
| Integration | Farat and Elgun (P8); Farid for end-to-end (P11) | P8, P11 |
| System testing | All three run the manual checklist | P11 |
| Final documentation | README: each member writes their part. DEVELOPMENT_PLAN and TEST_REPORT: all three | P12 |
| Demonstration | Each member presents their part, all three present the integrated flow | P12 |

---

## 4. Responsibilities for each phase

Detailed in `IMPLEMENTATION_ROADMAP.md`. Summary:

| Phase | Lead | Support |
|---|---|---|
| P1 Analysis | Shared | — |
| P2 Structure and PostgreSQL | Elgun | Farid (config names), Farat (layout) |
| P3 Upload and validation | Elgun | Farid (logging setup) |
| P4 Parsing | Elgun | Farid (sample files) |
| P5 Detection rules | Elgun | Farid (boundary tests) |
| P6 Incidents, stats, history | Elgun | Farat (response shapes) |
| P7 Frontend | Farat | Elgun (API questions) |
| P8 Integration | Farat | Elgun, Farid |
| P9 Gemini AI | Farid | Elgun (database link) |
| P10 Telegram and monitoring | Farid | Elgun (health endpoint, 500 counter) |
| P11 Integration and security | Farid | All |
| P12 Documentation | Shared | Each member writes own section |

---

## 5. Git responsibilities

- Each commit is made by the **team member who wrote the change**, using their own Git account. Commit authorship must match the real author.
- The commit plan per phase is in `TEAM_COMMIT_PLAN.md`.
- One person opens the pull request per phase; another person reviews and merges it.

---

## 6. Points to confirm

1. Owners in §1 are acceptable to all three members.
2. The workload suggestions in §2 are accepted or amended.
3. Elgun agrees to lead P2–P6, or the lead role is shared.
4. Farid's sample-file and boundary-test role in §2 is accepted.
