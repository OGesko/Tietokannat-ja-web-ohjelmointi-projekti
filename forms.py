from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    ValidationError,
    FloatField,
    SubmitField
)
from wtforms.validators import InputRequired, Length, EqualTo, DataRequired, Regexp ,Optional
from flask_wtf import FlaskForm
from flask_login import current_user
from models import User

class login_form(FlaskForm):
    username = StringField(validators=[InputRequired()])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering


class register_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken!")
        
class create_account_form(FlaskForm):
    name = StringField('Account Name', validators=[DataRequired()])
    balance = FloatField('Initial Balance', validators=[DataRequired()])
    submit = SubmitField('Create Account')