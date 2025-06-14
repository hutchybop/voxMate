from flask import Blueprint, render_template
from models.decorators import isLoggedIn

appSettings = Blueprint(
    "appSettings", __name__, template_folder="templates", static_folder="static"
)

@appSettings.route("/settings")
@isLoggedIn
def settings():
    return render_template("appSettings/settings.html")
