from flask import Blueprint, render_template, session, redirect, url_for
import mysql.connector
from config import Config

prediction = Blueprint("prediction", __name__)


def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


@prediction.route("/prediction")
def prediction_page():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get logged-in user_id
    cursor.execute(
        "SELECT user_id FROM users WHERE full_name = %s",
        (session["user"],)
    )
    user_data = cursor.fetchone()

    if not user_data:
        cursor.close()
        conn.close()
        return "User not found ❌"

    user_id = user_data["user_id"]

    # Get average expense
    cursor.execute("""
        SELECT 
            IFNULL(AVG(amount), 0) AS average_expense
        FROM expenses
        WHERE user_id = %s
    """, (user_id,))

    result = cursor.fetchone()

    average_expense = float(result["average_expense"])

    # Simple prediction logic
    predicted_value = round(average_expense * 1.10, 2)

    cursor.close()
    conn.close()

    return render_template(
        "prediction.html",
        predicted_value=predicted_value,
        average_expense=round(average_expense, 2)
    )