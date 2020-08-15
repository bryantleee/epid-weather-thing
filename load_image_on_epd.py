#!/usr/bin/env python

from PIL import Image
from inky import InkyWHAT

COLOR = 'yellow'

def load_image_on_epd(img, color=COLOR):
    
    assert img.size[0] == 400 and img.size[1] == 300, 'Image is {}. Please resize to make it (400, 300)'.format(img.size)
    
    # Set up the inky wHAT display and border colour
    inky_display = InkyWHAT(color)
    inky_display.set_border(inky_display.YELLOW)

    # Convert the image to use a white / black / red colour palette
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
    img = img.convert("RGB").quantize(palette=pal_img)

    # Display the final image on Inky wHAT
    inky_display.set_image(img)
    inky_display.show()

