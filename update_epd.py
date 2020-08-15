from generate_weather_forecast_image import generate_weather_display_image
from load_image_on_epd import load_image_on_epd

def update_epd():
    weather_display_image = generate_weather_display_image()
    load_image_on_epd(weather_display_image)

if __name__ == '__main__':
    update_epd()