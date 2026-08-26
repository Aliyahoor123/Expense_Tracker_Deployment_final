I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── database/
│   ├── __init__.py
│   └── db.py               ← stub file, functions defined but body is `pass`
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── register.html
├── .gitignore
├── app.py                  ← Flask app, placeholder routes only, no DB wired up
├── README.md
└── requirements.txt        ← werkzeug already listed

Write a spec document for Step 1: Replace the stub in database/db.py with a working SQLite implementation.

Save the output as:
  .claude/specs/01-database-setup.md

Create the .claude/specs/ folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use tables for schema definitions
- Use checkbox lists for Definition of Done
- Number all sections exactly as listed below

Include these 14 sections:

1. Overview
   — What this step does and why it is the foundational step
   — Mention that auth, profile, and expense tracking all depend on it

2. Depends on
   — State that this is the first step with no prerequisites

3. Routes
   — No new routes
   — Existing placeholder routes in app.py remain unchanged

4. Database Schema
   — Table A: users (id, name, email, password_hash, created_at)
   — Table B: expenses (id, user_id, amount, category, date, description, created_at)
   — For each column: name, SQLite type, and constraints (PK, autoincrement, NOT NULL, UNIQUE, FK, DEFAULT)
   — expenses.date must note YYYY-MM-DD format requirement

5. Functions to Implement (database/db.py)
   — get_db(): opens spendly.db in project root, sets row_factory = sqlite3.Row,
     enables PRAGMA foreign_keys = ON, returns connection
   — init_db(): creates both tables with CREATE TABLE IF NOT EXISTS, safe to call multiple times
   — seed_db(): checks if users table already has rows — if yes return early;
     otherwise insert one demo user (name: Demo User, email: demo@spendly.com,
     password: demo123 hashed via werkzeug) and 8 sample expenses linked to that user,
     covering all 7 categories, with dates spread across the current month

6. Changes to app.py
   — Import get_db, init_db, seed_db from database.db
   — Call init_db() and seed_db() inside app.app_context() on startup
   — DB must be ready before any route is served

7. Files to Change
   — database/db.py and app.py only

8. Files to Create
   — None

9. Dependencies
   — No new pip packages
   — Use sqlite3 (stdlib) and werkzeug.security (already installed)

10. Categories (Fixed List)
    — Food, Transport, Bills, Health, Entertainment, Shopping, Other
    — These are the only valid values; list them as a bullet list

11. Rules for Implementation
    — No ORM, no SQLAlchemy
    — Parameterized queries only — never string formatting in SQL
    — PRAGMA foreign_keys = ON on every connection
    — Store amount as REAL not INTEGER
    — Hash passwords with generate_password_hash from werkzeug.security
    — seed_db() must be idempotent (safe to call multiple times)
    — Dates must always be YYYY-MM-DD

12. Expected Behavior
    — What get_db(), init_db(), seed_db() must do when called correctly
    — What database-level constraints must enforce

13. Error Handling Expectations
    — Duplicate email insert → UNIQUE constraint failure
    — Expense with invalid user_id → foreign key constraint failure
    — Invalid queries → raise clear errors for debugging

14. Definition of Done
    — Checkbox list:
      - Database file created on app startup
      - Both tables exist with correct schema and constraints
      - Demo user exists with hashed password
      - 8 sample expenses exist across all 7 categories
      - No duplicate seed data on repeated runs
      - App starts without errors
      - Foreign key enforcement works
      - All queries use parameterized SQL