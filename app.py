import os

from flask import Flask, redirect, render_template, request, session
from werkzeug.utils import secure_filename

from database import cursor, db


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    voter_id = request.form.get("voterid")
    password = request.form.get("password")

    if not voter_id or not password:
        return render_template("login.html", error="Invalid credentials")

    if cursor is None:
        return render_template("login.html", error="Database is not available right now")

    cursor.execute(
        "SELECT * FROM users WHERE voter_id=? AND password=?",
        (voter_id, password),
    )
    user = cursor.fetchone()

    if not user:
        return render_template("login.html", error="Invalid credentials")

    session["user"] = user["voter_id"]
    session["role"] = user["role"]

    if user["role"] == "Admin":
        return redirect("/admin")
    return redirect("/dashboard")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if cursor is None or db is None:
        return render_template("register.html", error="Database is not available right now")

    name = request.form["name"]
    voter_id = request.form["voter_id"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    role = request.form["role"]
    photo = request.files.get("photo")

    if password != confirm_password:
        return render_template("register.html", error="Passwords do not match")

    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    cursor.execute(
        """
        INSERT INTO users (voter_id, name, password, role)
        VALUES (%s, %s, %s, %s)
        """,
        (voter_id, name, password, role),
    )
    db.commit()

    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    if cursor is None or db is None:
        return render_template("login.html", error="Database is not available right now")

    voter_id = session["user"]

    cursor.execute("SELECT role FROM users WHERE voter_id=?", (voter_id,))
    role = cursor.fetchone()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    return render_template("dashboard.html", candidates=candidates, role=role["role"])


@app.route("/vote", methods=["POST"])
def vote():
    if "user" not in session:
        return redirect("/")

    if cursor is None or db is None:
        return render_template("login.html", error="Database is not available right now")

    voter_id = session["user"]
    candidate_id = request.form["candidate_id"]

    cursor.execute("SELECT has_voted FROM users WHERE voter_id=?", (voter_id,))
    user = cursor.fetchone()

    if user and user["has_voted"] == 1:
        return "You have already voted!"

    cursor.execute(
        "UPDATE candidates SET votes = votes + 1 WHERE id=?",
        (candidate_id,),
    )

    cursor.execute(
        "UPDATE users SET has_voted = 1 WHERE voter_id=?",
        (voter_id,),
    )

    db.commit()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect("/")


@app.route("/results")
def results():
    if cursor is None or db is None:
        return render_template("login.html", error="Database is not available right now")
    cursor.execute("SELECT * FROM candidates ORDER BY votes DESC")
    candidates = cursor.fetchall()
    return render_template("results.html", candidates=candidates)


@app.route("/add_candidate", methods=["GET", "POST"])
def add_candidate():
    if request.method == "GET":
        return render_template("add_candidate.html")

    if cursor is None or db is None:
        return render_template("login.html", error="Database is not available right now")

    name = request.form["name"]
    cursor.execute("INSERT INTO candidates (name) VALUES (%s)", (name,))
    db.commit()
    return redirect("/dashboard")


@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")

    if session.get("role") != "Admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)