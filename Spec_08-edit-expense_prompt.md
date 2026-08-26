I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md                   ← complete
│       ├── 02-registration.md                     ← complete
│       ├── 03-login_logout.md                     ← complete
│       ├── 04-profile.md                          ← complete
│       ├── 05-backend-routes-for-profile-page.md  ← complete
│       ├── 06-date-filter-profile.md              ← complete
│       └── 07-add-expense.md                      ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                      ← get_db(), init_db(), seed_db(),
│   │                                                create_user(), get_user_by_email()
│   └── queries.py                                 ← get_user_by_id(), get_summary_stats(),
│                                                    get_recent_transactions(),
│                                                    get_category_breakdown(),
│                                                    insert_expense()
├── static/
│   ├── css/
│   │   └── profile.css
│   └── js/
├── templates/
│   ├── base.html                                  ← has "Add Expense" navbar link
│   ├── landing.html
│   ├── login.html                                 ← complete
│   ├── register.html                              ← complete
│   ├── profile.html                              ← complete, with date filter +
│   │                                               "Add Expense" button
│   └── add_expense.html                          ← complete
├── tests/
│   ├── test_backend_connection.py                 ← complete
│   └── test_add_expense.py                        ← complete
├── .gitignore
├── app.py                                         ← GET /expenses/<id>/edit exists
│                                                    as a stub only
├── README.md
└── requirements.txt

Steps 01 through 07 are complete. Now write a spec for Step 08: Implement the Edit
Expense feature at /expenses/<id>/edit.

Save the output as:
  .claude/specs/08-edit-expense.md

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
  — Step 08 lets a logged-in user edit any of their own expenses via a
    pre-populated form at /expenses/<id>/edit
  — The GET handler loads the existing expense from the database and renders
    the form with its current values
  — The POST handler validates the submission and updates the row in place
  — Ownership is enforced: a user can only edit expenses that belong to them
  — Two new query helpers are added to database/queries.py:
    get_expense_by_id and update_expense
  — The transactions table in profile.html gains an "Edit" action link per row,
    which requires get_recent_transactions to also return the expense id

Depends on
  — Step 01 — Database setup (expenses table exists with all required columns)
  — Step 03 — Login / Logout (session["user_id"] is set and enforced)
  — Step 05 — Profile page renders transactions (the edit link lives there)
  — Step 07 — Add Expense (establishes the form pattern this step follows)

Routes
  — GET /expenses/<int:id>/edit — render edit form pre-populated with existing
    expense values — logged-in only
  — POST /expenses/<int:id>/edit — validate and save updated expense —
    logged-in only

Database changes
  — No new tables or columns
  — All required columns already exist in expenses:
    id, user_id, amount, category, date, description

Templates
  — Create: templates/edit_expense.html
      — extends base.html
      — form with method="POST" and action="/expenses/{{ expense.id }}/edit"
      — Fields (identical to add_expense.html, all pre-filled with current values):
          — amount — number input, step="0.01", min="0.01", required, pre-filled
          — category — <select> with exactly 7 fixed options, pre-selected to
            current value
          — date — <input type="date">, required, pre-filled to current value
          — description — text input, optional, max 200 chars, pre-filled
      — Submit button labelled "Save Changes" and a cancel link back to /profile
      — Error message block that re-populates submitted (not original) values
        on validation failure
  — Modify: templates/profile.html
      — Add an "Actions" column header to the transactions table <thead>
      — Add an "Edit" link cell per row pointing to
        /expenses/{{ tx.id }}/edit

Files to change
  — database/queries.py
      — Add get_expense_by_id(expense_id, user_id)
          — fetches a single expense row only if it belongs to the given user
          — returns None if not found or if user_id does not match
          — query must scope to id = ? AND user_id = ?
      — Add update_expense(expense_id, user_id, amount, category, date,
        description)
          — issues a parameterised UPDATE scoped to id = ? AND user_id = ?
            for ownership safety
      — Modify get_recent_transactions
          — add id to the SELECT column list so templates can build edit links
  — app.py
      — Import get_expense_by_id and update_expense from database.queries
      — Replace the GET-only placeholder at /expenses/<int:id>/edit with a
        full GET + POST handler:
          — GET: call get_expense_by_id; return 404 if not found or not owned;
            render edit_expense.html with expense and categories list
          — POST: read form fields, validate (same rules as Step 07),
            call update_expense, redirect to url_for("profile") on success;
            re-render form with errors otherwise
          — Route decorator must accept both methods:
            @app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
  — templates/profile.html
      — Add <th>Actions</th> to the table header
      — Add an "Edit" link cell per transaction row

Files to create
  — templates/edit_expense.html

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — get_expense_by_id must scope its query to id = ? AND user_id = ? —
    return None if not found or if ownership check fails
  — update_expense must also include user_id = ? in its WHERE clause as a
    second ownership guard
  — Unauthenticated access to both GET and POST must redirect to /login
  — If the expense does not exist or belongs to another user, return 404
  — Validation rules for POST (identical to Step 07 add expense):
      1. amount: required; must be a positive float greater than 0;
         parse with float(), catch ValueError
      2. category: required; must be one of the 7 fixed categories;
         reject anything else
      3. date: required; must be a valid YYYY-MM-DD string;
         parse with datetime.strptime
      4. description: optional; strip whitespace; store None if blank
  — On any validation error, re-render the form with the error message and
    the submitted (not original) values pre-filled
  — After a successful update, redirect to url_for("profile") —
    do NOT render the form again
  — Currency must always display as ₹ — never £ or $
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html
  — Use url_for() for every internal link — never hardcode paths

Tests to write
  — File: tests/test_edit_expense.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — get_expense_by_id with valid expense_id and correct user_id
        → returns the matching row as a dict-like object
      — get_expense_by_id with valid expense_id and wrong user_id
        → returns None
      — get_expense_by_id with non-existent expense_id
        → returns None
      — update_expense with valid expense_id, correct user_id, new amount=99.0
        → row in DB reflects updated amount
      — update_expense with valid expense_id, wrong user_id
        → row in DB unchanged (0 rows affected, no error raised)
  — Route tests (bullet list):
      — GET /expenses/<id>/edit unauthenticated → redirects to /login (302)
      — GET /expenses/<id>/edit authenticated, own expense → returns 200;
        response contains form pre-filled with current values; <select> has
        correct category pre-selected
      — GET /expenses/<id>/edit authenticated, other user's expense → returns 404
      — GET /expenses/<id>/edit authenticated, non-existent id → returns 404
      — POST /expenses/<id>/edit unauthenticated → redirects to /login (302)
      — POST /expenses/<id>/edit authenticated, valid data → redirects to
        /profile (302); updated values reflected in the database
      — POST /expenses/<id>/edit authenticated, other user's expense → returns 404
      — POST /expenses/<id>/edit authenticated, missing amount → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, amount = 0 → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, non-numeric amount → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, invalid category → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, invalid date string → returns 200;
        response contains an error message
      — POST /expenses/<id>/edit authenticated, no description → redirects to
        /profile (302); row updated with description = NULL

Definition of done
  — Checkbox list:
    - Visiting /expenses/<id>/edit while logged out redirects to /login
    - Visiting /expenses/<id>/edit for a non-existent or other user's expense
      returns 404
    - Visiting /expenses/<id>/edit while logged in shows a form pre-filled
      with the expense's current values
    - The category dropdown has the correct category pre-selected
    - Submitting valid changes redirects to /profile and the updated values
      appear in the transaction list
    - Submitting with a missing or zero amount re-renders the form with an
      error and the submitted values retained
    - Submitting with an invalid category re-renders the form with an error
    - Submitting with an invalid date re-renders the form with an error
    - Submitting without a description saves the expense with no error
    - Each row in the profile transaction table has an "Edit" link pointing
      to the correct URL