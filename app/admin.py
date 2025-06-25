from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint("admin", __name__)

@bp.get("/")
@login_required
def dashboard():
    return render_template(
        "admin_dashboard.html",
        admin=current_user.username,
        now=datetime.utcnow()
    )
