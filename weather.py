import requests, json
from PIL import Image, ImageFont, ImageDraw, ImageChops
#from waveshare_epd import epd7in5bc

def ms2kh(ms):
    """ converts from m/s to km/h """
    ms = float(ms)
    speed = int(ms * 3.6)
    return f'{speed}km/h'

def angle_semantics(degree):
    degree = int(degree)
    if (degree <= 20 or degree >= 340):
        return 'N'
    elif (degree > 30 and degree < 70):
        return 'NE'
    elif (degree >= 70 and degree < 120):
        return 'E'
    elif (degree >= 120 and degree < 160):
        return 'SE'
    elif (degree >= 160 and degree < 210):
        return 'S'
    elif (degree >= 210 and degree < 250):
        return 'SW'
    elif (degree >= 250 and degree < 300):
        return 'W'
    else:
        return 'NW'


def pretty_wind(wind_deg, wind_speed):
    return f'{ms2kh(wind_speed)} {angle_semantics(wind_deg)}'

class Weatherman():
    def __init__(self, width=800):
        with open(f'config/weather.json') as weatherconf:
            conf = json.load(weatherconf)
            self.lat = conf['lat']
            self.lon = conf['lon']
            self.exclude = conf['exclude']
            self.apikey = conf['apikey']
            self.width = width

    def update_weather(self):
        res = requests.get("https://api.openweathermap.org/data/2.5/onecall", timeout=1, params = {
                'lat': self.lat,
                'lon': self.lon,
                'exclude': self.exclude,
                'units': 'metric',
                'appid': self.apikey
            })

        weatherdata = res.json()
        self.weathers = []

        # append weather data for now, next 4hours, 8hours and next day.
        self.weathers.append(weatherdata['hourly'][0])
        self.weathers.append(weatherdata['hourly'][4])
        self.weathers.append(weatherdata['hourly'][8])
        self.weathers.append(weatherdata['hourly'][12])

        self.__render_display_info()

    def __render_display_info(self):
        #canvas = Image.new('1', (128, epd.width), 255)
        canvas = Image.new('1', (self.width, 128), 255)
        canvas_drawable = ImageDraw.Draw(canvas)
        canvas_font = ImageFont.truetype('fonts/Hack-Bold.ttf', 14)
        period = ['Now', '+4H', '+8H', '+12H'].__iter__()

        # horizontal axis position
        x = 0
        # Draw icons first, then overlay text so text can write into png image whitespace
        for weather in self.weathers:
            icon = weather['weather'][0]['icon']
            # icons are 128 x 128 in size
            weather_icon = Image.open(f'openweathermap-api-icons/icons/{icon}.png')
            width, height = weather_icon.size
            weather_icon = weather_icon.resize((width//2, height//2))
            weather_icon = weather_icon.convert('1').point(lambda x: 0 if x > 0 else 255, mode='1')
            #weather_icon = ImageChops.invert(weather_icon)
            canvas.paste(weather_icon, (x, 32))
            x += 128

        # reset the horizontal axis
        x = 0
        for weather in self.weathers:
            temp = weather['temp']
            uvi = weather['uvi']
            if 'prep' in weather:
                prep = weather['prep']
            else:
                prep = 0
            wind = pretty_wind(weather['wind_deg'], weather['wind_speed'])
            # write temp, uvi, prep, wind
            x += 64
            canvas_drawable.text((x, 30), f"{int(temp)} °C", font=canvas_font)
            canvas_drawable.text((x, 45), f"{int(uvi)} mW/m²", font=canvas_font)
            canvas_drawable.text((x, 60), f"{prep} mm", font=canvas_font)
            canvas_drawable.text((x, 75), f"{wind}", font=canvas_font)
            canvas_drawable.text((x, 100), f"{next(period)}", font=canvas_font)
            # shift along horizontal axis
            x += 64

        canvas.save('weather.png')

    def get_weather_row(self):
        return Image.open('weather.png')

#weatherman = Weatherman()
#weatherman.update_weather()
#weatherman.display_weather_info()
