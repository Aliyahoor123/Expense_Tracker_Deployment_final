I'm building Spendly — a personal expense tracker web app built with Flask + SQLite + Jinja2.

Here is my exact project structure:

expense-tracker/
├── .claude/
│   └── specs/
│       ├── 01-database-setup.md              ← complete
│       ├── 02-registration.md                ← complete
│       ├── 03-login_logout.md                ← complete
│       ├── 04-profile.md                     ← complete
│       └── 05-backend-routes-for-profile-page.md  ← complete
├── database/
│   ├── __init__.py
│   ├── db.py                                 ← get_db(), init_db(), seed_db(),
│   │                                           create_user(), get_user_by_email()
│   └── queries.py                            ← get_user_by_id(), get_summary_stats(),
│                                               get_recent_transactions(),
│                                               get_category_breakdown() all implemented
├── static/
│   ├── css/
│   │   └── profile.css                       ← exists, styled with CSS variables
│   └── js/
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html                            ← complete
│   ├── register.html                         ← complete
│   └── profile.html                          ← complete, wired to live DB queries
├── tests/
│   └── test_backend_connection.py            ← complete
├── .gitignore
├── app.py                                    ← /profile renders live data from queries.py
├── README.md
└── requirements.txt

Steps 01 through 05 are complete. Now write a spec for Step 06: Add a date-range filter
to the existing /profile route.

Save the output as:
  .claude/specs/06-date-filter-profile.md

Create the folder if it does not exist.

Rules for the spec itself:
- Output only the Markdown spec document
- No code, no prose outside the spec sections
- Use bullet lists throughout
- Use a checkbox list for Definition of Done
- Use the exact section names listed below — no numbers, just headings

Include these sections in order:

Overview
  — Step 06 adds a date-range filter to the existing /profile route so users can
    narrow the transaction list, summary stats, and category breakdown to a
    specific period
  — The filter is driven entirely by query-string parameters (date_from and date_to)
    on GET /profile — no new routes required
  — A compact filter bar with four quick-select preset buttons ("This Month",
    "Last 3 Months", "Last 6 Months", "All Time") and two <input type="date">
    fields lets users pick any custom range
  — All three data sections (summary stats, recent transactions, category breakdown)
    must respect the active date filter

Depends on
  — Step 01 — Database setup (expenses table with date column must exist)
  — Step 04 — Profile page UI (template with all four sections must exist)
  — Step 05 — Backend connection (get_summary_stats, get_recent_transactions,
    get_category_breakdown in database/queries.py must exist and be wired to
    the /profile route)

Routes
  — No new routes
  — The existing GET /profile route is modified to read two optional query parameters:
      — date_from — ISO date string YYYY-MM-DD, inclusive lower bound
      — date_to — ISO date string YYYY-MM-DD, inclusive upper bound
  — If either parameter is absent or malformed, the route falls back to an
    unfiltered "All Time" view — never errors out

Database changes
  — No database changes
  — The expenses.date column (TEXT, YYYY-MM-DD) already supports BETWEEN
    comparison in SQLite

Templates
  — Modify: templates/profile.html
      — Add a filter bar section above the summary stats row containing:
          — Four quick-select preset buttons: "This Month", "Last 3 Months",
            "Last 6 Months", "All Time"
            — each is a link to /profile with the appropriate date_from/date_to
              query params computed in app.py
            — "All Time" passes no query params (clean /profile URL)
          — A custom range sub-form with two <input type="date"> fields
            (date_from, date_to) and an "Apply" submit button
          — The currently active preset or custom range must be visually
            highlighted with an active state on the button
      — No structural changes to any existing section — only the Jinja variables
        fed into them change when a filter is active

Files to change
  — app.py
      — In profile() view: read date_from and date_to from request.args
      — Validate both values are well-formed ISO dates using
        datetime.strptime(value, "%Y-%m-%d"); on ValueError treat as absent
      — If date_from > date_to after validation: treat both as absent, flash
        "Start date must be before end date."
      — Compute preset date ranges (e.g. first day of current month for
        "This Month") in app.py — never in the template
      — Pass validated date_from, date_to, and preset URL params back to the
        template so the filter bar can reflect the active state
      — Pass date_from and date_to to each of the three query helpers
  — database/queries.py
      — get_summary_stats(user_id, date_from=None, date_to=None)
          — when both params are provided add AND date BETWEEN ? AND ? to the
            expenses queries
          — when absent behave identically to Step 05 (unfiltered)
      — get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)
          — same pattern; ordering newest-first and limit remain unchanged
      — get_category_breakdown(user_id, date_from=None, date_to=None)
          — same pattern; percentage recalculation logic remains unchanged
  — templates/profile.html — add filter bar (see Templates section above)
  — static/css/profile.css — add styles for filter bar and active-preset button
    state using CSS variables only

Files to create
  — None

New dependencies
  — None

Rules for implementation
  — No SQLAlchemy or ORMs — raw sqlite3 only via get_db()
  — Parameterised queries only — never string-format dates into SQL;
    use ? placeholders even for date-range bounds
  — Date validation in app.py: use datetime.strptime(value, "%Y-%m-%d");
    on ValueError treat the param as absent (fall back to no filter)
  — Preset links must be generated with url_for("profile", date_from=..., date_to=...)
    — never hardcoded URL strings in the template
  — When date_from and date_to are both absent, all three query helpers must
    behave identically to their Step 05 behaviour (unfiltered)
  — If date_from > date_to after validation, treat both as absent and flash:
    "Start date must be before end date."
  — "All Time" preset must pass no query params (clean /profile URL)
  — Preset date calculations must be computed in app.py, not in the template
  — Use CSS variables — never hardcode hex values
  — No inline styles
  — All templates extend base.html
  — Use url_for() for every internal link — never hardcode paths

Definition of done
  — Checkbox list:
    - Visiting /profile with no query params returns the same data as Step 05
      (unfiltered, all expenses)
    - Clicking "This Month" filters all three sections to the current calendar
      month only
    - Clicking "Last 3 Months" filters to expenses in the 3-month window
      ending today
    - Clicking "Last 6 Months" filters to expenses in the 6-month window
      ending today
    - Clicking "All Time" removes any active filter and shows all expenses
    - Submitting a custom date range with valid date_from and date_to shows
      only expenses within that range in all three sections
    - Submitting a range where date_from > date_to shows a flash error and
      falls back to the unfiltered view
    - Submitting a malformed date string (e.g. date_from=not-a-date) does not
      crash the app — it silently falls back to the unfiltered view
    - The active preset button or custom-range fields visually indicate which
      filter is currently applied
    - All amounts continue to display the ₹ symbol regardless of active filter
    - A user with no expenses in the selected range sees ₹0.00 total spent,
      0 transactions, and an empty category breakdown — no errors