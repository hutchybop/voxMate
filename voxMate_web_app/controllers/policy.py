from flask import Blueprint, render_template, url_for
import markdown
import os
from flask import current_app

policy = Blueprint(
    "policy", __name__, template_folder="templates", static_folder="static"
)

@policy.route("/t&c")
def t_c():
    return render_template("policy/t_c.html")


@policy.route("/cookie")
def cookie():
    return render_template("policy/cookie.html")


@policy.route("/about")
def about():
    readme_path = os.path.join(current_app.root_path, "..", "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Replace image path to use the static route
    md_content = md_content.replace(
        'src="voxMate_web_app/static/images/voxMate.png"',
        f'src="{url_for("static", filename="images/voxMate.png")}"'
    )

    html_content = markdown.markdown(md_content, extensions=["fenced_code", "tables"])
    return render_template("policy/about.html", content=html_content)
