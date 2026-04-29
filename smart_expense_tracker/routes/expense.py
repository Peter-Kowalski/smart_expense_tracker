from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from config import Config

expense = Blueprint("expense", __name__)


def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


# -----------------------------------
# Add Expense
# -----------------------------------
@expense.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get logged-in user's user_id
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

    # Get all categories for dropdown
    cursor.execute("SELECT category_id, category_name FROM categories")
    categories = cursor.fetchall()

    if request.method == "POST":
        title = request.form["title"]
        amount = request.form["amount"]
        category_id = request.form["category_id"]
        expense_date = request.form["expense_date"]

        cursor.execute("""
            INSERT INTO expenses
            (user_id, category_id, title, amount, expense_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            category_id,
            title,
            amount,
            expense_date
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("expense.view_expenses"))

    cursor.close()
    conn.close()

    return render_template(
        "add_expense.html",
        categories=categories
    )


# -----------------------------------
# View Expenses
# -----------------------------------
@expense.route("/expenses")
def view_expenses():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    cursor.execute("""
        SELECT 
            e.expense_id,
            e.title,
            e.amount,
            e.expense_date,
            c.category_name
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.category_id
        WHERE e.user_id = %s
        ORDER BY e.expense_date DESC
    """, (user_id,))

    user_expenses = cursor.fetchall()

    total_spent = sum(
        float(item["amount"])
        for item in user_expenses
    )

    average_expense = (
        total_spent / len(user_expenses)
        if user_expenses else 0
    )

    top_category = "None"

    if user_expenses:
        category_count = {}

        for item in user_expenses:
            cat = item["category_name"]

            if cat in category_count:
                category_count[cat] += 1
            else:
                category_count[cat] = 1

        top_category = max(
            category_count,
            key=category_count.get
        )

    cursor.close()
    conn.close()

    return render_template(
        "expenses.html",
        expenses=user_expenses,
        total_spent=round(total_spent, 2),
        average_expense=round(average_expense, 2),
        top_category=top_category
    )


# -----------------------------------
# Delete Expense
# -----------------------------------
@expense.route("/delete-expense/<int:expense_id>")
def delete_expense(expense_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE expense_id = %s",
        (expense_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("expense.view_expenses"))