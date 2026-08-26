I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md   ← complete
│       ├── 02-registration.md     ← complete
│       ├── 03-login_logout.md     ← complete
│       └── 04-profile.md         ← complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db(), create_user(),
│                                     get_user_by_email() all implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                 ← complete
│   ├── register.html              ← complete
│   └── profile.html              ← complete with hardcoded data (Step 04)
├── .gitignore
├── app.py                         ← /profile renders hardcoded data from Step 04
├── README.md
└── requirements.txt

Steps 01 through 04 are complete. Now write a spec for Step 05: Replace all hardcoded
data in the /profile route with live SQLite queries.

Save the output as:
  .claude/specs/05-backend-routes-for-profile-page.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a table for the unit test cases
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 05 replaces all hardcoded data in the /profile route with live queries
    against the SQLite database
  — The profile page currently renders a static demo user, fixed summary stats,
    a hand-typed transaction list, and a hardcoded category breakdown
  — This step wires those four sections to real data so every logged-in user
    sees their own expenses
  — Three parallel subagents handle the three independent data concerns —
    transaction history, summary stats, and category breakdown — before being
    integrated into the single /profile route

Depends on
  — Step 01 — Database setup (tables and get_db() exist)
  — Step 02 — Registration (users are stored in the database)
  — Step 03 — Login / Logout (session["user_id"] is set on login)
  — Step 04 — Profile page static UI (template already renders all four sections)

Routes
  — No new routes
  — The existing GET /profile route is modified in place

Database changes
  — No database changes
  — The users and expenses tables already have all required columns:
    user_id, amount, category, date, description, created_at

Templates
  — Modify: templates/profile.html
      — Amounts must be rendered with the ₹ symbol (Indian Rupee) — never £ or $
      — All four dynamic sections are already present in the template —
        no structural changes needed, only the Jinja variables they consume
        are now real

Files to change
  — app.py — replace hardcoded data in the profile() view with calls to the
    new query helpers in database/queries.py
  — templates/profile.html — confirm ₹ symbol is used for all currency display

Files to create
  — database/queries.py — pure query helpers with no Flask imports;
    one function per data concern:
      — get_user_by_id(user_id)
          → dict with name, email, member_since
      — get_summary_stats(user_id)
          → dict with total_spent, transaction_count, top_category
      — get_recent_transactions(user_id, limit=10)
          → list of dicts, each with date, description, category, amount
          → ordered newest-first
      — get_category_breakdown(user_id)
          → list of dicts, each with name, amount, pct
          → pct is percentage of total rounded to nearest int
          → ordered by amount descending

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — Currency must always display as ₹ — never £ or $
  — member_since must be derived from users.created_at and formatted as
    "Month YYYY" (e.g. "January 2026")
  — pct values in category breakdown must sum to 100; use integer rounding
    and adjust the largest category to absorb any rounding remainder
  — If a user has no expenses, all helpers must return zeros and empty lists —
    never raise exceptions
  — All helpers in database/queries.py must call get_db() internally and
    close the connection before returning
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html

Tests to write
  — File: tests/test_backend_connection.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — get_user_by_id with valid user_id → dict with correct name, email, member_since
      — get_user_by_id with non-existent id → None
      — get_summary_stats with user_id with expenses →
        correct total_spent, transaction_count, top_category
      — get_summary_stats with user_id with no expenses →
        {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
      — get_recent_transactions with user_id with expenses →
        list ordered newest-first, each item has date, description, category, amount
      — get_recent_transactions with user_id with no expenses → empty list
      — get_category_breakdown with user_id with expenses →
        list ordered by amount desc; pct values are integers summing to 100
      — get_category_breakdown with user_id with no expenses → empty list
  — Route tests:
      — GET /profile unauthenticated → redirects to /login (302)
      — GET /profile authenticated as seed user:
          — returns 200
          — response contains "Demo User"
          — response contains "demo@spendly.com"
          — response contains ₹ symbol
          — total_spent matches sum of all seed expenses (346.24)
          — transaction_count is 8
          — top_category is "Bills" (highest single-category total)
          — transaction list appears in newest-first order
          — category breakdown contains all 7 categories

Definition of done
  — Checkbox list:
    - Logging in as demo@spendly.com / demo123 shows "Demo User" and
      "demo@spendly.com" on the profile page — not the hardcoded strings
    - Total spent displayed on the profile page equals ₹346.24
    - Transaction count displayed is 8
    - Top category displayed is "Bills"
    - Transaction list shows 8 rows ordered newest date first
    - Category breakdown shows 7 categories with percentages that add up to 100%
    - All amounts on the page display the ₹ symbol
    - Registering a brand-new user and visiting /profile shows ₹0.00 total spent,
      0 transactions, and an empty category breakdown — no errors