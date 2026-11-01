from machine import Pin
import time
from lib.neopixel import NeoPixel

pixel_pin1 = Pin(16)
pixel_pin2 = Pin(17)
PIXEL_COUNT = 1
COLOR = 0xFF0000

strip1 = NeoPixel(pixel_pin1, PIXEL_COUNT)
strip2 = NeoPixel(pixel_pin2, PIXEL_COUNT)

def hex_to_rgb(hex_color):
    """Convert a hex color to an RGB tuple."""
    return ((hex_color >> 16) & 0xFF, (hex_color >> 8) & 0xFF, hex_color & 0xFF)

strip1[0] = hex_to_rgb(COLOR)
strip1.write()

strip2[0] = hex_to_rgb(0x000000)
strip2.write()


def main():
    i = 0
    increment = True
    while True:
        strip1[0] = (i, 0, 0)
        strip2[0] = (255 - i, 0, 0)
        strip1.write()
        strip2.write()
        if i >= 255:
            increment = False
        elif i <= 0:
            increment = True
        if increment:
            i += 1
        else:
            i -= 1
        time.sleep_ms(10)



if __name__ == "__main__":
    main()
