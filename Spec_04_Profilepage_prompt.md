I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md   ← complete
│       ├── 02-registration.md     ← complete
│       └── 03-login_logout.md     ← complete
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
│   └── register.html              ← complete
├── .gitignore
├── app.py                         ← GET /profile exists as a stub only
├── README.md
└── requirements.txt

Steps 01, 02, and 03 are complete. Now write a spec for Step 04: Implement the profile page with hardcoded UI data.

Save the output as:
  .claude/specs/04-profile.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a numbered list for the four template sections
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — This step replaces the /profile stub with a fully designed profile page
    showing static, hardcoded data
  — The goal is to establish the complete UI layout before any real DB queries
    are wired up in Step 05
  — Four sections to build: user info card, summary stats, transaction history
    table, category breakdown
  — Building UI first lets the team validate design in isolation and ensures
    templates are ready for the backend-connection step

Depends on
  — Step 01 — Database setup (schema must exist)
  — Step 02 — Registration (user accounts must be creatable)
  — Step 03 — Login + Logout (session must be set; /profile must be a protected route)

Routes
  — GET /profile — render the profile page — logged-in only
    (redirect to /login if not authenticated)

Database changes
  — No database changes
  — The existing users and expenses tables are sufficient
  — No DB queries in this step — all data is hardcoded

Templates
  — Create: templates/profile.html — full profile page extending base.html
  — Must contain four sections:
      1. User info card — avatar initials, name, email, member-since date
         (all hardcoded values)
      2. Summary stats row — total spent, number of transactions, top category
         (all hardcoded values)
      3. Transaction history table — list of recent expenses with date,
         description, category badge, amount (at least 3 hardcoded rows)
      4. Category breakdown — per-category totals as a simple list or
         progress-bar rows (at least 3 hardcoded categories)

Files to change
  — app.py — replace /profile stub with a real view function that:
      — redirects unauthenticated users to /login
      — passes hardcoded context variables (user dict, stats dict, expenses list,
        category breakdown list) to profile.html

Files to create
  — templates/profile.html

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — use raw sqlite3 via get_db() if any DB call is ever needed
  — Parameterised queries only — never string-format SQL
  — Authentication guard: check session.get("user_id"); if absent,
    redirect(url_for("login"))
  — All data passed to the template must be hardcoded Python dicts/lists in
    app.py — no DB queries in this step
  — Use CSS variables — never hardcode hex values
  — No inline styles anywhere in profile.html
  — All templates must extend base.html
  — Category badges must use a CSS class, not inline colour styles
  — Use url_for() for every internal link — never hardcode paths

Definition of done
  — Checkbox list:
    - Visiting /profile without being logged in redirects to /login
    - Visiting /profile while logged in returns HTTP 200
    - The page displays a user info card with a name and email
    - The page displays at least three summary stat values
      (e.g. total spent, transaction count, top category)
    - The page displays a transaction history table with at least three
      hardcoded rows
    - The page displays a category breakdown section with at least three
      categories
    - The navbar shows the logged-in state (username + logout link)
    - No hex colour values appear in profile.html — only CSS variables