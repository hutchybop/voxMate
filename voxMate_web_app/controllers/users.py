from flask import Blueprint, render_template, flash, current_app, session, redirect, url_for
from passlib.hash import pbkdf2_sha256
import uuid
from dataclasses import asdict
from pathlib import Path
import json

from models.forms import RegisterForm
from models.forms import LoginForm
from models.models import User
from models.models import AppSettings
from models.decorators import isLoggedIn

users = Blueprint(
    "users", __name__, template_folder="templates", static_folder="static"
)

# Define the base directory and the path to the user configuration file
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # goes up to voxMate/
CONFIG_PATH = BASE_DIR / "config" / "user_config.json"


def save_user_config(user_id, email):
    # Ensure the directory exists
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.touch()
    # Write the user ID to the configuration file overwriting any existing content
    # If a new user logs in their settings will be appied
    with open(CONFIG_PATH, "w") as f:
        json.dump({"user_id": user_id, "email": email}, f, indent=2)
    
    # Checks mongodb to see if the user has saved settings
    user_settings = current_app.db.appSettings.find_one({"_id": user_id})
    if not user_settings:
        # If no settings found, create default settings for the user
        default_settings = current_app.db.appSettings.find_one({"_id": "default"})

        # Using get() to either set the defualt_setting value or the value given
        new_user_settings = AppSettings(
            _id=user_id,
            email=email,
            silence_threshold=default_settings["silence_threshold"],
            silence_duration=default_settings["silence_duration"],
            noise_reduction=default_settings["noise_reduction"],
            stt_model=default_settings["stt_model"],
            ai_model=default_settings["ai_model"]
        )
        # Insert the new user settings into the database
        current_app.db.appSettings.insert_one(asdict(new_user_settings))
 

@users.route("/register", methods=["GET", "POST"])
def register():

    # Check if user is already logged in
    if session.get("_id"):
        flash("You are already logged in.", "info")
        return render_template("main/index.html")
    
    # Importing the RegisterForm from forms module
    form = RegisterForm()

    # If the form is submitted and valid, create a new user
    if form.validate_on_submit():
        # Check if the email already exists in the database
        existing_user = current_app.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return render_template("users/login.html")
        # If the email is not registered, proceed with registration
        # Create a new user object
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        # Insert the user into the database
        current_app.db.users.insert_one(asdict(user))
        # Save the user ID to the user configuration file
        save_user_config(user._id, user.email)

        # Store the user ID and email in the session
        session["_id"] = user._id
        session["email"] = user.email

        # Flash a success message and redirect to the index page
        flash("Registration successful!", "success")
        return render_template("main/index.html")
    
    return render_template("users/register.html", title="voxMate - Register", form=form)



@users.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if session.get("_id"):
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))
    
    form = LoginForm()

    if form.validate_on_submit():
        # Find the user by email
        user_data = current_app.db.users.find_one({"email": form.email.data})
        
        # If no user found with this email
        if not user_data:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("users.login"))
        
        # Create User object and verify password
        user = User(**user_data)
        if not pbkdf2_sha256.verify(form.password.data, user.password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("users.login"))
        
        # Only reach here if both email and password are correct
        save_user_config(user._id, user.email)
        session["_id"] = user._id
        session["email"] = user.email
        flash("Login successful!", "success")
        return redirect(url_for("main.index"))  # Use redirect instead of render_template

    return render_template("users/login.html", title="voxMate - Login", form=form)


@users.route("/logout")
@isLoggedIn
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("users.login"))