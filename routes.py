from flask import (
    Flask,
    jsonify,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request
)
from sqlalchemy import text
from datetime import timedelta, datetime
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError

from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import app, db,login_manager,bcrypt
#from models import User, Account, Category, Transaction
from forms import login_form, register_form, create_account_form, AddExpenseForm, FilterDataForm

class User(UserMixin):
    def __init__(self, id, username, pwd, admin):
        self.id = id
        self.username = username
        self.pwd_hash = pwd
        self.admin = admin

    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def set_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.pwd_hash, password)
        
    # Required by Flask-Login
    @property
    def is_active(self):
        return True  # Implement your logic to determine if the user is active

    @property
    def is_authenticated(self):
        return True  # Implement your logic to determine if the user is authenticated

    @property
    def is_anonymous(self):
        return False  # Implement your logic to determine if the user is anonymous


@login_manager.user_loader
def load_user(user_id):
    sql = text('SELECT * FROM "user" WHERE id = :id')
    result = db.session.execute(sql, {"id": user_id})
    user = result.fetchone()
    if user:
        return User(user.id, user.username, user.pwd, user.admin)
    else:
        return None

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route("/")
def index():
    return render_template("index.html",title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        if request.method == "POST":
            username = form.username.data
            pwd = form.pwd.data
            sql = text('SELECT * FROM "user" WHERE username = :username')
            result = db.session.execute(sql, {"username": username})
            user = result.fetchone()
            try:
                if user:
                    if check_password_hash(user.pwd, pwd):
                        user_obj = User(user.id, user.username, user.pwd, user.admin)
                        login_user(user_obj)
                        return redirect(url_for('personal'))
                    else:
                        flash("Invalid Username or password!", "danger")
            except Exception as e:
                flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )

# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit() and request.method == "POST":
        pwd = generate_password_hash(form.pwd.data).decode('utf-8')
        username = form.username.data
        try:            
            sql = text('INSERT INTO "user" (username, pwd) VALUES (:username, :pwd)')
            db.session.execute(sql, {"username": username, "pwd": pwd})
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"1. Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"2. Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/personal")
@login_required
def personal():
    sql = text('SELECT * FROM "account" WHERE user_id = :user_id')
    result = db.session.execute(sql, {"user_id": current_user.id})
    accounts = result.fetchall()
    return render_template("personal.html", user=current_user, accounts=accounts)

@app.route("/create_account", methods=("GET", "POST"))
@login_required
def create_account():
    form = create_account_form()
    if form.validate_on_submit() and request.method == "POST":
        name = form.name.data
        balance = form.balance.data
        user_id = current_user.id
        sql = text('INSERT INTO "account" (name, balance, user_id) VALUES (:name, :balance, :user_id)')
        db.session.execute(sql, {"name": name, "balance": balance, "user_id": user_id})
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('personal'))
    return render_template('create_account.html', form=form)

@app.route("/account/<int:account_id>", methods=("GET", "POST"))
@login_required
def account(account_id):
    sql = text('SELECT * FROM "account" WHERE id = :id')
    result = db.session.execute(sql, {"id": account_id})
    account = result.fetchone()
    if account.user_id != current_user.id:
        flash('You do not have access to this account.', 'danger')
        return redirect(url_for('personal_page'))

    add_expense_form = AddExpenseForm()    
    filter_form = FilterDataForm()

    categories_sql = text('SELECT id, name FROM "category"')
    categories_result = db.session.execute(categories_sql)
    categories = [(category.id, category.name) for category in categories_result.fetchall()]

    add_expense_form.category.choices = categories
    filter_form.filter_category.choices = categories

    if request.method == 'POST' and add_expense_form.validate_on_submit():
        description = add_expense_form.description.data
        amount = float(add_expense_form.amount.data)
        category_name = add_expense_form.category.data
        new_category = add_expense_form.new_category.data
        recurring = 'recurring' in add_expense_form

        category_sql = text('SELECT * FROM "category" WHERE name = :name')
        category_result = db.session.execute(category_sql, {"name": category_name})
        category = category_result.fetchone()

        if not category and new_category:
            insert_category_sql = text('INSERT INTO "category" (name) VALUES (:name) RETURNING id')
            category_result = db.session.execute(insert_category_sql, {"name": new_category})
            db.session.commit()
            category = category_result.fetchone()

        transaction_sql = text('INSERT INTO "transaction" (description, amount, timestamp, user_id, account_id, recurring) VALUES (:description, :amount, :timestamp, :user_id, :account_id, :recurring) RETURNING id')
        result = db.session.execute(transaction_sql, {"description": description, "amount": amount, "timestamp": datetime.now(), "user_id": current_user.id, "account_id": account_id, "recurring": recurring})
        db.session.commit()

        transaction = result.fetchone()

        transaction_category_sql = text('INSERT INTO "transaction_category" (transaction_id, category_id) VALUES (:transaction_id, :category_id)')
        db.session.execute(transaction_category_sql, {
            "transaction_id": transaction.id,
            "category_id": category.id
        })
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('account', account_id=account.id))
    
    #Calculate spent this month
    transactions_sql = text('SELECT * FROM "transaction" WHERE account_id = :account_id AND EXTRACT(MONTH FROM timestamp) = :month')
    transactions_result = db.session.execute(transactions_sql, {"account_id": account_id, "month": datetime.now().month})
    transactions = transactions_result.fetchall()
    spent_this_month = sum(t.amount for t in transactions)

    sql_all_transactions = text('SELECT transaction.*, category.name FROM transaction LEFT JOIN transaction_category ON transaction.id = transaction_category.transaction_id LEFT JOIN category ON transaction_category.category_id = category.id WHERE transaction.account_id = :account_id')
    param = {"account_id": account_id}
    result_all_transactions = db.session.execute(sql_all_transactions, param)
    all_transactions = result_all_transactions.fetchall()

    filtered_expenses = all_transactions

    print("Request method:", request.method)
    print("Form data:", request.form)

    if request.method == "POST":
        print("submit form")
        if filter_form.validate_on_submit():
            print("validate form")
            filter_category = filter_form.filter_category.data
            filter_start_date = filter_form.start_date.data
            filter_end_date = filter_form.end_date.data

            print(f"Start Date: {filter_start_date}")
            print(f"End Date: {filter_end_date}")
            print(f"Filter Category: {filter_category}")

            query = sql_all_transactions
            param ={"account_id": account_id}
            print(query)
            if filter_form.filter_category:
                query += text('AND tc.category_id = :category_id')
                param["filter_category"] = filter_category
                print(query)
            if filter_form.start_date:
                query += text('AND timestamp >= :filter_start_date')
                param["filter_start_date"] = filter_start_date
                print(query)
            if filter_form.end_date:
                query += text('AND timestamp <= :filter_end_date')
                param["filter_end_date"] = filter_end_date
                print(query)
            try:
                print(query)
                filter_results = db.session.execute(query, param)
                filtered_expenses = filter_results.fetchall()
            except Exception as e:
                flash(f"Error filtering transactions: {str(e)}", "danger")
        else:
            print("Form validation failed.")
            print(filter_form.errors)

    return render_template('account.html', account=account, spent_this_month=spent_this_month,
    form=add_expense_form, 
    filter_form=filter_form,
    all_transactions=all_transactions, 
    filtered_expenses=filtered_expenses)

#TEST routes
@app.route("/test_db")
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Database connection is working."
    except Exception as e:
        return str(e)
    
@app.route("/check_tables")
def check_tables():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    return str(tables)

@app.route("/test_add_user")
def test_add_user():
    try:
        newuser = User(username="testuser", pwd=bcrypt.generate_password_hash("testpassword").decode('utf-8'))
        db.session.add(newuser)
        db.session.commit()
        return "User added successfully."
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}"

@app.route("/check_categories")
def check_categories():
    try:
        sql = text("SELECT * FROM category")
        result = db.session.execute(sql)
        categories = result.fetchall()
        return jsonify([dict(row) for row in categories])
    except Exception as e:
        return str(e)