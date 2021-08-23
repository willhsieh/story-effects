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

    os.remove(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('exports'))

@app.route('/media/exports/<filename>')
def export(filename):
    return send_from_directory(app.config['EXPORT_PATH'], filename)

@app.route('/exports')
def exports():
    files = os.listdir(app.config['EXPORT_PATH'])
    return render_template('export.html', files=files)


# -------------------------------- #
# ------- ACTUAL PROCESSING ------ #
# -------------------------------- #
@app.route("/<string:imagepath>")
def imageconvert(imagepath):
    # -------------------------------- #
    # ------------- IMAGE ------------ #
    # -------------------------------- #
    # import image, resize to 1080 by 1920
    img = Image.open("media/uploads/" + imagepath)

    # rotate to correct orientation
    try:
        exifdata = img.getexif() # get photo metadata
        orientation = exifdata.get(274)
        if orientation == 8:
            img = img.rotate(90, expand = True)
        if orientation == 3:
            img = img.rotate(180, expand = True)
        if orientation == 6:
            img = img.rotate(270, expand = True)
    except (AttributeError, KeyError, IndexError, TypeError): # in case metadata is bad
        pass

    # https://stackoverflow.com/a/4744625/16074281
    aspect = 1.0 * img.width / img.height
    ideal_aspect = 9.0 / 16.0 # Instagram stories are 9:16

    if aspect > ideal_aspect: # too wide
        new_width = int(ideal_aspect * img.height)
        offset = (img.width - new_width) / 2
        resize = (offset, 0, img.width - offset, img.height)
    else: # too narrow
        new_height = int(img.width / ideal_aspect)
        offset = (img.height - new_height) / 2
        resize = (0, offset, img.width, img.height - offset)

    img = img.crop(resize).resize((1080, 1920), Image.ANTIALIAS)


    # -------------------------------- #
    # ------------- TEXT ------------- #
    # -------------------------------- #
    # set font and font sizes for date and time
    date_font = ImageFont.truetype('WestwoodSans-Regular.ttf', 80)
    time_font = ImageFont.truetype('WestwoodSans-Regular.ttf', 40)

    try:
        # date and time text
        exifdata = img.getexif() # use photo metadata

        # row 39 is datetime data
        now = exifdata.get(36867)
        if isinstance(now, bytes):
            now = now.decode()
        now = datetime.strptime(now, '%Y:%m:%d %H:%M:%S')

    except (AttributeError, KeyError, IndexError, TypeError): # in case metadata is bad
        now = datetime.now() # use system time

    # for printing out all metadata tags:
    # for tag_id in exifdata:
    #     # get the tag name, instead of human unreadable tag id
    #     tag = TAGS.get(tag_id, tag_id)
    #     print(tag_id)
    #     data = exifdata.get(tag_id)
    #     # decode bytes 
    #     if isinstance(data, bytes):
    #         data = data.decode()
    #     print(f"{tag:25}: {data}")

    # day of week is stored as int from 0 to 6
    dayofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    date_text = dayofweek[now.weekday()]
    date_text = date_text.upper()

    # convert time to 12 hour time w/ AM/PM
    time_text = now.strftime("%I:%M %p")


    # -------------------------------- #
    # ------------- EDIT ------------- #
    # -------------------------------- #
    # load image
    draw = ImageDraw.Draw(img)

    # calculate date text offset
    w, h = draw.textsize(date_text, date_font)
    gapwidth = 50 # adjust as needed
    totalwidth = w + (len(date_text) - 1) * gapwidth

    # start position for text
    offset = 0 # vertical offset
    left = (img.width - totalwidth) / 2
    top = ((img.height - h) / 2) + offset

    # draw text, increment by gapwidth
    for letter in date_text:
        draw.text((left, top - 30), letter, (255, 255, 255), font = date_font)
        letterwidth, letterheight = draw.textsize(letter, font = date_font)
        left += gapwidth + letterwidth

    # calculate time text offset
    w, h = draw.textsize(time_text, time_font)
    gapwidth = 10 # adjust as needed
    totalwidth = w + (len(time_text) - 1) * gapwidth

    # start position for text
    left = (img.width - totalwidth) / 2
    top = ((img.height - h) / 2) + offset

    # draw text, increment by gapwidth
    for letter in time_text:
        draw.text((left, top + 60), letter, (255, 255, 255), font = time_font)
        letterwidth, letterheight = draw.textsize(letter, font = time_font)
        left += gapwidth + letterwidth


    # -------------------------------- #
    # ------------ EXPORT ------------ #
    # -------------------------------- #
    # save image
    img.save("media/exports/" + imagepath)

    return True






if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    