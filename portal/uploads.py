import os
import uuid
from flask import Flask, flash, request, redirect, url_for, send_from_directory, Blueprint, g
from werkzeug.utils import secure_filename
from portal.auth import login_required, admin
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
    if request.method == 'POST':
        assignment_id = request.form['assignment_id']
# VALIDATE student in roster for class

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
            unique_filename = ".".join([str(uuid.uuid4()), filename.rsplit('.', 1)[1].lower()])

            with get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT assignment_id
                        FROM uploads
                        WHERE owner_id = %s
                        AND assignment_id = %s
                    """, (g.user['id'], assignment_id))
                    first_upload = cur.fetchall()
            if not first_upload:
                file.save(os.path.join(uploads_path, unique_filename))
                with get_db() as con:
                    with con.cursor() as cur:
                        cur.execute("""
                            INSERT INTO uploads (upload_name, upload_id, owner_id, assignment_id)
                            VALUES (%s, %s, %s, %s)
                        """, (filename, unique_filename, g.user['id'], assignment_id))
            else:
                flash('File already turned in.')
    
        return redirect( url_for('student.assignments') )

@bp.route('/teacher/assignments/uploads/<upload_id>')
@login_required
@admin
def uploaded_file(upload_id):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               upload_id)




