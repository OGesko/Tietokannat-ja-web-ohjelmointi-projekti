"""functions for the webapp"""
from datetime import datetime
from sqlalchemy import text
from app import db

def check_balance(balance, warning_threshold=50.0):
    """Check if the balance is nearing zero and return a warning message."""
    if balance < warning_threshold:
        return f"Warning: Your account balance is low ({balance:.2f})"
    return None

def calculate_balance(account_id):
    """Calculate the balance for an account."""
    # Get the initial account balance
    initial_balance_sql = text('SELECT balance FROM "account" WHERE id = :account_id')
    initial_balance_result = db.session.execute(initial_balance_sql, {"account_id": account_id})
    initial_balance = initial_balance_result.scalar() or 0

    # Get the total amount of expenses (transactions) for the account
    expenses_sql = text('''
        SELECT SUM(amount) AS total_expenses
        FROM "transaction"
        WHERE account_id = :account_id
    ''')
    expenses_result = db.session.execute(expenses_sql, {"account_id": account_id})
    total_expenses = expenses_result.scalar() or 0

    # Calculate the balance
    balance = initial_balance - total_expenses
    return balance

def calculate_spent_this_month(account_id):
    """Calculate spent this month"""
    transactions_sql = text('''
        SELECT * FROM "transaction"
        WHERE account_id = :account_id
        AND EXTRACT(MONTH FROM timestamp) = :month
        ''')
    transactions_result = db.session.execute(transactions_sql,
    {"account_id": account_id, "month": datetime.now().month})

    transactions = transactions_result.fetchall()
    spent_this_month = sum(t.amount for t in transactions)

    return spent_this_month
