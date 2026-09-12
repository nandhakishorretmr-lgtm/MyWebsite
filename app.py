from flask import Flask, render_template, request, session, redirect
import sqlite3

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "mytech-secret-key"

DATABASE = "messages.db"


# -------------------------
# Database setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


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

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return render_template("success.html")


# -------------------------
# Admin login
# -------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password")

        if password == "MyTech@2026":

            # Remember that the admin is logged in
            session["admin_logged_in"] = True

            return redirect("/messages")

        return "Wrong password!"

    return render_template("admin.html")


# -------------------------
# Private messages page
# -------------------------
@app.route("/messages")
def messages():

    # Check if admin is logged in
    if not session.get("admin_logged_in"):
        return redirect("/admin")

    conn = sqlite3.connect(DATABASE)

    messages = conn.execute(
        "SELECT id, name, email, message FROM messages ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "messages.html",
        messages=messages
    )


# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/admin")


# -------------------------
# Start Flask
# -------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)