import uuid

from app import app as flask_app
from database.db import create_user, get_db, get_user_by_email
from database.queries import delete_expense, get_expense_by_id, insert_expense


def _demo_user_id():
    return get_user_by_email("demo@spendly.com")["id"]


def _delete_expense_row(expense_id):
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


# ---- delete_expense (query helper) ---- #

def test_delete_expense_correct_user():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 10.0, "Food", "2026-06-01", "To delete")
    delete_expense(expense_id, user_id)
    assert get_expense_by_id(expense_id, user_id) is None


def test_delete_expense_wrong_user_no_effect():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 10.0, "Food", "2026-06-01", "To keep")
    other_id, other_email = _create_temp_user()
    try:
        delete_expense(expense_id, other_id)
        assert get_expense_by_id(expense_id, user_id) is not None
    finally:
        _delete_expense_row(expense_id)
        _delete_user(other_id)


def test_delete_expense_nonexistent_no_error():
    delete_expense(9999999, _demo_user_id())  # must not raise


# ---- POST /expenses/<id>/delete ---- #

def test_post_delete_requires_login():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 10.0, "Food", "2026-06-01", "To keep")
    try:
        client = flask_app.test_client()
        resp = client.post(f"/expenses/{expense_id}/delete")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
    finally:
        _delete_expense_row(expense_id)


def test_post_delete_own_expense():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 10.0, "Food", "2026-06-01", "To delete")
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post(f"/expenses/{expense_id}/delete")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")
    assert get_expense_by_id(expense_id, user_id) is None


def test_post_delete_other_users_expense_404():
    user_id = _demo_user_id()
    expense_id = insert_expense(user_id, 10.0, "Food", "2026-06-01", "To keep")
    other_id, other_email = _create_temp_user()
    try:
        client = flask_app.test_client()
        client.post("/login", data={"email": other_email, "password": "pw123456"})
        resp = client.post(f"/expenses/{expense_id}/delete")
        assert resp.status_code == 404
        assert get_expense_by_id(expense_id, user_id) is not None
    finally:
        _delete_expense_row(expense_id)
        _delete_user(other_id)


def test_post_delete_nonexistent_404():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.post("/expenses/999999999/delete")
    assert resp.status_code == 404


def test_get_delete_returns_405():
    client = flask_app.test_client()
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    resp = client.get("/expenses/1/delete")
    assert resp.status_code == 405
