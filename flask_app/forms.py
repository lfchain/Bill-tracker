from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, PasswordField, FloatField, SelectField
from wtforms import validators
from wtforms.fields.html5 import DateField
from wtforms.validators import (
    InputRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)

from .models import User

class SearchForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()], format='%Y-%m-%d')
    submit = SubmitField("Search")

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")


class UpdateProfilePicForm(FlaskForm):
    picture = FileField('Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only!')])

    submit = SubmitField('Update')

class ReceiptForm(FlaskForm):
    receipt = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only!')])
    amount = FloatField("Amount", validators=[InputRequired()])
    date = DateField('Date', validators=[InputRequired()], format='%Y-%m-%d')
    description = StringField('Description', validators=[InputRequired(), Length(min=1, max=100)])
    category = SelectField(u'Category', 
            choices=[('Housing','Housing'),
                    ('Transportation','Transportation'),
                    ('Food', 'Food'),
                    ('Utilities', 'Utilities'),
                    ('Insurance', 'Insurance'),
                    ('Medical & Healthcare', 'Medical & Healthcare'), 
                    ('Saving, Investing, & Debt Payments', 'Saving, Investing, & Debt Payments'),
                    ('Recreation & Entertainment', 'Recreation & Entertainment'),
                    ('Miscellaneous', 'Miscellaneous')],
            validators=[InputRequired()]
                    )
    submit = SubmitField("Submit")



