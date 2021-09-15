import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from sims import app
from werkzeug.utils import secure_filename
import logging
from sims.inference import utils as inference_utils
from sims.users.utils import read_json, allowed_file

inference = Blueprint("inference", __name__)

options = read_json("sims/vars.json")["options"]
ALLOWED_EXTENSIONS = set(read_json("sims/vars.json")["allowed_extensions"])

# -----------------------------------------------------------------
# ---------------------------- OPTION 1 ---------------------------
@inference.route("/simil}", methods=['GET', 'POST'])
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

        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            logging.info("File allowed. Redirecting to prediction endpoint")

        return redirect(url_for('inference.simil_pred', filename=filename, nb_responses=str(nb_responses)))

    logging.warning("Only Post methods allowed. Reloading endpoint.")
    return render_template('simil.html', task=options[0])


@inference.route('/simil_pred')  # methods=['GET', 'POST'])
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
@inference.route("/tri}", methods=['GET', 'POST'])
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

        return redirect(url_for('inference.tri_pred', fileList=file_list))

    return render_template('tri.html', task=options[1])

@inference.route('/tri_pred')  # methods=['GET', 'POST'])
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



