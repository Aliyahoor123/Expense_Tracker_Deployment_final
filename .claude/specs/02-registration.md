# Spec 02: User Registration

## Overview

- This step upgrades the existing stub `GET /register` route into a fully functional registration form that handles both `GET` and `POST`.
- The form accepts `name`, `email`, `password`, and `confirm_password`.
- On success: flash a success message and redirect to `/login`.
- This is the entry point for all authenticated features in Spendly.

## Depends on

- Step 01 — Database setup (`users` table, `get_db()`)

## Routes

- `GET /register` — render registration form — public (already exists as stub, upgrade it)
- `POST /register` — process form, validate input, insert user, redirect to `/login` — public

## Database changes

- No new tables or columns.
- The existing `users` table covers all requirements.
- One new DB helper to add to `database/db.py`:
  - `create_user(name, email, password)`
    - hashes password with werkzeug
    - inserts a row into `users`
    - returns the new user's id
    - raises `sqlite3.IntegrityError` if email is already taken (UNIQUE constraint)

## Templates

- Modify `templates/register.html`:
  - change form action to `url_for('register')` with `method="post"`
  - add `name` attributes to all inputs: `name`, `email`, `password`, `confirm_password`
  - add a block to display flashed error messages (e.g. "Email already registered", "Passwords do not match")
  - keep all existing visual design unchanged

## Files to change

- `app.py` — upgrade `register()` to handle GET and POST; add flash + redirect logic
- `database/db.py` — add `create_user()` helper
- `templates/register.html` — wire up form action/method and flash message display

## Files to create

- None

## New dependencies

- None — uses `werkzeug.security` (already installed) and Flask's built-in `flash`, `redirect`, `url_for`

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only — never use f-strings in SQL
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext
- `app.secret_key` must be set in `app.py` for `flash()` to work (use a hardcoded dev string for now)
- Server-side validation must check in this order:
  - All fields are non-empty
  - `password == confirm_password`
  - Email is not already registered (catch `sqlite3.IntegrityError`)
- On any validation failure: re-render the form with a flashed error — do not redirect
- On success: flash a success message and redirect to `url_for('login')`
- Use `abort(405)` if an unsupported HTTP method reaches the route
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs

## Definition of done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting with all valid fields creates a new user in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error, no DB insert
- [ ] Submitting with an already-registered email re-renders with "Email already registered"
- [ ] Submitting with any empty field re-renders with a validation error
- [ ] Password is stored as a hash — never plaintext — verifiable by inspecting `spendly.db`
- [ ] No duplicate user is created on repeated valid submissions with the same email
