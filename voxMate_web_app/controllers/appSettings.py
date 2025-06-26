from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash
from models.decorators import isLoggedIn
from models.forms import SettingsForm

appSettings = Blueprint(
    "appSettings", __name__, template_folder="templates", static_folder="static"
)

@appSettings.route("/settings", methods=["GET", "POST"])
@isLoggedIn
def settings():
    settingsForm = SettingsForm()
    settings = current_app.db.appSettings.find_one({"_id": session["_id"]})

    # Checks if the The form validates, and The form data contains the key 'noise_reduction'
    #  — regardless of whether its value is True or False, just that the key exists.
    # Checking noise_reduction here as WTForms does not handle boolean field validation well
    if settingsForm.validate_on_submit() and 'noise_reduction' in settingsForm.data:

        print(settingsForm.data)

        # Collect the form data, excluding the CSRF token
        form_data = {k: v for k, v in settingsForm.data.items() 
                    if k != 'csrf_token'}
        
        # Insert the new user settings into the database
        settingUpdate = current_app.db.appSettings.update_one(
            {"_id": session["_id"]},
            {"$set": form_data}
        )

        if settingUpdate:
            appSettings.socketio.emit('settings_updated')


        flash("Settings updated successfully!", "success")
        return redirect(url_for("appSettings.settings"))
    

    return render_template("appSettings/settings.html", title="voxMate - Settings", settings=settings, settingsForm=settingsForm)


