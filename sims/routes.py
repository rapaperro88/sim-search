from sims import app
import logging
from flask import render_template, url_for, flash, redirect

# Custom utils
import sys
sys.path.append('./sims/utils')
import inference_utils
import utils
from sims.forms import RegistrationForm, LoginForm
from sims.models import User

# Blog-like content for options used
options = [
    {
        'tete': "Option 1",
        'title': 'Images Similaires',
        'content': 'Téléchargez une image et obtenez des images similaires',
        'sous_titre': 'Recherche par similarité',
        'url_name': 'simil',
        },
    {
        'tete': "Option 2",
        'title': "Tri d'images",
        'content': 'Avez vous un dossier avec des images en vrac ? \nNous le trions pour vous',
        'sous_titre': "Tri d'images dans un dossier",
        'url_name': 'tri',
    },
]


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)
#
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"



# -----------------------------------------------------------------
# ------------------------ Intro Endpoints ------------------------
@app.route("/")
def home():
    logging.info("App initialized")
    return render_template('home.html')


@app.route("/about")
def about():
    logging.info("Entering about endpoint")
    return render_template('layout.html', posts=options)

@app.route("/main")
def main():
    logging.info("Entering home endpoint")
    return render_template('main.html', posts=options)



# -----------------------------------------------------------------
# ----------------------- Register + Login ------------------------
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # TODO: Database insertion
        flash(f'Le compte pour {form.username.data} a bien été crée!', 'success')
        logging.info(f"New account created. login: {form.username.data}.")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # TODO: replace by SQL validation
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



# -----------------------------------------------------------------
# ---------------------------- OPTION 1 ---------------------------
@app.route("/simil}", methods=['GET', 'POST'])
def simil():
    logging.info("Similar images selected")
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            logging.error("Unknown error, post request cannot process files. Reloading endpoint.")
            return redirect(request.url)
        logging.info("Post method allowed.")

        file = request.files['file']
        nb_responses = request.form["nb_responses"]

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            logging.warning("Tried to upload empty image field. Reloading endpoint.")
            flash('Please select a file to upload')
            return redirect(request.url)

        if file and utils.allowed_file(file.filename, ALLOWED_EXTENSIONS):

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            logging.info("File allowed. Redirecting to prediction endpoint")

        return redirect(url_for('simil_pred', filename=filename, nb_responses=str(nb_responses)))

    logging.warning("Only Post methods allowed. Reloading endpoint.")
    return render_template('simil.html', task=options[0])

@app.route('/simil_pred')  # methods=['GET', 'POST'])
def simil_pred():
    if request.method == 'POST':
        logging.warning("Method not allowed for this endpoint. Ignored request.")
        pass

    if request.method == 'GET':

        # Query image
        filename = request.args['filename']
        full_path = os.path.join(app.config['IMAGE_FOLDER'], filename)

        # Query answers expected
        nb_responses = request.args['nb_responses']

        similars_paths = inference_utils.get_similars(full_path, nb_responses)

    return render_template('simil_2.html', full_path=full_path, resp=similars_paths)



# -----------------------------------------------------------------
# ---------------------------- OPTION 1 ---------------------------
@app.route("/tri}", methods=['GET', 'POST'])
def tri():

    logging.info("Sort images selected")
    if request.method == 'POST':

        # check if the post request has the file part
        if 'fileList' not in request.files:
            logging.error("Unknown error, post request cannot process files. Reloading endpoint.")
            return redirect(request.url)
        logging.info("Post method allowed.")

        file_list = request.files['fileList']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file_list.filename == '':
            logging.warning("Tried to upload empty folder field. Reloading endpoint.")
            flash('Please select a file to upload')
            return redirect(request.url)

        if file_list:

            print(file_list)

            logging.info("File allowed. Redirecting to prediction endpoint")

        return redirect(url_for('tri_pred', fileList=file_list))

    return render_template('tri.html', task=options[1])

@app.route('/tri_pred')  # methods=['GET', 'POST'])
def tri_pred():
    if request.method == 'POST':
        logging.warning("Method not allowed for this endpoint. Ignored request.")
        pass

    if request.method == 'GET':
        # Query image
        file_list = request.args['fileList']
        print("----------------")
        print(file_list)
        print(type(file_list))
        print("----------------")

    return render_template('tri_pred.html', file_list=file_list)

