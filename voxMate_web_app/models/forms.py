# Required python imports
from flask_wtf import FlaskForm
from flask import request
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, FloatField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=20, message="Your password must be 5 or more characters long.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class SettingsForm(FlaskForm):
    silence_threshold = IntegerField("Silence Threshold", validators=[InputRequired()])
    silence_duration = FloatField("Silence Duration (s)", validators=[InputRequired()])
    volume_display = BooleanField("Volume Display")
    noise_reduction = BooleanField("Noise Reduction")
    stt_model = StringField("STT Model", validators=[InputRequired()])
    ai_model = StringField("AI Model", validators=[InputRequired()])
    default_volume = IntegerField("Default Volume (%)", validators=[InputRequired()])
    submit = SubmitField("Save Settings")

class VerifyForm(FlaskForm):
    code = StringField("code", validators=[InputRequired()])
    submit = SubmitField("Submit Code")