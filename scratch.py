import os
import imghdr
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS
from datetime import datetime

# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4096 * 4096
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.config['UPLOAD_PATH'] = 'media/uploads'
app.config['EXPORT_PATH'] = 'media/exports'

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    files = os.listdir(app.config['EXPORT_PATH'])
    for file in files:
        if file != "sample.jpg":
            os.remove(os.path.join(app.config['EXPORT_PATH'], file))
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        # convert here
        imageconvert(filename)

    if filename != "sample.jpg":
        os.remove(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('exports'))

@app.route('/media/exports/<filename>')
def export(filename):
    return send_from_directory(app.config['EXPORT_PATH'], filename)

@app.route('/exports')
def exports():
    files = os.listdir(app.config['EXPORT_PATH'])
    print(files)
    return render_template('export.html', files=files)
