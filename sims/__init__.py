from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

logging.basicConfig(filename='logs.log',
                    # encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

app = Flask(__name__)
IMAGE_FOLDER = os.path.join('static', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SECRET_KEY'] = '3fWewx7MKKnxeDPwIz7iZsAqFTbd63Bm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

from sims import routes