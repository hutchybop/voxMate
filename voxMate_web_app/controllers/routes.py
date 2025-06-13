from flask import Blueprint, render_template, flash, current_app, session
from passlib.hash import pbkdf2_sha256
import uuid
from dataclasses import asdict

from controllers.forms import RegisterForm
from controllers.models import User

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@pages.route("/")
def index():
    return render_template("index.html")

@pages.route("/register", methods=["GET", "POST"])
def register():

    # Check if user is already logged in
    if session.get("_id"):
        return render_template("index.html")
    
    # Importing the RegisterForm from forms module
    form = RegisterForm()

    # If the form is submitted and valid, create a new user
    if form.validate_on_submit():
        # Check if the email already exists in the database
        existing_user = current_app.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return render_template("login.html")
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
        return render_template("index.html")
    

    return render_template("register.html", title="Movies Watchlist - Register", form=form)

