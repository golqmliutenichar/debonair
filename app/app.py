from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret")   # ← NEW: comes from .env

DB_URL = (
	f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
	f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL

# Make “now” available inside any template (for {{ now().year }} in footer)
@app.context_processor
def inject_now():
    return {"now": datetime.utcnow}


# 1) Home page: show hero + daily special
SPECIALS = {
    "Monday":    "Buy one latte, get a free croissant.",
    "Tuesday":   "Free refills on espresso all day.",
    "Wednesday": "20% off any specialty tea.",
    "Thursday":  "Trivia Night—get a free cookie if you win!",
    "Friday":    "Live DJ 6–9pm + happy hour on energy drinks.",
    "Saturday":  "Bring a friend—2‐for‐1 on any drip coffee.",
    "Sunday":    "Family brunch: 3 pancakes + coffee for $7."
}

@app.get("/health")
def health():
	return {"status": "ok"}, 200

@app.route("/", methods=["GET"])
def home():
    today = datetime.now().strftime("%A")
    daily_special = SPECIALS.get(today, "")
    return render_template(
        "index.html",
        page="home",
        daily_special=daily_special
    )


# 2) Pricing page
@app.route("/pricing", methods=["GET"])
def pricing():
    plans = [
        {"name": "Hourly Pass",  "price": "$5/hr",   "details": "Access any seat; pay by the hour."},
        {"name": "Day Pass",     "price": "$20/day", "details": "Unlimited access 8am–8pm."},
        {"name": "Weekly Pass",  "price": "$75/week","details": "7 days unlimited; save 10%."},
        {"name": "Monthly Pass", "price": "$250/mo", "details": "All-access; includes priority booking."}
    ]
    return render_template("pricing.html", page="pricing", plans=plans)


# 3) Stations page
@app.route("/stations", methods=["GET"])
def stations():
    station_list = [
        {
            "title": "Standard Desk",
            "description": "Comfortable chair + 24″ monitor—ideal for casual browsing.",
            "image": None  # could become "images/desk1.jpg"
        },
        {
            "title": "Dedicated Station",
            "description": "24/7 reserved station w/dual monitors, ergonomic chair, locker.",
            "image": None
        },
        {
            "title": "Gaming Rig",
            "description": "High-end PC (RTX 4070), mechanical keyboard, 165Hz monitor.",
            "image": None
        },
        {
            "title": "Quiet Pod",
            "description": "Sound‐proof pod for focused work or recording; whiteboard walls.",
            "image": None
        }
    ]
    return render_template("stations.html", page="stations", station_list=station_list)


# 4) Contact page (GET shows form, POST handles submission)
@app.route("/contact", methods=["GET"])
def contact_get():
    return render_template("contact.html", page="contact")


@app.route("/contact", methods=["POST"])
def contact_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("All fields are required.", "warning")
        return redirect(url_for("contact_get"))

    # (Later you could store the message in a DB or send an email.)
    flash(f"Thanks {name}! We received your message.", "success")
    return redirect(url_for("contact_get"))


# 5) (Optional) “Reserve a Station” page (just a placeholder for now)
@app.route("/reserve", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        name       = request.form.get("name", "").strip()
        email      = request.form.get("email", "").strip()
        station_id = request.form.get("station_id", "").strip()

        if not name or not email or not station_id:
            flash("All fields are required to reserve a station.", "warning")
            return redirect(url_for("reserve"))

        flash(f"Thank you, {name}! Your reservation for station #{station_id} has been received.", "success")
        return redirect(url_for("reserve"))

    # if GET:
    return render_template("reserve.html", page="reserve")
if __name__ == "__main__":
    # Starts Flask’s dev server at http://127.0.0.1:5000
    app.run(debug=True, port=5000)
