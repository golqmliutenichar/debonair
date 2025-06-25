from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import pymysql, os
from werkzeug.security import check_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")

def _get_db_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_USER_PWD"),
        database=os.getenv("DB_NAME"),
        autocommit=True,
    )

# ── routes ───────────────────────────────────────────────────────────────────
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user  = request.form.get("username","").strip()
        pwd   = request.form.get("password","")

        with _get_db_conn().cursor() as cur:
            cur.execute("SELECT username, password_hash FROM admin_users WHERE username=%s AND is_active=1 ", (user,))
            row = cur.fetchone()

        if row and check_password_hash(row[1], pwd):
            session["admin"] = user           # logged-in flag
            flash("Welcome, {}!".format(user), "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials", "danger")

    return render_template("admin_login.html")

@bp.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out.", "success")
    return redirect(url_for("auth.login"))
