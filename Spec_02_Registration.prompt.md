I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       └── 01-database-setup.md   ← already complete
├── database/
│   ├── __init__.py
│   └── db.py                      ← get_db(), init_db(), seed_db() implemented
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── register.html              ← stub template, no form action or method yet
├── .gitignore
├── app.py                         ← GET /register exists as a stub route only
├── README.md
└── requirements.txt

Step 01 (database setup) is complete. Now write a spec for Step 02: Implement user registration.

Save the output as:
  .claude/specs/02-registration.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout — no tables needed for this spec
- Use a checkbox list for Definition of Done
- Use the section names exactly as listed below (no numbers, just headings)

Include these sections in order:

Overview
  — Describe that this step upgrades the existing stub GET /register route into a
    fully functional form handling both GET and POST
  — The form accepts name, email, password, confirm_password
  — On success: flash a success message and redirect to /login
  — This is the entry point for all authenticated features

Depends on
  — Step 01 — Database setup (users table, get_db())

Routes
  — GET /register — render registration form — public
    (already exists as stub, upgrade it)
  — POST /register — process form, validate input, insert user, redirect to /login — public

Database changes
  — No new tables or columns
  — The existing users table covers all requirements
  — One new DB helper to add to database/db.py:
      create_user(name, email, password)
      — hashes password with werkzeug
      — inserts a row into users
      — returns the new user's id
      — raises sqlite3.IntegrityError if email is already taken (UNIQUE constraint)

Templates
  — Modify templates/register.html:
      — change form action to url_for('register') with method="post"
      — add name attributes to all inputs: name, email, password, confirm_password
      — add a block to display flashed error messages
        (e.g. "Email already registered", "Passwords do not match")
      — keep all existing visual design unchanged

Files to change
  — app.py — upgrade register() to handle GET and POST; add flash + redirect logic
  — database/db.py — add create_user() helper
  — templates/register.html — wire up form action/method and flash message display

Files to create
  — None

New dependencies
  — None — uses werkzeug.security (already installed) and Flask's built-in
    flash, redirect, url_for

Rules for implementation
  — No SQLAlchemy or ORMs
  — Parameterised queries only — never use f-strings in SQL
  — Hash passwords with werkzeug.security.generate_password_hash — never store plaintext
  — app.secret_key must be set in app.py for flash() to work
    (use a hardcoded dev string for now)
  — Server-side validation must check in this order:
      1. All fields are non-empty
      2. password == confirm_password
      3. Email is not already registered (catch sqlite3.IntegrityError)
  — On any validation failure: re-render the form with a flashed error — do not redirect
  — On success: flash a success message and redirect to url_for('login')
  — Use abort(405) if an unsupported HTTP method reaches the route
  — All templates must extend base.html
  — Use CSS variables — never hardcode hex values
  — Use url_for() for every internal link — never hardcode URLs

Definition of done
  — Checkbox list:
    - GET /register renders the registration form without errors
    - Submitting with all valid fields creates a new user in users and redirects to /login
    - Submitting with mismatched passwords re-renders the form with an error, no DB insert
    - Submitting with an already-registered email re-renders with "Email already registered"
    - Submitting with any empty field re-renders with a validation error
    - Password is stored as a hash — never plaintext — verifiable by inspecting spendly.db
    - No duplicate user is created on repeated valid submissions with the same email