from flask import Blueprint, render_template, session, redirect, url_for
import mysql.connector
from config import Config

analytics = Blueprint("analytics", __name__)


def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


@analytics.route("/analytics")
def analytics_page():
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

    # Total expense + total transactions + average
    cursor.execute("""
        SELECT 
            IFNULL(SUM(amount), 0) AS total_expense,
            COUNT(*) AS total_count,
            IFNULL(AVG(amount), 0) AS average_expense
        FROM expenses
        WHERE user_id = %s
    """, (user_id,))

    summary = cursor.fetchone()

    total_expense = float(summary["total_expense"])
    total_count = summary["total_count"]
    average_expense = float(summary["average_expense"])

    # Category-wise summary
    cursor.execute("""
        SELECT 
            c.category_name,
            SUM(e.amount) AS total_amount
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.category_id
        WHERE e.user_id = %s
        GROUP BY c.category_name
        ORDER BY total_amount DESC
    """, (user_id,))

    category_summary = cursor.fetchall()

    # Top category
    top_category = (
        category_summary[0]["category_name"]
        if category_summary else "None"
    )

    cursor.close()
    conn.close()

    return render_template(
        "analytics.html",
        total_expense=round(total_expense, 2),
        total_count=total_count,
        average_expense=round(average_expense, 2),
        top_category=top_category,
        category_summary=category_summary
    )