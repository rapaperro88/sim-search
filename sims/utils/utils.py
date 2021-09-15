import os
import secrets
from PIL import Image


def allowed_file(filename: str, allowed_extensions: set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions




