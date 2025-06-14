from flask import Blueprint, render_template, flash, current_app, session, redirect, url_for
from passlib.hash import pbkdf2_sha256
import uuid
from dataclasses import asdict

from models.forms import RegisterForm
from models.forms import LoginForm
from models.models import User
from models.decorators import isLoggedIn

users = Blueprint(
    "users", __name__, template_folder="templates", static_folder="static"
)

@users.route("/register", methods=["GET", "POST"])
def register():

    # Check if user is already logged in
    if session.get("_id"):
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
        return redirect(url_for("main.index"))

    # Importing the LoginForm from forms module
    form = LoginForm()

    # If the form is submitted and valid, log in the user
    if form.validate_on_submit():
        # Find the user by email from the forms class
        user_data = current_app.db.users.find_one({"email": form.email.data})
        #  If no user is found, flash an error message
        if not user_data:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("users.login"))
        # Create a User object from the user data
        user = User(**user_data)
        # If user is found, verify the password
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            # Store the user ID and email in the session
            session["_id"] = user._id
            session["email"] = user.email
            # Flash a success message and redirect to the index page
            flash("Login successful!", "success")
            return render_template("main/index.html")

    return render_template("users/login.html", title="voxMate - Login", form=form)



@users.route("/logout")
@isLoggedIn
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("users.login"))