# CyberGuard

AI-powered security log analyzer for CSCI 3509 (Digital Defenders, ADA University).

## Setup

Commands are for Windows PowerShell. You need Python 3.12 and PostgreSQL 16 or newer.

1. Create and activate a virtual environment (run from the project folder):

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

2. Install the pinned packages. `requirements-dev.txt` also installs pytest for the tests:

   ```powershell
   python -m pip install -r requirements-dev.txt
   ```

3. Create your local settings file, then open `.env` and put your PostgreSQL password into `DATABASE_URL` and `TEST_DATABASE_URL` (between the `:` and the `@`):

   ```powershell
   copy .env.example .env
   ```

   `.env` is git-ignored. Never commit it or paste it anywhere.

4. Create the two databases. Use psql or pgAdmin:

   ```sql
   CREATE DATABASE cyberguard;
   CREATE DATABASE cyberguard_test;
   ```

5. Create the tables. The script is safe to run again:

   ```powershell
   python database\init_db.py
   ```

6. Start the server, then open http://127.0.0.1:8000/health in a browser:

   ```powershell
   python -m uvicorn backend.app.main:create_app --factory --reload
   ```

   `/health` returns 200 when the database answers, and 503 with `"status": "degraded"` when it does not.

7. Run the tests. They use `TEST_DATABASE_URL` only, and stop if that database name does not end with `_test`:

   ```powershell
   python -m pytest
   ```

Logs are written to the console and to `logs/cyberguard.log`.
