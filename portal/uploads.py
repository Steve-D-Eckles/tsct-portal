import os
import uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, Blueprint, g
from werkzeug.utils import secure_filename
from portal.auth import login_required, admin, validate_roster
from portal.db import get_db

bp = Blueprint('uploads', __name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/student/assignments/upload', methods=('GET', 'POST'))
@login_required
def upload_file():
    """Student can upload a file to certain assignments"""
    if request.method == 'POST':
        # Get the assignment_id from the form
        assignment_id = request.form['assignment_id']
        
        # Validate that the student accessing this assignment is in this session
        if validate_roster():
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No file was selected')
            # Check that this file passes all validation
            if file and allowed_file(file.filename):
                # Store the name of the uploaded file as filename
                filename = secure_filename(file.filename)
                # Store the path to the uploads directory as uploads_path
                uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
                # So that files with the same names can be uploaded this creates a unique id for the uploaded file
                unique_filename = ".".join([str(uuid.uuid4()), filename.rsplit('.', 1)[1].lower()])
                # This will attempt to get some data from uploads to see if a file has already been uploaded
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("""
                            SELECT assignment_id
                            FROM uploads
                            WHERE owner_id = %s
                            AND assignment_id = %s
                        """, (g.user['id'], assignment_id))
                        first_upload = cur.fetchall()
                # As long as the query above doesn't return any data then allow the student to upload a file
                if not first_upload:
                    # Save the file to the uploads directory
                    file.save(os.path.join(uploads_path, unique_filename))
                    # Insert the unique assignment id that is the actual name of the file in the uploads directory
                    # Insert the original name of the file as well for reference
                    with get_db() as con:
                        with con.cursor() as cur:
                            cur.execute("""
                                INSERT INTO uploads (upload_name, upload_id, owner_id, assignment_id)
                                VALUES (%s, %s, %s, %s)
                            """, (filename, unique_filename, g.user['id'], assignment_id))
                    flash('File Uploaded Succesfully!')
                # If the file has already been turned in, flash this error
                else:
                    flash('File already turned in.')

            else:
                flash('Not a file that can be turned in.')
        
    # By doing this, a get request is being preformed. This will redirect to student.home
    return redirect( url_for('student.assignments') )

@bp.route('/teacher/assignments/uploads/<upload_id>')
@login_required
@admin
def uploaded_file(upload_id):
    """ View a students uploaded file for an assignment """
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               upload_id)




