from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sims.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("S'inscrire")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Le nom choisi existe déjà. Veuillez choisir un autre.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ce mail est déjà associé à un compte. Veuillez choisir un autre ou vous connecter.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class UpdateAccountForm(FlaskForm):
    username = StringField("Nom d'utilisateur",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Mail',
                        validators=[DataRequired(), Email()])
    picture = FileField('Changer votre photo de profil', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Modifier')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Ce nom d'utilisateur est déjà associé à un compte. Veuillez choisir un autre.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Ce mail est déjà associé à un compte. Veuillez choisir un autre.")


class RequestResetForm(FlaskForm):
    email = StringField('Mail',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Je souhaite réinitialiser mon mot de passe')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Aucun compte n'est associé à ce mail. Veuillez vous inscrire d'abord.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Réinitialiser mon mot de passe !')

