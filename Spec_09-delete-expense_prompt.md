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
│       ├── 07-add-expense.md                      ← complete
│       └── 08-edit-expense.md                     ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                      ← get_db(), init_db(), seed_db(),
│   │                                                create_user(), get_user_by_email()
│   └── queries.py                                 ← get_user_by_id(), get_summary_stats(),
│                                                    get_recent_transactions() [returns id],
│                                                    get_category_breakdown(),
│                                                    insert_expense(),
│                                                    get_expense_by_id(),
│                                                    update_expense()
├── static/
│   ├── css/
│   │   ├── profile.css
│   │   └── style.css
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                                 ← complete
│   ├── register.html                              ← complete
│   ├── profile.html                              ← complete; transactions table has
│   │                                               "Actions" column with "Edit" links
│   ├── add_expense.html                          ← complete
│   └── edit_expense.html                         ← complete
├── tests/
│   ├── test_backend_connection.py                 ← complete
│   ├── test_add_expense.py                        ← complete
│   └── test_edit_expense.py                       ← complete
├── .gitignore
├── app.py                                         ← GET /expenses/<id>/delete exists
│                                                    as a stub only
├── README.md
└── requirements.txt

Steps 01 through 08 are complete. Now write a spec for Step 09: Implement the Delete
Expense feature at /expenses/<id>/delete.

Save the output as:
  .claude/specs/09-delete-expense.md

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
  — Step 09 lets a logged-in user permanently delete one of their own expenses
    directly from the profile transaction table
  — A "Delete" button per row submits a POST request to /expenses/<id>/delete
  — The handler verifies ownership, removes the row from the database, and
    redirects back to /profile
  — There is no separate confirmation page — a browser-side confirm() dialog
    in the button's onclick handler is used to prevent accidental deletions
  — The existing get_expense_by_id helper from Step 08 is reused for ownership
    verification — no new query lookup functions are needed
  — Only one new mutation helper is added: delete_expense in database/queries.py

Depends on
  — Step 01 — Database setup (expenses table exists)
  — Step 03 — Login / Logout (session["user_id"] is set and enforced)
  — Step 05 — Profile page renders transactions (the delete button lives there)
  — Step 08 — Edit Expense (get_expense_by_id is available; the Actions column
    already exists in the profile transactions table)

Routes
  — POST /expenses/<int:id>/delete — verify ownership, delete the expense row,
    redirect to /profile — logged-in only
  — No GET handler — a bare GET to this URL must return 405

Database changes
  — No new tables or columns
  — The expenses table already has all required columns

Templates
  — Modify: templates/profile.html
      — Inside the existing "Actions" <td> per transaction row, add a delete form:
          — <form> with method="POST" and action="/expenses/{{ tx.id }}/delete"
          — style="display:inline" on the <form> tag is the one permitted
            exception to the no-inline-styles rule — it is a layout-utility
            value only, not a design value
          — onsubmit="return confirm('Delete this expense?')" on the <form> tag
            to provide browser-side confirmation before submission
          — A <button type="submit"> with class="btn-delete" and label "Delete"
      — "Edit" link from Step 08 remains alongside the new "Delete" button

Files to change
  — database/queries.py
      — Add delete_expense(expense_id, user_id)
          — issues a parameterised DELETE FROM expenses WHERE id = ? AND user_id = ?
          — the dual-column WHERE clause is the ownership guard
          — commits and closes the connection before returning
  — app.py
      — Import delete_expense from database.queries
      — Replace the GET-only placeholder at /expenses/<int:id>/delete with a
        POST-only handler:
          — Guard: redirect to /login if not authenticated
          — Call get_expense_by_id(id, session["user_id"]); if None, abort(404)
          — Call delete_expense(id, session["user_id"])
          — Redirect to url_for("profile")
      — Route decorator must be:
        @app.route("/expenses/<int:id>/delete", methods=["POST"])
  — templates/profile.html — add the delete form inside the existing Actions <td>
  — static/css/style.css
      — Add a .btn-delete style using CSS variables for danger colour
        (e.g. a red-toned CSS variable) — never hardcode hex values

Files to create
  — None

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format values into SQL
  — PRAGMA foreign_keys = ON must be enabled on every connection
    (already handled in get_db())
  — delete_expense must scope its DELETE to id = ? AND user_id = ? —
    this is the ownership guard that prevents one user deleting another's expense
  — The route must only accept POST — a bare GET to the URL must return 405
  — Unauthenticated access must redirect to /login (302)
  — If the expense does not exist or belongs to another user, return 404
  — After successful deletion, redirect to url_for("profile") —
    do not render a template
  — The only permitted inline style is style="display:inline" on the <form>
    tag — no hex colours or design values may be inlined anywhere
  — Use CSS variables — never hardcode hex values
  — All templates extend base.html
  — Currency must always display as ₹ — never £ or $
  — Use url_for() for every internal link — never hardcode paths

Tests to write
  — File: tests/test_delete_expense.py
  — Unit tests — format as a table with columns: Function | Input | Expected output:
      — delete_expense with valid expense_id and correct user_id
        → row removed from DB
      — delete_expense with valid expense_id and wrong user_id
        → row remains in DB (0 rows deleted, no error raised)
      — delete_expense with non-existent expense_id
        → no error raised, DB unchanged
  — Route tests (bullet list):
      — POST /expenses/<id>/delete unauthenticated → redirects to /login (302)
      — POST /expenses/<id>/delete authenticated, own expense →
        redirects to /profile (302); row no longer exists in the database
      — POST /expenses/<id>/delete authenticated, other user's expense →
        returns 404; row still exists in the database
      — POST /expenses/<id>/delete authenticated, non-existent id → returns 404
      — GET /expenses/<id>/delete any user → returns 405 (Method Not Allowed)

Definition of done
  — Checkbox list:
    - POST /expenses/<id>/delete while logged out redirects to /login
    - POSTing to /expenses/<id>/delete for a non-existent or other user's
      expense returns 404
    - GET /expenses/<id>/delete returns 405
    - Clicking "Delete" on a transaction row and confirming in the browser
      dialog removes that expense from the database
    - After deletion, the user is redirected to /profile and the deleted
      expense no longer appears in the transaction list
    - Cancelling the browser confirm() dialog does not submit the form and
      leaves the expense intact
    - Each transaction row in the profile table now shows both "Edit" and
      "Delete" actions