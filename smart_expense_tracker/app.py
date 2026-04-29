from flask import Flask, render_template, session, redirect, url_for
from config import Config

from routes.auth import auth
from routes.expense import expense
from routes.analytics import analytics
from routes.prediction import prediction

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(expense)
app.register_blueprint(analytics)
app.register_blueprint(prediction)


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    import mysql.connector

    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

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

    # Summary values
    cursor.execute("""
        SELECT
            IFNULL(SUM(amount), 0) AS total_spent,
            COUNT(*) AS total_transactions,
            IFNULL(AVG(amount), 0) AS average_expense
        FROM expenses
        WHERE user_id = %s
    """, (user_id,))

    summary = cursor.fetchone()

    total_spent = float(summary["total_spent"])
    total_transactions = summary["total_transactions"]
    average_expense = float(summary["average_expense"])

    # Recent expenses
    cursor.execute("""
        SELECT
            title,
            amount,
            expense_date
        FROM expenses
        WHERE user_id = %s
        ORDER BY expense_date DESC
        LIMIT 5
    """, (user_id,))

    recent_expenses = cursor.fetchall()

    monthly_budget = 10000
    remaining_budget = monthly_budget - total_spent
    predicted_expense = round(average_expense * 1.10, 2)

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        total_spent=round(total_spent, 2),
        average_expense=round(average_expense, 2),
        remaining_budget=round(remaining_budget, 2),
        predicted_expense=predicted_expense,
        total_transactions=total_transactions,
        recent_expenses=recent_expenses
    )


if __name__ == "__main__":
    app.run(debug=True)