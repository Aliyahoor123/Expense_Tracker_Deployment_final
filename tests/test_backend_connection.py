import uuid

from app import app as flask_app
from database.db import get_db, get_user_by_email
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)


def _demo_user_id():
    return get_user_by_email("demo@spendly.com")["id"]


# ---- get_user_by_id ---- #

def test_get_user_by_id_valid():
    result = get_user_by_id(_demo_user_id())
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    assert result["member_since"]


def test_get_user_by_id_missing():
    assert get_user_by_id(999999) is None


# ---- get_summary_stats ---- #

def test_get_summary_stats_with_expenses():
    stats = get_summary_stats(_demo_user_id())
    assert stats["total_spent"] == 404.23
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses():
    stats = get_summary_stats(999999)
    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# ---- get_recent_transactions ---- #

def test_get_recent_transactions_with_expenses():
    rows = get_recent_transactions(_demo_user_id())
    dates = [row["date"] for row in rows]
    assert dates == sorted(dates, reverse=True)
    assert all({"date", "description", "category", "amount"} <= row.keys() for row in rows)


def test_get_recent_transactions_no_expenses():
    assert get_recent_transactions(999999) == []


# ---- get_category_breakdown ---- #

def test_get_category_breakdown_with_expenses():
    rows = get_category_breakdown(_demo_user_id())
    totals = [row["amount"] for row in rows]
    assert totals == sorted(totals, reverse=True)
    assert all(isinstance(row["pct"], int) for row in rows)
    assert sum(row["pct"] for row in rows) == 100


def test_get_category_breakdown_no_expenses():
    assert get_category_breakdown(999999) == []


# ---- /profile route ---- #

def test_profile_requires_login():
    client = flask_app.test_client()
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_authenticated_seed_user():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})

    resp = client.get("/profile")
    assert resp.status_code == 200

    body = resp.get_data(as_text=True)
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "$" not in body.split('<script src="')[0]


def test_profile_new_user_has_zero_state():
    client = flask_app.test_client()
    email = f"newuser-{uuid.uuid4().hex[:8]}@spendly.com"
    client.post(
        "/register",
        data={"name": "New Person", "email": email, "password": "pw123456", "confirm_password": "pw123456"},
    )
    client.post("/login", data={"email": email, "password": "pw123456"})

    resp = client.get("/profile")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "₹0.00" in body

    conn = get_db()
    conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
