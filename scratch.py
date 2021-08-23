# Instagram Story Effects
# Copyright (C) 2021 William Hsieh - All Rights Reserved
# MIT License

# Add story filters to existing photos

from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS
from datetime import datetime

# import image, resize to 1080 by 1920
img = Image.open("ball.jpg")

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


# set font and font sizes for date and time
date_font = ImageFont.truetype('WestwoodSans-Regular.ttf', 80)
time_font = ImageFont.truetype('WestwoodSans-Regular.ttf', 40)

# date and time text

# using system time:
today = datetime.today()
now = datetime.now()

# using photo metadata:
exifdata = img.getexif()

# iterating over all EXIF data fields
for tag_id in exifdata:
    # get the tag name, instead of human unreadable tag id
    tag = TAGS.get(tag_id, tag_id)
    data = exifdata.get(tag_id)
    # decode bytes 
    if isinstance(data, bytes):
        data = data.decode()
    print(f"{tag:25}: {data}")

# row 39 is datetime data
now = exifdata.get(36867)
if isinstance(now, bytes):
    now = now.decode()
now = datetime.strptime(now, '%Y:%m:%d %H:%M:%S')

# day of week is stored as int from 0 to 6
dayofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
date_text = dayofweek[now.weekday()]
date_text = date_text.upper()

# convert time to 12 hour time w/ AM/PM
time_text = now.strftime("%I:%M %p")
