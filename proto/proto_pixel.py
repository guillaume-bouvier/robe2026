from machine import Pin
from lib.neopixel import NeoPixel

pixel_pin = Pin(28)
PIXEL_COUNT = 3
COLOR = 0xFF0000

strip = NeoPixel(pixel_pin, PIXEL_COUNT)

def hex_to_rgb(hex_color):
    """Convert a hex color to an RGB tuple."""
    return ((hex_color >> 16) & 0xFF, (hex_color >> 8) & 0xFF, hex_color & 0xFF)

strip.fill(hex_to_rgb(COLOR))
strip.write()

def main():
    while True:
        value = input("Enter an RGB hex color (for example, FF0000): ").strip()

        if len(value) != 6:
            print("Color must contain exactly 6 hexadecimal digits")
            continue

        strip.set_no_gamma(2, strip[1])
        strip.set_no_gamma(1, strip[0])
        strip[0] = hex_to_rgb(int(value, 16))

        strip.write()

        print(f"Set color to: {value}")
        print(f"Actual RGB values: {strip[0]}")
        print(f"Full strip values: {[strip[i] for i in range(PIXEL_COUNT)]}")

if __name__ == "__main__":
    main()
