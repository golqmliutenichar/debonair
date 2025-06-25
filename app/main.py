from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime

bp = Blueprint("main", __name__)

@bp.context_processor
def inject_now():
    return {"now": datetime.utcnow}

SPECIALS = {
    "Monday":    "Buy one latte, get a free croissant.",
    "Tuesday":   "Free refills on espresso all day.",
    "Wednesday": "20 % off any specialty tea.",
    "Thursday":  "Trivia Night – free cookie if you win!",
    "Friday":    "Live DJ 6-9 pm; happy-hour energy drinks.",
    "Saturday":  "2-for-1 drip coffee with a friend.",
    "Sunday":    "Family brunch – 3 pancakes + coffee for $7"
}

@bp.get("/health")
def health():                # used by Docker HEALTHCHECK
    return {"status": "ok"}, 200

@bp.get("/")
def home():
    return render_template(
        "index.html",
        daily_special=SPECIALS.get(datetime.utcnow().strftime("%A"), "")
    )

# ---------- the other static pages -----------
@bp.get("/pricing")
def pricing():
    plans = [
        {"name": "Hourly Pass",  "price": "$5/hr",   "details": "Any seat; pay by the hour"},
        {"name": "Day Pass",     "price": "$20",     "details": "Unlimited 8 am-8 pm"},
        {"name": "Weekly Pass",  "price": "$75",     "details": "Save 10 %, 7 days"},
        {"name": "Monthly Pass", "price": "$250",    "details": "Priority booking"}
    ]
    return render_template("pricing.html", page="pricing", plans=plans)


@bp.get("/stations")
def stations():
    stations = [
        {"title": "Standard Desk",   "desc": "24″ monitor, comfy chair"},
        {"title": "Gaming Rig",      "desc": "RTX 4070, 165 Hz display"},
        {"title": "Quiet Pod",       "desc": "Sound-proof, whiteboard walls"},
        {"title": "Dedicated Station","desc": "Dual monitors, locker"}
    ]
    return render_template("stations.html", page="stations", station_list=stations)


@bp.get("/contact")
def contact_get():
    return render_template("contact.html", page="contact")


@bp.post("/contact")
def contact_post():
    name  = request.form.get("name","").strip()
    email = request.form.get("email","").strip()
    msg   = request.form.get("message","").strip()
    if not all([name, email, msg]):
        flash("All fields are required.", "warning")
    else:
        flash(f"Thanks {name}! We’ll get back to you shortly.", "success")
    return redirect(url_for("main.contact_get"))
