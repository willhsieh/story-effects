# Instagram Story Effects
# Copyright (C) 2021 William Hsieh - All Rights Reserved
# MIT License

# Add story filters to existing photos

from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS
from datetime import datetime


# -------------------------------- #
# ------------- IMAGE ------------ #
# -------------------------------- #
# import image, resize to 1080 by 1920
img = Image.open("media/drone.jpg")

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
img.save("media/output.jpg")