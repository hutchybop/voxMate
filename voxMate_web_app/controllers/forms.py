from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, URLField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=20, message="Your password must be 5 or more characters long.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Register")