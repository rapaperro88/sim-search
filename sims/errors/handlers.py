from flask import Blueprint, render_template
from sims.users.utils import send_error_email_notification
from flask_login import current_user
import logging

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    logging.error("Error 404 encountered.")
    send_error_email_notification(current_user, 404)
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    logging.error("Error 403 encountered.")
    send_error_email_notification(current_user, 403)
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    logging.error("Error 500 encountered.")
    send_error_email_notification(current_user, 500)
    return render_template('errors/500.html'), 500
