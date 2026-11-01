from machine import Pin
from lib.neopixel import NeoPixel

pixel_pin = Pin(16)
pixel_pin2 = Pin(17)
PIXEL_COUNT = 1
COLOR = 0xFF0000

strip = NeoPixel(pixel_pin, PIXEL_COUNT)
strip2 = NeoPixel(pixel_pin2, PIXEL_COUNT)

def hex_to_rgb(hex_color):
    """Convert a hex color to an RGB tuple."""
    return ((hex_color >> 16) & 0xFF, (hex_color >> 8) & 0xFF, hex_color & 0xFF)

strip[0] = hex_to_rgb(COLOR)
strip.write()
strip2[0] = hex_to_rgb(COLOR)
strip2.write()


def main():
    while True:
        value = input("Enter an RGB hex color (for example, FF0000): ").strip()

        if len(value) != 6:
            raise ValueError("Color must contain exactly 6 hexadecimal digits")

        strip[0] = hex_to_rgb(int(value, 16))
        strip.write()
        strip2.set_no_gamma(0, hex_to_rgb(int(value, 16)))
        strip2.write()

        print(f"Set color to: {value}")
        print(f"Actual RGB values: {strip[0]}")

if __name__ == "__main__":
    main()
