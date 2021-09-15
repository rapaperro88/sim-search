import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '3fWewx7MKKnxeDPwIz7iZsAqFTbd63Bm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_PASS')
print(os.environ.get("GMAIL_USER"))
mail = Mail(app)

VAR = "var"

from sims.users.routes import users
from sims.main.routes import main
from sims.inference.routes import inference

app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(inference)

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