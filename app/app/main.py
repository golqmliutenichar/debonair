# app/main.py
from datetime import datetime
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app  # ← added current_app
)
import pymysql

bp = Blueprint("main", __name__)

# ---------- helpers ----------
SPECIALS = {
    "Monday":  "Buy one latte, get one free croissant.",
    "Tuesday": "Free refills on espresso all day.",
    "Wednesday": "20 % off any specialty tea.",
    "Thursday":  "Trivia Night—get a free cookie if you win!",
    "Friday":    "Live DJ 🎧 + happy hour on energy drinks.",
    "Saturday":  "Bring a friend—฿1 off on any drip coffee.",
    "Sunday":    "Family brunch: 3 pancakes + coffee for $7."
}

def daily_special() -> str:
    return SPECIALS.get(datetime.utcnow().strftime("%A"), "")

def get_db():
    return pymysql.connect(
        host     = os.getenv("DB_HOST"),
        port     = int(os.getenv("DB_PORT", 3306)),
        user     = os.getenv("DB_USER"),
        password = os.getenv("DB_USER_PWD"),
        database = os.getenv("DB_NAME"),
        autocommit=True,
    )

# ---------- public pages ----------
@bp.get("/")
def home():
    try:
        return render_template(
            "index.html",
            page="home",
            daily_special=daily_special()
        )
    except Exception:
        current_app.logger.exception("Home page failed")
        return "Internal Server Error", 500

@bp.get("/pricing")
def pricing():
    plans = [
        {"name":"Hourly Pass",  "price":"$5/hr",  "details":"Any seat; pay by the hour"},
        {"name":"Day Pass",     "price":"$20",    "details":"Unlimited 8 a-m – 8 p-m"},
        {"name":"Weekly Pass",  "price":"$75",    "details":"Save 10 %, 7 days"},
        {"name":"Monthly Pass", "price":"$250",   "details":"Priority booking"},
    ]
    try:
        return render_template("pricing.html", page="pricing", plans=plans)
    except Exception:
        current_app.logger.exception("Pricing page failed")
        return "Internal Server Error", 500

@bp.get("/stations")
def stations():
    stations = [
        {"title":"Standard Desk",  "desc":"24'' monitor, comfy chair"},
        {"title":"Gaming Rig",     "desc":"RTX 4070, 165 Hz display"},
        {"title":"Quiet Pod",      "desc":"Sound-proof, whiteboard walls"},
        {"title":"Dedicated Station", "desc":"Dual monitors, locker"},
    ]
    return render_template("stations.html", page="stations", station_list=stations)

# ---------- contact ----------
@bp.get("/contact")
def contact_get():
    return render_template("contact.html", page="contact")

@bp.post("/contact")
def contact_post():
    name    = request.form.get("name","").strip()
    email   = request.form.get("email","").strip()
    message = request.form.get("message","").strip()

    if not all([name, email, message]):
        flash("All fields are required.", "warning")
        return redirect(url_for("main.contact_get"))

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO contact (name,email,message)
                VALUES (%s,%s,%s)
                """,
                (name, email, message)
            )
        flash("Thanks {}! We’ll get back to you shortly.".format(name), "success")
    except Exception:
        current_app.logger.exception("Failed to insert contact form")
        flash("Server error—please try again later.", "danger")

    return redirect(url_for("main.contact_get"))  # ← endpoint is main.contact_get

# ---------- reserve ----------
@bp.route("/reserve", methods=["GET","POST"])
def reserve():
    if request.method == "POST":
        name       = request.form.get("name","").strip()
        email      = request.form.get("email","").strip()
        station_id = request.form.get("station_id","").strip()

        if not all([name, email, station_id]):
            flash("All fields are required.", "warning")
            return redirect(url_for("main.reserve"))

        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO reservations (name,email,station_id,timeslot)
                    VALUES (%s,%s,%s,NOW())
                    """,
                    (name, email, station_id)      # ← no stray comma!
                )
            flash("Reservation saved—see you soon!", "success")
        except Exception:
            current_app.logger.exception("Reservation insert failed")
            flash("Server error—please try again.", "danger")

        return redirect(url_for("main.reserve"))

    # GET
    return render_template("reserve.html", page="reserve")
