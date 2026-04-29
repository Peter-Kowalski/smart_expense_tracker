from flask import Blueprint, render_template, request, redirect, url_for, session
from models.db import get_db_connection

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO users (full_name, email, password)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, email, password))
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session["user"] = user["full_name"]
            session["user_id"] = user["user_id"]
            return redirect(url_for("dashboard"))

        return "Invalid Login Credentials ❌"

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))