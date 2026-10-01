import calendar
import sqlite3
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (
    delete_expense as db_delete_expense,
    get_category_breakdown,
    get_expense_by_id,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
    insert_expense,
    update_expense,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Profile date-filter helpers                                         #
# ------------------------------------------------------------------ #

def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _months_ago(d, months):
    total = d.month - 1 - months
    year = d.year + total // 12
    month = total % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _build_presets(today, active_from, active_to):
    ranges = [
        ("This Month", today.replace(day=1), today),
        ("Last 3 Months", _months_ago(today, 3), today),
        ("Last 6 Months", _months_ago(today, 6), today),
        ("All Time", None, None),
    ]
    presets = []
    for label, start, end in ranges:
        start_str = start.isoformat() if start else None
        end_str = end.isoformat() if end else None
        presets.append({
            "label": label,
            "date_from": start_str,
            "date_to": end_str,
            "active": active_from == start_str and active_to == end_str,
        })
    return presets


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return render_template("register.html")

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html")

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return render_template("register.html")

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))

    if date_from is None or date_to is None:
        date_from = date_to = None
    elif date_from > date_to:
        flash("Start date must be before end date.", "error")
        date_from = date_to = None

    date_from_str = date_from.isoformat() if date_from else None
    date_to_str = date_to.isoformat() if date_to else None

    presets = _build_presets(date.today(), date_from_str, date_to_str)
    is_custom = date_from_str is not None and not any(p["active"] for p in presets)

    user = get_user_by_id(user_id)
    stats = get_summary_stats(user_id, date_from_str, date_to_str)
    expenses = get_recent_transactions(user_id, date_from=date_from_str, date_to=date_to_str)
    categories = get_category_breakdown(user_id, date_from_str, date_to_str)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        expenses=expenses,
        categories=categories,
        presets=presets,
        date_from=date_from_str,
        date_to=date_to_str,
        is_custom=is_custom,
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "GET":
        form_data = {"amount": "", "category": "", "date": date.today().isoformat(), "description": ""}
        return render_template("add_expense.html", categories=CATEGORIES, form_data=form_data)

    amount_raw = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date_raw = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()
    form_data = {"amount": amount_raw, "category": category, "date": date_raw, "description": description}

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number.", "error")
        return render_template("add_expense.html", categories=CATEGORIES, form_data=form_data)

    if category not in CATEGORIES:
        flash("Please select a valid category.", "error")
        return render_template("add_expense.html", categories=CATEGORIES, form_data=form_data)

    try:
        expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        flash("Please enter a valid date.", "error")
        return render_template("add_expense.html", categories=CATEGORIES, form_data=form_data)

    insert_expense(user_id, amount, category, expense_date.isoformat(), description or None)
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, user_id)
    if expense is None:
        abort(404)

    if request.method == "GET":
        form_data = {
            "amount": expense["amount"],
            "category": expense["category"],
            "date": expense["date"],
            "description": expense["description"] or "",
        }
        return render_template("edit_expense.html", categories=CATEGORIES, form_data=form_data, expense=expense)

    amount_raw = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date_raw = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()
    form_data = {"amount": amount_raw, "category": category, "date": date_raw, "description": description}

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number.", "error")
        return render_template("edit_expense.html", categories=CATEGORIES, form_data=form_data, expense=expense)

    if category not in CATEGORIES:
        flash("Please select a valid category.", "error")
        return render_template("edit_expense.html", categories=CATEGORIES, form_data=form_data, expense=expense)

    try:
        expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        flash("Please enter a valid date.", "error")
        return render_template("edit_expense.html", categories=CATEGORIES, form_data=form_data, expense=expense)

    update_expense(id, user_id, amount, category, expense_date.isoformat(), description or None)
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if get_expense_by_id(id, user_id) is None:
        abort(404)

    db_delete_expense(id, user_id)
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
