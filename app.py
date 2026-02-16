from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pickle
import os
import urllib.parse

from db import init_db, DB_NAME
from email_utils import send_appreciation_email

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "vitaldrop-secret"
init_db()

# ---------- Load ML model ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
model = None

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ ML model loaded")
else:
    print("⚠️ model.pkl not found, using rules fallback")


# ---------- Camps table (auto-create, safe) ----------
def ensure_camps_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS camps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camp_name TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            google_maps_link TEXT,
            active_status INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

ensure_camps_table()


# ---------- Donors DB helpers ----------
def save_donor(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO donors
        (name, email, phone, blood_group, recency, frequency, monetary, time_months, prediction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["email"], data["phone"], data["blood_group"],
        data["recency"], data["frequency"], data["monetary"], data["time_months"],
        data["prediction"]
    ))
    conn.commit()
    conn.close()


def fetch_donors():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id, name, email, phone, blood_group,
            recency, frequency,
            prediction,
            donated, donated_at,
            created_at
        FROM donors
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------- Camps helpers ----------
def fetch_camps(city="", area=""):
    """
    Smart search:
    - City box me user 'Muradnagar' likhe tab bhi match ho (area me bhi search)
    - Area optional filter
    - Active camps first
    """
    city = (city or "").strip()
    area = (area or "").strip()

    if not city:
        return []

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if area:
        cur.execute("""
            SELECT id, camp_name, city, area, address, phone, email, google_maps_link, active_status
            FROM camps
            WHERE (lower(city) = lower(?) OR lower(area) LIKE lower(?))
              AND lower(area) LIKE lower(?)
            ORDER BY active_status DESC, id DESC
        """, (city, f"%{city}%", f"%{area}%"))
    else:
        cur.execute("""
            SELECT id, camp_name, city, area, address, phone, email, google_maps_link, active_status
            FROM camps
            WHERE lower(city) = lower(?)
               OR lower(area) LIKE lower(?)
            ORDER BY active_status DESC, id DESC
        """, (city, f"%{city}%"))

    rows = cur.fetchall()
    conn.close()
    return rows


def build_map_embed(camp_name, city, area, address, google_maps_link=None):
    """
    FREE map preview embed (no API key)
    """
    query_text = " ".join([camp_name or "", address or "", area or "", city or ""]).strip()
    query = urllib.parse.quote_plus(query_text) if query_text else ""
    embed_url = f"https://www.google.com/maps?q={query}&output=embed"
    return embed_url


def build_contact_links(phone, email, camp_name):
    """
    Contact links:
    - tel (call) (mobile pe best)
    - WhatsApp (desktop+mobile reliable)
    - mailto (only if email exists)
    """
    phone_digits = "".join([ch for ch in (phone or "") if ch.isdigit()])

    whatsapp_number = phone_digits
    if len(phone_digits) == 10:
        whatsapp_number = "91" + phone_digits

    wa_msg = f"Hello, I need urgent blood support. I want to contact {camp_name}. Please guide me."
    wa_msg_enc = urllib.parse.quote(wa_msg)

    tel_link = f"tel:{phone_digits}" if phone_digits else None
    wa_link = f"https://api.whatsapp.com/send?phone={whatsapp_number}&text={wa_msg_enc}" if whatsapp_number else None

    mail_link = None
    if email and email.strip():
        subject = urllib.parse.quote("Emergency Blood Requirement - VitalDrop")
        body = urllib.parse.quote(
            f"Hello {camp_name},\n\nI need urgent blood support. Please share availability and process.\n\nThanks"
        )
        mail_link = f"mailto:{email}?subject={subject}&body={body}"

    return tel_link, wa_link, mail_link


# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        blood_group = request.form.get("blood_group", "").strip()

        # safe int parsing
        recency = int(request.form.get("recency") or 0)
        frequency = int(request.form.get("frequency") or 0)
        monetary = int(request.form.get("monetary") or 0)
        time_months = int(request.form.get("time") or 0)

        prob_display = None

        # ---------- Prediction ----------
        if model:
            X_input = [[recency, frequency, monetary, time_months]]
            prob = model.predict_proba(X_input)[0][1]
            prob_display = round(prob * 100, 1)

            if prob >= 0.70:
                prediction = "High Donation Likelihood"
            elif prob >= 0.40:
                prediction = "Medium Donation Likelihood"
            else:
                prediction = "Low Donation Likelihood"
        else:
            if recency <= 3 and frequency >= 2:
                prediction = "High Donation Likelihood"
            elif recency <= 6 and frequency >= 1:
                prediction = "Medium Donation Likelihood"
            else:
                prediction = "Low Donation Likelihood"

        save_donor({
            "name": name,
            "email": email,
            "phone": phone,
            "blood_group": blood_group,
            "recency": recency,
            "frequency": frequency,
            "monetary": monetary,
            "time_months": time_months,
            "prediction": prediction
        })

        return render_template(
            "result.html",
            prediction=prediction,
            name=name,
            blood_group=blood_group,
            recency=recency,
            frequency=frequency,
            monetary=monetary,
            time=time_months,
            prob=prob_display
        )

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    donors = fetch_donors()
    return render_template("dashboard.html", donors=donors)


@app.route("/mark-donated/<int:donor_id>", methods=["POST"])
def mark_donated(donor_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT name, email, donated FROM donors WHERE id = ?", (donor_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        flash("Donor not found ❌")
        return redirect(url_for("dashboard"))

    name, email, donated = row
    donated = int(donated)

    if donated == 1:
        conn.close()
        flash("Already marked as donated ✅")
        return redirect(url_for("dashboard"))

    cur.execute(
        "UPDATE donors SET donated = 1, donated_at = datetime('now') WHERE id = ?",
        (donor_id,)
    )
    conn.commit()
    conn.close()

    try:
        send_appreciation_email(email, name)
        flash(f"Marked donated ✅ Email sent to {email} ✅")
    except Exception as e:
        flash(f"Marked donated ✅ but Email failed: {e}")

    return redirect(url_for("dashboard"))


# ---------- Nearby Camps page ----------
@app.route("/nearby-camps", methods=["GET", "POST"])
def nearby_camps():
    camps = []
    city = ""
    area = ""
    selected_map_embed = None
    selected_camp_name = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        area = request.form.get("area", "").strip()

        if not city:
            flash("Please enter City ❌")
            return render_template("nearby_camps.html", camps=[], city=city, area=area)

        camps_raw = fetch_camps(city=city, area=area)

        for r in camps_raw:
            (cid, camp_name, c_city, c_area, address, phone, email, maps_link, active_status) = r

            map_embed = build_map_embed(
                camp_name=camp_name, city=c_city, area=c_area, address=address, google_maps_link=maps_link
            )

            tel_link, wa_link, mail_link = build_contact_links(phone=phone, email=email, camp_name=camp_name)

            camps.append({
                "id": cid,
                "camp_name": camp_name,
                "city": c_city,
                "area": c_area,
                "address": address,
                "phone": phone,
                "email": email,
                "active_status": active_status,
                "map_embed": map_embed,
                "tel_link": tel_link,
                "wa_link": wa_link,
                "mail_link": mail_link,
            })

        selected_id = request.form.get("selected_camp_id")
        if selected_id:
            for c in camps:
                if str(c["id"]) == str(selected_id):
                    selected_map_embed = c["map_embed"]
                    selected_camp_name = c["camp_name"]
                    break

        if not camps:
            flash("No camps found for this city/area ❌")

    return render_template(
        "nearby_camps.html",
        camps=camps,
        city=city,
        area=area,
        selected_map_embed=selected_map_embed,
        selected_camp_name=selected_camp_name
    )


if __name__ == "__main__":
    app.run(debug=True)
