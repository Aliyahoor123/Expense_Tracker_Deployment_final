# Spec 01: Database Setup

## 1. Overview

This step replaces the stub implementation in `database/db.py` with a working SQLite implementation. It establishes the persistent data layer for Spendly, including database connection handling, schema creation, and seed data.

This is the foundational step of the project. No other feature can function without it — authentication (register/login), the user profile page, and expense tracking (add/edit/delete/list) all depend on a working database connection and the `users` and `expenses` tables defined here.

## 2. Depends on

This is the first step in the project. It has no prerequisites.

## 3. Routes

- No new routes are added in this step.
- Existing placeholder routes in `app.py` remain unchanged.

## 4. Database Schema

### Table A: `users`

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

### Table B: `expenses`

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id) |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL — must be stored in `YYYY-MM-DD` format |
| description | TEXT | — |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

## 5. Functions to Implement (`database/db.py`)

| Function | Responsibility |
|---|---|
| `get_db()` | Opens `spendly.db` in the project root, sets `row_factory = sqlite3.Row`, enables `PRAGMA foreign_keys = ON`, returns the connection |
| `init_db()` | Creates the `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS`; safe to call multiple times |
| `seed_db()` | Checks whether `users` already has rows — if so, returns early; otherwise inserts one demo user (name: `Demo User`, email: `demo@spendly.com`, password: `demo123` hashed via `werkzeug.security`) and 8 sample expenses linked to that user, covering all 7 categories, with dates spread across the current month |

## 6. Changes to `app.py`

- Import `get_db`, `init_db`, `seed_db` from `database.db`.
- Call `init_db()` and `seed_db()` inside `app.app_context()` on startup.
- The database must be fully initialized and seeded before any route is served.

## 7. Files to Change

- `database/db.py`
- `app.py`

## 8. Files to Create

- None.

## 9. Dependencies

- No new pip packages.
- Use `sqlite3` (Python standard library) and `werkzeug.security` (already listed in `requirements.txt`).

## 10. Categories (Fixed List)

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

## 11. Rules for Implementation

- No ORM, no SQLAlchemy.
- Parameterized queries only — never string formatting in SQL.
- `PRAGMA foreign_keys = ON` must be set on every connection.
- Store `amount` as `REAL`, not `INTEGER`.
- Hash passwords with `generate_password_hash` from `werkzeug.security`.
- `seed_db()` must be idempotent — safe to call multiple times without creating duplicate data.
- Dates must always be stored and read in `YYYY-MM-DD` format.

## 12. Expected Behavior

- `get_db()` must return a connection to `spendly.db` with `row_factory = sqlite3.Row` and foreign key enforcement enabled.
- `init_db()` must create the `users` and `expenses` tables if they do not already exist, and must not error or alter data if the tables already exist.
- `seed_db()` must insert the demo user and 8 sample expenses only on first run; subsequent calls must leave existing data untouched.
- Database-level constraints must enforce: uniqueness of `users.email`, non-null requirements on all `NOT NULL` columns, and referential integrity between `expenses.user_id` and `users.id`.

## 13. Error Handling Expectations

| Scenario | Expected Result |
|---|---|
| Duplicate email insert | Raises a `UNIQUE` constraint failure |
| Expense inserted with invalid `user_id` | Raises a foreign key constraint failure |
| Invalid or malformed queries | Raise a clear, unsuppressed error for debugging |

## 14. Definition of Done

- [ ] Database file (`spendly.db`) is created on app startup
- [ ] Both `users` and `expenses` tables exist with correct schema and constraints
- [ ] Demo user exists with a hashed password
- [ ] 8 sample expenses exist, covering all 7 categories
- [ ] Repeated runs of `seed_db()` do not create duplicate seed data
- [ ] App starts without errors
- [ ] Foreign key enforcement is active and works as expected
- [ ] All database queries use parameterized SQL
