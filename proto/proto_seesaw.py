from machine import Pin, I2C
import time
from lib.neopixel import NeoPixel, SeeSaw
from lib.mpu6050 import MPU6050

pixel_pin = Pin(16)
PIXEL_COUNT = 20

strip = NeoPixel(pixel_pin, PIXEL_COUNT)

PIXEL_MAP = [
    (0, 1),
    (2, 3),
    (4, 5),
    (6, 7),
    (8, 9),
    (10, 11),
    (12, 13),
    (14, 15),
    (16, 17),
    (18, 19),
]

seesaw = SeeSaw(strip, PIXEL_MAP)


def init():
    strip.fill((0, 0, 0))  # Turn off all pixels initially
    strip.write()


def main():
    seesaw.set_speed(100)  # Set the speed of the animation (lower is faster)
    seesaw.set_increment(2)  # Set the increment value for the animation
    while True:
        updated = seesaw.update()
        time.sleep_ms(1)


if __name__ == "__main__":
    main()
