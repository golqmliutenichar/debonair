"""
App-factory — no ORM models; we still init SQLAlchemy so we can run
raw SQL through its connection pool, and to give Flask-Login a session.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text

db = SQLAlchemy()
login_mgr = LoginManager()
login_mgr.login_view = "auth.login"     # where @login_required redirects


class AdminUser:                         # *minimal* wrapper for flask-login
    def __init__(self, row):
        self.id, self.username, self.is_superadmin = row

    # --- Flask-Login helpers ---
    def is_active(self):       return True
    def is_authenticated(self):return True
    def is_anonymous(self):    return False
    def get_id(self):          return str(self.id)


@login_mgr.user_loader                # runs every request that has a session
def load_user(user_id: str):
    row = db.session.execute(
        text("SELECT id, username, is_superadmin "
             "FROM admin_users WHERE id = :uid AND is_active = 1"),
        {"uid": user_id}
    ).fetchone()
    return AdminUser(row) if row else None


# ---------- factory -------------
def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    # ---- core config ----
    app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_USER_PWD']}"
        f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # ----------------------

    db.init_app(app)
    login_mgr.init_app(app)

    # blueprints ----------
    from .main  import bp as main_bp
    from .auth  import bp as auth_bp
    from .admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,  url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
