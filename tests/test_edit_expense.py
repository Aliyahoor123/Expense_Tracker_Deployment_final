import uuid

from app import app as flask_app
from database.db import create_user, get_db, get_user_by_email
from database.queries import get_expense_by_id, insert_expense, update_expense


def _demo_user_id():
    return get_user_by_email("demo@spendly.com")["id"]


def _delete_expense(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def _delete_user(user_id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def _create_temp_user():
    email = f"other-{uuid.uuid4().hex[:8]}@spendly.com"
    return create_user("Other User", email, "pw123456"), email


# ---- get_expense_by_id ---- #

def test_get_expense_by_id_owned():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        result = get_expense_by_id(expense_id, user_id)
        assert result["id"] == expense_id
        assert result["amount"] == 20.0
        assert result["category"] == "Food"
    finally:
        _delete_expense(expense_id)


def test_get_expense_by_id_wrong_user():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    other_id, other_email = _create_temp_user()
    try:
        assert get_expense_by_id(expense_id, other_id) is None
    finally:
        _delete_expense(expense_id)
        _delete_user(other_id)


def test_get_expense_by_id_missing():
    assert get_expense_by_id(9999999, _demo_user_id()) is None


# ---- update_expense ---- #

def test_update_expense_correct_user():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        update_expense(expense_id, user_id, 99.0, "Bills", "2026-04-02", "Updated")
        row = get_expense_by_id(expense_id, user_id)
        assert row["amount"] == 99.0
        assert row["category"] == "Bills"
    finally:
        _delete_expense(expense_id)


def test_update_expense_wrong_user_no_effect():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    other_id, other_email = _create_temp_user()
    try:
        update_expense(expense_id, other_id, 99.0, "Bills", "2026-04-02", "Updated")
        row = get_expense_by_id(expense_id, user_id)
        assert row["amount"] == 20.0
    finally:
        _delete_expense(expense_id)
        _delete_user(other_id)


# ---- GET /expenses/<id>/edit ---- #

def test_get_edit_requires_login():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        resp = client.get(f"/expenses/{expense_id}/edit")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    finally:
        _delete_expense(expense_id)


def test_get_edit_own_expense():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.get(f"/expenses/{expense_id}/edit")
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert "Snacks" in body
        assert '<option value="Food" selected' in body
    finally:
        _delete_expense(expense_id)


def test_get_edit_other_users_expense_404():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    other_id, other_email = _create_temp_user()
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": other_email, "password": "pw123456"})
        resp = client.get(f"/expenses/{expense_id}/edit")
        assert resp.status_code == 404
    finally:
        _delete_expense(expense_id)
        _delete_user(other_id)


def test_get_edit_nonexistent_404():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.get("/expenses/999999999/edit")
    assert resp.status_code == 404


# ---- POST /expenses/<id>/edit ---- #

def test_post_edit_requires_login():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "30", "category": "Food", "date": "2026-04-02"})
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    finally:
        _delete_expense(expense_id)


def test_post_edit_valid():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(
            f"/expenses/{expense_id}/edit",
            data={"amount": "99.0", "category": "Bills", "date": "2026-04-02", "description": "Updated"},
        )
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/profile")

        row = get_expense_by_id(expense_id, user_id)
        assert row["amount"] == 99.0
        assert row["category"] == "Bills"
        assert row["date"] == "2026-04-02"
        assert row["description"] == "Updated"
    finally:
        _delete_expense(expense_id)


def test_post_edit_other_users_expense_404():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    other_id, other_email = _create_temp_user()
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": other_email, "password": "pw123456"})
        resp = client.post(
            f"/expenses/{expense_id}/edit",
            data={"amount": "50", "category": "Food", "date": "2026-04-02"},
        )
        assert resp.status_code == 404

        row = get_expense_by_id(expense_id, user_id)
        assert row["amount"] == 20.0
    finally:
        _delete_expense(expense_id)
        _delete_user(other_id)


def test_post_edit_missing_amount():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "", "category": "Food", "date": "2026-04-02"})
        assert resp.status_code == 200
        assert "Amount must be a positive number." in resp.get_data(as_text=True)
    finally:
        _delete_expense(expense_id)


def test_post_edit_zero_amount():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "0", "category": "Food", "date": "2026-04-02"})
        assert resp.status_code == 200
        assert "Amount must be a positive number." in resp.get_data(as_text=True)
    finally:
        _delete_expense(expense_id)


def test_post_edit_non_numeric_amount():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "abc", "category": "Food", "date": "2026-04-02"})
        assert resp.status_code == 200
        assert "Amount must be a positive number." in resp.get_data(as_text=True)
    finally:
        _delete_expense(expense_id)


def test_post_edit_invalid_category():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "10", "category": "NotACategory", "date": "2026-04-02"})
        assert resp.status_code == 200
        assert "Please select a valid category." in resp.get_data(as_text=True)
    finally:
        _delete_expense(expense_id)


def test_post_edit_invalid_date():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(f"/expenses/{expense_id}/edit", data={"amount": "10", "category": "Food", "date": "not-a-date"})
        assert resp.status_code == 200
        assert "Please enter a valid date." in resp.get_data(as_text=True)
    finally:
        _delete_expense(expense_id)


def test_post_edit_no_description():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 20.0, "Food", "2026-04-01", "Snacks")
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
        resp = client.post(
            f"/expenses/{expense_id}/edit",
            data={"amount": "15.5", "category": "Transport", "date": "2026-04-03"},
        )
        assert resp.status_code == 302
        row = get_expense_by_id(expense_id, user_id)
        assert row["description"] is None
    finally:
        _delete_expense(expense_id)
