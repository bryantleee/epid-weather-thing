import requests
from datetime import datetime, timedelta
import json
from PIL import Image, ImageDraw, ImageFont

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

BASE_URL = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}'
KEY = CONFIG["OPENWEATHER_API_KEY"]
COORDS = (CONFIG["LOCATION_COORD_LONG"], CONFIG["LOCATION_COORD_LAT"])

def request_weather_api(base_url=BASE_URL, coords=COORDS, key=KEY):
    r = requests.get(base_url.format(coords[0], coords[1], key))
    if r.ok:
        weather_data = r.json()
        return weather_data


def k_to_f(temp_in_k):
    return temp_in_k * (9/5) - 459.67


def is_snow_alert(hourly_weather_data):
    for hourly_weather in hourly_weather_data[:4]:
        if hourly_weather['weather'][0]['id'] in range(600, 623):
              return True
    return False

def is_umbrella_alert(hourly_weather_data):
    for hourly_weather in hourly_weather_data[:4]:
        if hourly_weather['weather'][0]['id'] in range(0, 600):
              return True
    return False

def get_concat_h(im1, im2):
    dst = Image.new('RGBA', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGBA', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def center_crop_image(im, new_width, new_height):
    width, height = im.size   # Get dimensions
    left = (width - new_width)//2
    top = (height - new_height)//2
    right = (width + new_width)//2
    bottom = (height + new_height)//2
    # Crop the center of the image
    return im.crop((left, top, right, bottom))


def get_concat_h_cut(im1, im2):
    dst = Image.new('RGBA', (im1.width + im2.width, min(im1.height, im2.height)))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def generate_weather_icon(weather_id, resize=(200, 200)):
    return Image.open('icons/{}@2x.png'.format(weather_id)).resize(resize, Image.ANTIALIAS)

def generate_temperature_image(temperature):
    stringed_temp = str(round(temperature))

    text_layout = {
        1 : [62, 50, 25],
        2 : [62, 30, 25],
        3 : [56, 20, 25],
        'neg' : [62, 15, 25]
    } # [font size, x start location, y start location]
    W, H = (250, 90)
    layout = text_layout.get(len(stringed_temp) if temperature >= 0 else 'neg')
    im = Image.new("RGB",(W,H),color = (255, 255, 255))
    fnt = ImageFont.truetype('fonts/Roboto-Medium.ttf', layout[0])
    draw = ImageDraw.Draw(im)
    stringed_temp += '°F'
    w, h = draw.textsize(stringed_temp, font=fnt)
    draw.text(((W-w)/2, 25), stringed_temp, font=fnt, fill="black")
    return im


def generate_subcaption_image(temperature, feels_like_temperature, weather_description):
    
    '''
    subcaption will be feels like temperature if it is signficantly different than actual temperature
    subcaption will be weather in all other cases
    '''
    subcaption = weather_description.title() if feels_like_temperature - 5 < temperature < feels_like_temperature + 5 else 'Feels Like {}°F'.format(feels_like_temperature)    
    
    W, H = (250, 60)

    im = Image.new("RGB",(W,H),color = (255, 255, 255))
    fnt = ImageFont.truetype('fonts/Roboto-Medium.ttf', 25)

    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(subcaption, font=fnt)
    draw.text(((W-w)/2, 0), subcaption, font=fnt, fill="black")
    
    return im


def generate_future_weather_icon(weather_id, width):
    weather_icon = generate_weather_icon(weather_id, resize=(100, 100))
    return center_crop_image(weather_icon, width, 75)


def generate_future_time_image(time, width):
    W, H = (width, 25)
    im = Image.new("RGB",(W,H),color = (255, 255, 0))
    fnt = ImageFont.truetype('fonts/Roboto-Medium.ttf', 16)
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(time, font=fnt)
    draw.text(((W-w)/2, 10), time, font=fnt, fill="white")
    return im


def generate_future_temperature_image(temperature, width):
    temperature = str(round(temperature)) +'°F'
    W, H = (width, 50)
    im = Image.new("RGB",(W,H),color = (255, 255, 0))
    fnt = ImageFont.truetype('fonts/Roboto-Medium.ttf', 28)
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(temperature, font=fnt)
    draw.text(((W-w)/2, 0), temperature, font=fnt, fill="white")
    return im

def generate_future_image(temperature, weather_id, time, i):
    width = 133 if i != 2 else 134
    future_weather_icon = generate_future_weather_icon(weather_id, width)
    future_time_image = generate_future_time_image(time, width)
    future_temperature_image = generate_future_temperature_image(temperature, width)
    
    temp = get_concat_v(future_time_image, future_weather_icon)
    return get_concat_v(temp, future_temperature_image)

def convert_to_rgb(img, yellow_background=False):
    background = Image.new("RGB", img.size, (255, 255, 0 if yellow_background else 255))
    background.paste(img, mask=img.split()[3]) #3 is the alpha channel
    return background

# # Main Function to Call
# ### Call API
def generate_weather_display_image():
    weather = request_weather_api()
    current_weather = weather['current']


    # ### 1. Generate weather condition images
    current_weather_condition = current_weather['weather'][0]
    condition_icon = generate_weather_icon(current_weather_condition['icon'])
    condition_icon = center_crop_image(condition_icon, 150, 150)


    # ### 2. Generate temperature images
    temperature = k_to_f(current_weather['temp'])
    temperature_img = generate_temperature_image(temperature)


    # ### 3. Generate Subheading images
    subheading_img = generate_subcaption_image(current_weather['temp'], 
                                                current_weather['feels_like'], 
                                                current_weather['weather'][0]['description'])
    temp_and_subcap = get_concat_v(temperature_img, subheading_img)
    current_weather_img = get_concat_h_cut(condition_icon, temp_and_subcap)

    # ### 4. Generate Future Forecast images
    current_time = datetime.now()
    current_time_str = current_time.strftime("%I:00 %p")
    future_time_images = []
    delta_hours = (1, 3, 5)
    for i, delta_hour in enumerate(delta_hours):
        future_time = current_time + timedelta(hours=delta_hour)
        for hourly_weather in weather['hourly']:
            if datetime.fromtimestamp(hourly_weather['dt']).hour == future_time.hour:
                future_time_images.append(generate_future_image(k_to_f(hourly_weather['temp']), 
                                                                hourly_weather['weather'][0]['icon'], 
                                                                future_time.strftime("%I:00 %p"), i))
                break
    
    
    temp = get_concat_h(future_time_images[0], future_time_images[1])
    future_forecast_image = convert_to_rgb(get_concat_h(temp, future_time_images[2]), yellow_background=True)
    weather_image = get_concat_v(current_weather_img, future_forecast_image)
    return convert_to_rgb(weather_image)   
if __name__ == '__main__':
    generate_weather_display_image().save('sample-output3.png')
    print('finished')