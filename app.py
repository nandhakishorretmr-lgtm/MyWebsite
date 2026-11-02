from flask import Flask, render_template, request, session, redirect, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Secret key for login sessions
# Set SECRET_KEY as an environment variable on Render.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this")

DATABASE = os.path.join(app.root_path, "messages.db")


# -------------------------
# Google Search Console verification
# -------------------------
@app.route("/google5dae8ab8a16fd70d.html")
def google_verification():
    return send_from_directory(
        app.root_path,
        "google5dae8ab8a16fd70d.html"
    )


# -------------------------
# Robots.txt for Google
# -------------------------
@app.route("/robots.txt")
def robots():
    return """User-agent: *
Allow: /

Sitemap: https://nandhakishor-mytech.onrender.com/sitemap.xml
""", 200, {"Content-Type": "text/plain; charset=utf-8"}


# -------------------------
# Sitemap for Google Search Console
# -------------------------
@app.route("/sitemap.xml")
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://nandhakishor-mytech.onrender.com/</loc>
    </url>
</urlset>
""", 200, {"Content-Type": "application/xml; charset=utf-8"}


# -------------------------
# Database setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        conn.commit()
    finally:
        conn.close()


# Create the table when Flask or Gunicorn loads this file.
init_db()


# -------------------------
# Home page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# TechFixHub page
# -------------------------
@app.route("/techfixhub")
def techfixhub():
    return render_template("techfixhub.html")


# -------------------------
# Contact form
# -------------------------
@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        return "Please fill in all fields.", 400

    conn = sqlite3.connect(DATABASE)

    try:
        conn.execute(
            "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )
        conn.commit()
    finally:
        conn.close()

    return render_template("success.html")


# -------------------------
# Admin login
# -------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")

        # Set ADMIN_PASSWORD on Render before using this publicly.
        if password == os.environ.get("ADMIN_PASSWORD", ""):
            session["admin_logged_in"] = True
            return redirect("/messages")

        return "Wrong password!", 401

    return render_template("admin.html")


# -------------------------
# Private messages page
# -------------------------
@app.route("/messages")
def messages():
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect(DATABASE)

    try:
        stored_messages = conn.execute(
            "SELECT id, name, email, message FROM messages ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "messages.html",
        messages=stored_messages
    )


# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


# -------------------------
# Start Flask locally
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")