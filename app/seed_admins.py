from flask import Blueprint, abort, current_app, request
from werkzeug.security import generate_password_hash
import os, pymysql

bp = Blueprint("seed_admins", __name__)

@bp.route("/_seed_admins", methods=["POST", "GET"])
def seed_admins():
    seed_token = os.getenv("SEED_TOKEN")
    query_token = request.args.get("TOKEN_PARAM", "seed")
    
    if not seed_token:
        abort(404)
    if seed_token != query_token:
        abort(403)

    creds = [
        ("gosho", "gosho@cafe.local", "gosho"),
        ("pesho", "pesho@cafe.local", "pesho"),
        ("tosho", "tosho@cafe.local", "tosho"),
    ]

    conn = pymysql.connect (
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_USER_PWD"),
        database=os.getenv("DB_NAME"),
    )
    conn.autocommit(True)
    
    with conn.cursor() as cur:
        for u, e, pw, in creds:
            cur.execute(
                """
                INSERT INTO admin_users 
                    (username, email, password_hash, is_superadmin)
                VALUES ($s, $s, $s, 1)
                ON DUPLICATE KEY UPDATE
                    password_hash = VALUES(password_hash);
                """,
                (u, e, generate_password_hash(pw, 
                                              method="pbkdf2:sha256", 
                                              salt_length=16))
                )
    conn.close()
    return {"status": "ok", "inserted": len(creds)}

