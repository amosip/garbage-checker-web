import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from garbage_checker.checker import scan_pdf_for_garbled_ocr

bp = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['GET', 'POST'])
def index():
    upload_result = None
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            temp_path = os.path.join(upload_folder, filename)
            try:
                file.save(temp_path)
                is_garbled = scan_pdf_for_garbled_ocr(temp_path)
                upload_result = {
                    'filename': filename,
                    'is_garbled': is_garbled
                }
                flash(f"'{filename}' processed.")
            except Exception as e:
                flash(f"Error processing file {filename}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        elif file and not allowed_file(file.filename):
             flash('Invalid file type. Only PDFs are allowed.')
             return redirect(request.url)
    return render_template('index.html', upload_result=upload_result)