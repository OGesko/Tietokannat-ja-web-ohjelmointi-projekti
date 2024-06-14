from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session
)
from sqlalchemy import text
from datetime import timedelta
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

from app import create_app,db,login_manager,bcrypt
from models import User, Account
from forms import login_form, register_form, create_account_form


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.pwd, form.pwd.data):
                    login_user(user)
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
    if form.validate_on_submit():
        try:
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                pwd=bcrypt.generate_password_hash(pwd).decode('utf-8'),
            )
    
            db.session.add(newuser)
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
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
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
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template("personal.html", user=current_user, accounts=accounts)

@app.route("/create_account", methods=("GET", "POST"))
@login_required
def create_account():
    form = create_account_form()
    if form.validate_on_submit():
        account = Account(
            name=form.name.data,
            balance=form.balance.data,
            user_id=current_user.id  # Assign the account to the current user
        )
        db.session.add(account)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('personal'))
    return render_template('create_account.html', form=form)



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

if __name__ == "__main__":
    app.run(debug=True)