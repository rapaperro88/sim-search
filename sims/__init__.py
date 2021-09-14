from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '3fWewx7MKKnxeDPwIz7iZsAqFTbd63Bm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from sims import routes

# --------

import os
import logging

IMAGE_FOLDER = os.path.join("sims", 'static', 'img')
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

logging.basicConfig(filename='logs.log',
                    # encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )