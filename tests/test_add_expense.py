import uuid

from app import app as flask_app
from database.db import get_db, get_user_by_email
from database.queries import insert_expense


def _demo_user_id():
    return get_user_by_email("demo@spendly.com")["id"]


def _delete_expense(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


# ---- insert_expense ---- #

def test_insert_expense_with_description():
    expense_id = insert_expense(_demo_user_id(), 50.0, "Food", "2026-03-20", "Lunch")
    try:
        conn = get_db()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        conn.close()
        assert row["amount"] == 50.0
        assert row["category"] == "Food"
        assert row["date"] == "2026-03-20"
        assert row["description"] == "Lunch"
    finally:
        _delete_expense(expense_id)


def test_insert_expense_without_description():
    expense_id = insert_expense(_demo_user_id(), 50.0, "Food", "2026-03-20", None)
    try:
        conn = get_db()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        conn.close()
        assert row["description"] is None
    finally:
        _delete_expense(expense_id)


# ---- GET /expenses/add ---- #

def test_get_add_expense_requires_login():
    client = flask_app.test_client()
    resp = client.get("/expenses/add")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_get_add_expense_authenticated():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.get("/expenses/add")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    for cat in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert cat in body
    assert 'method="POST"' in body


# ---- POST /expenses/add ---- #

def test_post_add_expense_requires_login():
    client = flask_app.test_client()
    resp = client.post("/expenses/add", data={"amount": "10", "category": "Food", "date": "2026-03-20"})
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_post_add_expense_valid():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    marker = f"TEST-{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/expenses/add",
        data={"amount": "50.0", "category": "Food", "date": "2026-03-20", "description": marker},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")

    conn = get_db()
    row = conn.execute("SELECT * FROM expenses WHERE description = ?", (marker,)).fetchone()
    conn.close()
    assert row is not None
    _delete_expense(row["id"])


def test_post_add_expense_missing_amount():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/add", data={"amount": "", "category": "Food", "date": "2026-03-20"})
    assert resp.status_code == 200
    assert "Amount must be a positive number." in resp.get_data(as_text=True)


def test_post_add_expense_zero_amount():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/add", data={"amount": "0", "category": "Food", "date": "2026-03-20"})
    assert resp.status_code == 200
    assert "Amount must be a positive number." in resp.get_data(as_text=True)


def test_post_add_expense_non_numeric_amount():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/add", data={"amount": "abc", "category": "Food", "date": "2026-03-20"})
    assert resp.status_code == 200
    assert "Amount must be a positive number." in resp.get_data(as_text=True)


def test_post_add_expense_invalid_category():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/add", data={"amount": "10", "category": "NotACategory", "date": "2026-03-20"})
    assert resp.status_code == 200
    assert "Please select a valid category." in resp.get_data(as_text=True)


def test_post_add_expense_invalid_date():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/add", data={"amount": "10", "category": "Food", "date": "not-a-date"})
    assert resp.status_code == 200
    assert "Please enter a valid date." in resp.get_data(as_text=True)


def test_post_add_expense_no_description():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post(
        "/expenses/add",
        data={"amount": "12.34", "category": "Transport", "date": "2026-03-21"},
    )
    assert resp.status_code == 302

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE amount = ? AND date = ? AND category = ?",
        (12.34, "2026-03-21", "Transport"),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["description"] is None
    _delete_expense(row["id"])
