import os
import secrets
from PIL import Image
from flask_mail import Message
from flask import url_for
from sims import mail
import json


def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def save_picture(form_picture, app):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('[Sim-Search] Réinitialisation du mot de passe',
                  sender='andres.lombana88@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Pour changer votre mot de passe dans l'application Sim-Search, veuillez cliquer sur le lien ci-dessous :
{url_for('users.reset_token', token=token, _external=True)}
Si vous n'êtes pas à l'origine de cette demande veuillez ignorer ce mail.
'''
    mail.send(msg)


def send_error_email_notification(user, error_code):
    msg = Message(f'[Sim-Search - Admin] Problème général dans le serveur (erreur {error_code}).',
                  sender='a.lombana.dev@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Une erreur {error_code} a été détectée dans l'application Sim-Search !
Si vous n'êtes pas à administrateur de l'application Sim-Search, veuillez ignorer ce mail.
'''
    mail.send(msg)


def allowed_file(filename: str, allowed_extensions: set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


