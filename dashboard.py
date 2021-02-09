import os, sys, time
from datetime import datetime
from waveshare_epd import epd7in5bc
import logging
from PIL import Image, ImageFont, ImageDraw
import RPi.GPIO as GPIO

import weather

logging.basicConfig(level=logging.INFO)

epd = epd7in5bc.EPD()

weatherman = weather.Weatherman(width=epd.width)
# Use Hack Font
canvas_font = ImageFont.truetype('fonts/Hack-Bold.ttf', 14)

epd.init()
epd.Clear()

time.sleep(1)
# initialize canvas
canvas = Image.new('1', (epd.width, epd.height), 255)
hrycanvas = Image.new('1', (epd.width, epd.height), 255)
canvas_drawable = ImageDraw.Draw(canvas)

# Date Row
now = datetime.now()
date = now.strftime("%A, %d. %B %Y %I:%M%p")
canvas_drawable.text((10, 0), f"Last Update: {date}", font=canvas_font)

# Location Row
canvas_drawable.text((10, 20), "Melbourne, VIC, AU", font=canvas_font)
canvas_drawable.text((0,40), f"_" * 100)

# Weatherman Row
weatherman.update_weather()
canvas.paste(weatherman.get_weather_row(), (0, 50))

# TODO: other modules
# to debug check this image file.
canvas.save('dashboard.png')
logging.info('saved latest dashboard to dashboard.png')

epd.display(epd.getbuffer(canvas), epd.getbuffer(hrycanvas))
epd.Dev_exit()
epd7in5bc.epdconfig.module_exit()
GPIO.cleanup()
exit()
