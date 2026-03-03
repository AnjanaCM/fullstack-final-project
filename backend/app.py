from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()
@app.route("/")
def home():
    return redirect("/login")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            conn.close()
            return "Email already exists!"

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE email=? AND password=?",
                       (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]  # store name
            return redirect("/dashboard")
        else:
            return "Invalid email or password!"

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html",
                           user=session["user"],
                           students=students)
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Students (name, email) VALUES (?, ?)",
                       (name, email))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add.html")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        cursor.execute("UPDATE Students SET name=?, email=? WHERE id=?",
                       (name, email, id))
        conn.commit()
        conn.close()
        return redirect("/dashboard")

    cursor.execute("SELECT * FROM Students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template("edit.html", student=student)
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
if __name__ == "__main__":
    app.run(debug=True)