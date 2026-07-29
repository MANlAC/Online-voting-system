from flask import Flask, render_template, request, redirect, session
from database import cursor, db



app = Flask(__name__)
app.secret_key = "voting_secret_key"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    voter_id = request.form["voterid"]
    password = request.form["password"]

    

    cursor.execute(
        "SELECT * FROM users WHERE voter_id=%s AND password=%s",
        (voter_id, password)
    )

    user = cursor.fetchone()

    if user:
        session["user"] = user["voter_id"]
        session["role"] = user["role"]

    if user["role"] == "Admin":
        return redirect("/admin")
    else:
        return redirect("/dashboard")

    return "Invalid credentials"
    
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    name = request.form["name"]
    voter_id = request.form["voter_id"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    address = request.form["address"]
    role = request.form["role"]

    photo = request.files["photo"]

    if password != confirm_password:
        return "Passwords do not match"

    filename = photo.filename
    photo.save("uploads/" + filename)

    cursor.execute("""
        INSERT INTO users (voter_id, name, password, role)
        VALUES (%s, %s, %s, %s)
    """, (voter_id, name, password, role))

    db.commit()

    return redirect("/")    


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    voter_id = session["user"]

    cursor.execute("SELECT role FROM users WHERE voter_id=%s", (voter_id,))
    role = cursor.fetchone()

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    return render_template(
        "dashboard.html",
        candidates=candidates,
        role=role["role"]
    )


@app.route("/vote", methods=["POST"])
def vote():

    if "user" not in session:
        return redirect("/")

    voter_id = session["user"]
    candidate_id = request.form["candidate_id"]

    cursor.execute("SELECT has_voted FROM users WHERE voter_id=%s", (voter_id,))
    user = cursor.fetchone()

    if user and user["has_voted"] == 1:
        return "You have already voted!"

    cursor.execute(
        "UPDATE candidates SET votes = votes + 1 WHERE id=%s",
        (candidate_id,)
    )

    cursor.execute(
        "UPDATE users SET has_voted = 1 WHERE voter_id=%s",
        (voter_id,)
    )

    db.commit()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")




@app.route("/results")
def results():

    cursor.execute("SELECT * FROM candidates ORDER BY votes DESC")
    candidates = cursor.fetchall()

    return render_template("results.html", candidates=candidates)    


@app.route("/add_candidate", methods=["GET", "POST"])
def add_candidate():

    if request.method == "GET":
        return render_template("add_candidate.html")

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
    app.run(debug=True)