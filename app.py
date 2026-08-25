import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import get_db_connection, get_cursor, new_conn_and_cursor, PH


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret")
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file_storage, prefix=""):
    """Save an uploaded file and return the filename (stored in DB)."""
    if not file_storage or not file_storage.filename:
        return ""
    filename = secure_filename(file_storage.filename)
    if not filename or not allowed_file(filename):
        return ""
    unique_name = f"{prefix}{filename}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
    return unique_name


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    voter_id = request.form.get("voterid")
    password = request.form.get("password")

    if not voter_id or not password:
        flash("Please enter both voter ID and password.", "error")
        return redirect("/")

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(
            f"SELECT * FROM users WHERE voter_id={PH}",
            (voter_id,),
        )
        user = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not user or not check_password_hash(user["password"], password):
        flash("Invalid voter ID or password.", "error")
        return redirect("/")

    session["user"] = user["voter_id"]
    session["role"] = user["role"]
    session["name"] = user["name"]

    flash(f"Welcome back, {user['name']}!", "success")

    if user["role"] == "Admin":
        return redirect("/admin")
    return redirect("/dashboard")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form["name"]
    voter_id = request.form["voter_id"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    role = request.form["role"]

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect("/register")

    if len(password) < 4:
        flash("Password must be at least 4 characters.", "error")
        return redirect("/register")

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(
            f"INSERT INTO users (voter_id, name, password, role) VALUES ({PH}, {PH}, {PH}, {PH})",
            (voter_id, name, generate_password_hash(password), role),
        )
        conn.commit()
        flash("Registration successful! Please log in.", "success")
    except Exception:
        conn.rollback()
        flash("Registration failed — voter ID may already exist.", "error")
    finally:
        cur.close()
        conn.close()

    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    voter_id = session["user"]

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(f"SELECT * FROM users WHERE voter_id={PH}", (voter_id,))
        user = cur.fetchone()

        cur.execute("SELECT * FROM candidates ORDER BY id")
        candidates = cur.fetchall()

        cur.execute(f"SELECT has_voted FROM users WHERE voter_id={PH}", (voter_id,))
        has_voted = cur.fetchone()["has_voted"]
    finally:
        cur.close()
        conn.close()

    return render_template(
        "dashboard.html",
        candidates=candidates,
        role=user["role"],
        has_voted=has_voted,
        user_name=user["name"],
    )


@app.route("/vote", methods=["POST"])
def vote():
    if "user" not in session:
        return redirect("/")

    voter_id = session["user"]
    candidate_id = request.form["candidate_id"]

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(f"SELECT has_voted FROM users WHERE voter_id={PH}", (voter_id,))
        user = cur.fetchone()

        if user and user["has_voted"] == 1:
            flash("You have already voted!", "error")
            return redirect("/dashboard")

        cur.execute(
            f"UPDATE candidates SET votes = votes + 1 WHERE id={PH}",
            (candidate_id,),
        )

        cur.execute(
            f"UPDATE users SET has_voted = 1 WHERE voter_id={PH}",
            (voter_id,),
        )

        conn.commit()
        flash("Your vote has been recorded!", "success")
    finally:
        cur.close()
        conn.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")


@app.route("/results")
def results():
    conn, cur = new_conn_and_cursor()
    try:
        cur.execute("SELECT * FROM candidates ORDER BY votes DESC")
        candidates = cur.fetchall()

        total_votes = sum(c["votes"] for c in candidates)
    finally:
        cur.close()
        conn.close()
    return render_template("results.html", candidates=candidates, total_votes=total_votes)


# ── Admin routes ──────────────────────────────────────────────────────────


@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")
    if session.get("role") != "Admin":
        return "Access Denied"

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute("SELECT * FROM candidates ORDER BY id")
        candidates = cur.fetchall()

        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role='Voter'")
        total_voters = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE has_voted=1")
        total_voted = cur.fetchone()["cnt"]

        total_votes = sum(c["votes"] for c in candidates)

        turnout = round((total_voted / total_voters * 100), 1) if total_voters > 0 else 0
    finally:
        cur.close()
        conn.close()

    return render_template(
        "admin_dashboard.html",
        candidates=candidates,
        total_voters=total_voters,
        total_voted=total_voted,
        total_votes=total_votes,
        turnout=turnout,
    )


@app.route("/add_candidate", methods=["GET", "POST"])
def add_candidate():
    if "user" not in session or session.get("role") != "Admin":
        return redirect("/")

    if request.method == "GET":
        return render_template("add_candidate.html")

    name = request.form["name"]
    bio = request.form.get("bio", "")
    photo = request.files.get("photo")
    photo_name = save_upload(photo, prefix="candidate_") if photo else ""

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(
            f"INSERT INTO candidates (name, bio, photo) VALUES ({PH}, {PH}, {PH})",
            (name, bio, photo_name),
        )
        conn.commit()
        flash(f"Candidate '{name}' added successfully!", "success")
    finally:
        cur.close()
        conn.close()

    return redirect("/admin")


@app.route("/candidate/<int:candidate_id>/photo", methods=["POST"])
def upload_candidate_photo(candidate_id):
    """Admin: upload or replace a candidate's photo."""
    if "user" not in session or session.get("role") != "Admin":
        return redirect("/")

    photo = request.files.get("photo")
    if not photo or not photo.filename:
        return redirect("/admin")

    photo_name = save_upload(photo, prefix="candidate_")
    if not photo_name:
        flash("Invalid file type. Please upload PNG, JPG, GIF, or WebP.", "error")
        return redirect("/admin")

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(
            f"UPDATE candidates SET photo={PH} WHERE id={PH}",
            (photo_name, candidate_id),
        )
        conn.commit()
        flash("Photo updated successfully!", "success")
    finally:
        cur.close()
        conn.close()

    return redirect("/admin")


@app.route("/candidate/<int:candidate_id>/delete", methods=["POST"])
def delete_candidate(candidate_id):
    """Admin: delete a candidate and their photo file."""
    if "user" not in session or session.get("role") != "Admin":
        return redirect("/")

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute(f"SELECT name, photo FROM candidates WHERE id={PH}", (candidate_id,))
        row = cur.fetchone()
        if row and row["photo"]:
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], row["photo"])
            if os.path.exists(photo_path):
                os.remove(photo_path)

        cur.execute(f"DELETE FROM candidates WHERE id={PH}", (candidate_id,))
        conn.commit()
        if row:
            flash(f"Candidate '{row['name']}' has been removed.", "info")
    finally:
        cur.close()
        conn.close()

    return redirect("/admin")


@app.route("/reset_votes", methods=["POST"])
def reset_votes():
    """Admin: reset all vote counts."""
    if "user" not in session or session.get("role") != "Admin":
        return redirect("/")

    conn, cur = new_conn_and_cursor()
    try:
        cur.execute("UPDATE candidates SET votes = 0")
        cur.execute("UPDATE users SET has_voted = 0")
        conn.commit()
        flash("All votes have been reset.", "info")
    finally:
        cur.close()
        conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
