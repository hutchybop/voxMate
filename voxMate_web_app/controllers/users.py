# Required python imports
from flask import Blueprint, render_template, flash, current_app, session, redirect, url_for, request
from passlib.hash import pbkdf2_sha256
import uuid
from dataclasses import asdict
from pathlib import Path
import json
import os

#  Required local imports
from models.forms import RegisterForm
from models.forms import LoginForm
from models.forms import VerifyForm
from models.models import User
from models.models import AppSettings
from models.decorators import isLoggedIn
from models.decorators import check_user_status
from utils.api import contact_api_server

users = Blueprint(
    "users", __name__, template_folder="templates", static_folder="static"
)

# Define the base directory and the path to the user configuration file
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # goes up to voxMate/
CONFIG_PATH = BASE_DIR / "userConfig" / "user_config.json"


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
    user_settings = current_app.db.appSettings.find_one({"user_id": user_id})
    if not user_settings:
        # If no settings found, create default settings for the user
        default_settings = current_app.db.appSettings.find_one({"user_id": "default"})

        # Using get() to either set the defualt_setting value or the value given
        new_user_settings = AppSettings(
            user_id=user_id,
            email=email,
            silence_threshold=default_settings.get("silence_threshold"),
            silence_duration=default_settings.get("silence_duration"),
            volume_display=default_settings.get("volume_display"),
            noise_reduction=default_settings.get("noise_reduction"),
            stt_model=default_settings.get("stt_model"),
            ai_model=default_settings.get("ai_model")
        )
        # Insert the new user settings into the database
        current_app.db.appSettings.insert_one(asdict(new_user_settings))


def get_device_id():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    serial = line.strip().split(':')[1].strip()
                    return f"raspi-{serial}", None
        return None, "Serial not found"
    except Exception as e:
        return None, str(e)
 

@users.route("/register", methods=["GET", "POST"])
@check_user_status
def register():

    # Importing the RegisterForm from forms module
    form = RegisterForm()

    # If the form is submitted and valid, create a new user with unverified_user_id and send them to register/verify
    if form.validate_on_submit():

        if os.getenv("FLASK_ENV_PI") == 'true':
            # Get the device id if on Rpi
            device_id, error = get_device_id()
            if not device_id:
                flash(f"Error retrieving Raspberry device ID: {error}. Please try again.", "danger")
                return redirect(url_for('users.register'))
        else:
            # Device_id if testing locally
            device_id = 'in_dev_locally'
        
        # Check if the email already exists in the database for the device_id
        existing_user = current_app.db.users.find_one({"email": form.email.data, "device_id": device_id})
        if existing_user:
            flash("Email already registered for this device. Please log in.", "warning")
            return redirect(url_for("users.login"))
        
        # Add the user to the DB but with unverified_user_id set
        unverified_user_id = uuid.uuid4().hex
        user = User(
            unverified_user_id=unverified_user_id,
            email=form.email.data.lower(),
            verify=False,
            device_id=device_id,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        
        # Register the device and user witht the api server
        payload = {"device_id": device_id, "unverified_user_id": user.unverified_user_id, "email": user.email}
        response, error = contact_api_server(payload, "new")

        if response and response.get("success"):
            # Insert the user into the database
            current_app.db.users.insert_one(asdict(user))
            session['unverified_user_id'] = unverified_user_id # Using unverified_user_id and not user_id as user not verifed
            return redirect(url_for('users.verify'))
        elif error:
            flash(f"Error: {error}. Please try again.", 'danger')
        else:
            flash(f"Error connecting to the server. Please try again.", 'danger')
    
    return render_template("users/register.html", title="voxMate - Register", form=form)


@users.route("/register/verify", methods=["GET", "POST"])
@check_user_status
def verify():
    
    unverified_user_id = session.get("unverified_user_id")
    form = VerifyForm()

    if form.validate_on_submit():
        # Get the code the user has entered, which should be sent to the email address by the api server
        user_code = form.code.data
        # Get the user details from the DB
        user = current_app.db.users.find_one({"unverified_user_id": unverified_user_id})
        if user is None:
            session.pop('unverified_user_id', None)
            flash("Please register", "warning")
            return redirect(url_for('users.register'))

        # Verify the users code with the api server
        payload = {"device_id": user.get("device_id"), "unverified_user_id": unverified_user_id, "email": user.get("email"), "user_code": user_code}
        response, error = contact_api_server(payload, "verify")

        if response: 
            if response.get("success"):
                # Get the api_token or redirect back to verify if error
                api_token = response.get("api_token")
                if not api_token:
                    flash(f"Error connecting the server. Please try again.", 'danger')
                    return redirect(url_for('users.verify'))
                # Add the unverified_user_id to user_id
                user_id = unverified_user_id
                # Change the user id from unverified to user_id and changed verifiy to true in the DB
                current_app.db.users.update_one(
                        {"unverified_user_id": unverified_user_id}, 
                        {"$set": {"user_id": user_id, "unverified_user_id": None, "verify": True, "api_token": api_token}}
                )
                # Save the user ID to the user configuration file
                save_user_config(user_id, user.get("email"))
                # Store the user ID and email in the session
                session.pop('unverified_user_id', None)
                session["user_id"] = user_id
                session["email"] = user.get("email")
                session.permanent = True
                # Flash a success message and redirect to the index page
                flash("Registration successful!", "success")
                return redirect(url_for('main.index'))
            elif response.get("mismatch"):
                flash("The code you entered is incorrect", "warning")
                return redirect(url_for('users.verify'))
            elif response.get('expired'):
                flash("Your code has expired. Check you email for a new code", "info")
                return redirect(url_for('users.verify'))
        elif error:
            flash(f"Error: {error}. Please try again.", 'danger')
        else:
            flash(f"Error connecting the server. Please try again.", 'danger')

    return render_template("users/verify.html", title="voxMate - Verify", form=form)


@users.route("/register/get_code")
@check_user_status
def get_code():
    # Check the user is registered in the DB
    unverified_user_id = session.get("unverified_user_id")
    user = current_app.db.users.find_one({"unverified_user_id": unverified_user_id})
    if not user:
        # If not registered in db, remove the unverified_user_id from the seesion and send to register
        session.pop('unverified_user_id', None)
        flash('User not found, please register', 'warning')
        return redirect(url_for('users.register'))
    # Request new code from api server
    payload = {"device_id": user.get('device_id'), "unverified_user_id": unverified_user_id, "email": user.get('email')}
    response, error = contact_api_server(payload, "new")
    if response and response.get("success"):
        flash("New verification code sent to registered email address", "info")
    elif error:
        flash(f"Error: {error}. Please try again.", 'danger')
    else:
        flash(f"Error connecting the server. Please try again.", 'danger')
    
    return redirect(url_for('users.verify'))


@users.route("/login", methods=["GET", "POST"])
@check_user_status
def login():
    
    form = LoginForm()

    if form.validate_on_submit():
        # Find the user by email
        user_data = current_app.db.users.find_one({"email": form.email.data})
        
        # If no user found with this email
        if not user_data:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("users.login"))
        
        # If the user's verify is false add unverified_user_id to the session and redirect to verify
        if user_data.get("verify") == False:
            if user_data.get("unverified_user_id"):
                session.pop("user_id", None)
                session["unverified_user_id"] = user_data.get("unverified_user_id")
                current_app.db.users.update_one({"email": form.email.data}, {"$set": {"user_id": None}})
                flash("Please verify your email address")
                return redirect(url_for('users.verify'))
            elif user_data.get("user_id"):
                session.pop("user_id", None)
                session["unverified_user_id"] = user_data.get("user_id")
                current_app.db.users.update_one({"email": form.email.data}, {"$set": {"user_id": None}, "unverified_user_id": user_data.get("user_id")})
                flash("Please verify your email address")
                return redirect(url_for('users.verify'))

        # Create User object and verify password
        # user = User(**user_data)
        if not pbkdf2_sha256.verify(form.password.data, user_data.get("password")):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("users.login"))
        
        # Only reach here if both email and password are correct
        save_user_config(user_data.get("user_id"), user_data.get("email"))
        session["user_id"] = user_data.get("user_id")
        session["email"] = user_data.get("email")
        session.permanent = True
        flash("Login successful!", "success")
        return redirect(url_for("main.index"))

    return render_template("users/login.html", title="voxMate - Login", form=form)


@users.route("/logout")
@isLoggedIn
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("users.login"))