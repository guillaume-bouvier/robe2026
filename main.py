from machine import Pin, I2C
import time
import sys
try:
    import uselect as select
except ImportError:
    import select
from lib.neopixel import NeoPixel, SeeSaw
from lib.mpu6050 import MPU6050

GYRO_MIN_MAGNITUDE = 1.0
Z_OFFSET = 0.0
MIN_MOVEMENT_FOR_SPEED = 0.0
MAX_MOVEMENT_FOR_SPEED = 0.5
MIN_SPEED = 0
MAX_SPEED = 9
ALPHA = 0.005
filtered_movement = 0.0  # Initialize filtered movement with the minimum magnitude

i2c = I2C(1, scl=Pin(19), sda=Pin(18))
gyro = MPU6050(i2c)
gyro_enabled = False

pixel_pin = Pin(28)
PIXEL_COUNT = 25

strip = NeoPixel(pixel_pin, PIXEL_COUNT)

PIXEL_MAP = [
    (0, 1),
    (2, 3),
    (4, 5),
    (6, 7),
    (8, 10),
    (9, 11),
    ]

# Map of sleep ms and increment
SPEED_MAPPING = [
    (100, 1),
    (50, 1),
    (25, 1),
    (10, 1),
    (5, 1),
    (2, 1),
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
]

seesaw = SeeSaw(strip, PIXEL_MAP)


def set_seesaw_speed(speed):
    """Set the animation speed using one of the configured levels, from SEED_MAPPING."""
    if speed < 0 or speed >= len(SPEED_MAPPING):
        print("Invalid speed level: {}. Must be between 0 and {}.".format(speed, len(SPEED_MAPPING) - 1))
        return
    sleep_ms, increment = SPEED_MAPPING[speed]
    seesaw.set_speed(sleep_ms)
    seesaw.set_increment(increment)


def get_movement():
    global filtered_movement, gyro_enabled
    try:
        gyro_accel = gyro.read_accel_data()
    except Exception as e:
        print("Gyro read failed: {}".format(e))
        gyro_enabled = False
        return 0.0
    gyro_magnitude = (gyro_accel[0]**2 + gyro_accel[1]**2 + (gyro_accel[2]-Z_OFFSET)**2)**0.5 - GYRO_MIN_MAGNITUDE
    filtered_movement += ALPHA * (gyro_magnitude - filtered_movement)
    return abs(filtered_movement)


def get_speed(movement_value):
    movement_range = MAX_MOVEMENT_FOR_SPEED - MIN_MOVEMENT_FOR_SPEED
    movement_fraction = (movement_value - MIN_MOVEMENT_FOR_SPEED) / movement_range
    movement_fraction = max(0.0, min(1.0, movement_fraction))

    interval_range = MAX_SPEED - MIN_SPEED
    return int(MIN_SPEED + movement_fraction * interval_range)


def init():
    strip.fill((0, 0, 0))  # Turn off all pixels initially
    strip.write()

    try:
        gyro.wake()
        global gyro_enabled
        gyro_enabled = True
    except Exception as e:
        print("Gyro initialization failed: {}".format(e))
        gyro_enabled = False


def main():
    set_seesaw_speed(0)
    movement = 0.0

    while True:
        # TODO: Should disabling the gyro be a one-time thing, or should it be re-enabled if it starts working again?
        if gyro_enabled:
            movement = get_movement()
        speed = get_speed(movement)
        set_seesaw_speed(speed)
        seesaw.update()
        time.sleep_ms(1)


if __name__ == "__main__":
    init()
    main()
