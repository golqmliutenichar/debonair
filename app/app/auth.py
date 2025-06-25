"""
Simple username/password login against the existing *admin_users* table.
No ORM models; raw SQL is good enough here.
"""
import os
from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import text
from . import db, login_mgr, AdminUser

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")

        sql = text("SELECT id, username, password_hash, is_superadmin "
                   "FROM admin_users WHERE username=:u AND is_active=1")
        row = db.session.execute(sql, {"u": username}).fetchone()

        if row and check_password_hash(row.password_hash, password):
            user = AdminUser((row.id, row.username, row.is_superadmin))
            login_user(user, remember=True, duration=timedelta(days=30))
            flash("Welcome back ✌", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("admin_login.html")


@bp.get("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
