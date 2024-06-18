from sqlalchemy import text
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    ValidationError,
    FloatField,
    SubmitField,
    SelectField,
)
from wtforms.validators import InputRequired, Length, EqualTo, DataRequired, Regexp, NumberRange, Optional
from flask_wtf import FlaskForm
from app import db

class login_form(FlaskForm):
    username = StringField(validators=[InputRequired()])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])

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
        sql = text('SELECT id FROM "user" WHERE username = :username')
        print(f"sql q {sql}")
        result = db.session.execute(sql, {"username": username.data})
        user = result.fetchone()
        if user:
            raise ValidationError("Username already taken!")
        
class create_account_form(FlaskForm):
    name = StringField('Account Name', validators=[DataRequired()])
    balance = FloatField('Initial Balance', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class AddExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    category = SelectField('Category', validators=[Optional()])
    new_category = StringField('Or Name New Category', validators=[Optional()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    recurring = BooleanField('Recurring', validators=[Optional()])
    submit = SubmitField('Add Expense')

class FilterDataForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    filter_category = SelectField('Category', validators=[Optional()])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(FilterDataForm, self).__init__(*args, **kwargs)
        sql = text("SELECT id, name FROM category")
        categories = db.session.execute(sql).fetchall()
        self.filter_category.choices = [(c.id, c.name) for c in categories]