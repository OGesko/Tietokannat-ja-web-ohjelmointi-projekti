from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy(app)
bcrypt = Bcrypt()
migrate = Migrate(app, db)

import routes
#app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)