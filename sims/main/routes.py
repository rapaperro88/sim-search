from flask import render_template, Blueprint
import logging
from sims.users.utils import read_json

main = Blueprint("main", __name__)

options = read_json("sims/vars.json")["options"]

@main.route("/")
@main.route("/home")
def home():
    logging.info("App initialized")
    return render_template('home.html')


@main.route("/main.about")
def about():
    logging.info("Entering about endpoint")
    return render_template('about.html', title="Application Sim-Search")


@main.route("/main_page")
def main_page():
    print()
    for p in  options:
        print(p["url_name"])
        print()
    logging.info("Entering home endpoint")
    return render_template('main.html', posts=options)
