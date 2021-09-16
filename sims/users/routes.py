import os
import sims
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from sims import db, bcrypt
from sims.models import User
from sims.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm)
from sims.users.utils import save_picture, send_reset_email
import logging

users = Blueprint("users", __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("Vous êtes déjà identifié, vous pouvez utiliser Sim-Search.", "success")
        return redirect(url_for("main.home"))

    form = RegistrationForm()

    if len([f for f in os.listdir(os.path.dirname(sims.__file__)) if f.endswith(".db")]) == 0:
        db.create_all()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Le compte pour {form.username.data} a bien été crée! \
        Veuillez vous connecter pour pouvoir utiliser Sim-Search', 'success')
        logging.info(f"New account created. login: {form.username.data}.")
        return redirect(url_for("main.home"))


    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Le compte pour {form.username.data} a bien été crée! \
        Veuillez vous connecter pour pouvoir utiliser Sim-Search', 'success')
        logging.info(f"New account created. login: {form.username.data}.")
        return redirect(url_for("main.home"))
    return render_template('register.html', title="S'inscrire", form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            logging.info(f"Logged as: {form.email.data}.")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Connexion refusée. Veillez vérifier le nom d'utilisateur et le mot de passe", 'danger')
    return render_template('login.html', title='Connexion', form=form)


@users.route("/logout")
def logout():
    logout_user()
    logging.info(f"User logged out.")
    return redirect(url_for("main.home"))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, current_app)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Vos informations ont bien été mises à jour.", 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Mon compte',
                           image_file=image_file, form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        logging.warning(f"{user} asked for password reset. Mail containting token sent.")
        flash(f'Un mail vous a été envoyé à {user} avec les instructions pour réinitialiser votre mot de passe.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Réinitialiser le mot de passe', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Le token utilisé a expiré ou est incorrect.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        logging.warning(f"Password for {user} was reset successfully.")
        flash("Votre mot de passe a bien été modifié, vous pouvez vous connecter dès à présent.", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)




