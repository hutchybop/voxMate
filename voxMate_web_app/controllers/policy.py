from flask import Blueprint, render_template

policy = Blueprint(
    "policy", __name__, template_folder="templates", static_folder="static"
)

@policy.route("/t&c")
def t_c():
    return render_template("policy/t_c.html", title="voxMate - T&Cs")


@policy.route("/cookie")
def cookie():
    return render_template("policy/cookie.html", title="voxMate - Cookie Policy")
