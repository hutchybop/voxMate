# Required python imports
from flask import Blueprint, render_template, url_for, current_app
import markdown
import os

main = Blueprint(
    "main", __name__, template_folder="templates", static_folder="static"
)

@main.route("/")
def index():

    readme_path = os.path.join(current_app.root_path, "..", "readme.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Replace image path to use the static route
    md_content = md_content.replace(
        'src="voxMate_web_app/static/images/voxMate.png"',
        f'src="{url_for("static", filename="images/voxMate.png")}"'
    )

    html_content = markdown.markdown(
        md_content,
        extensions=["fenced_code", "codehilite", "tables", "attr_list"]
    )
    return render_template("main/index.html", content=html_content, title="voxMate - Home")