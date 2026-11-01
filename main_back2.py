from machine import Pin, I2C
import time
from lib.neopixel import NeoPixel
from lib.mpu6050 import MPU6050
from lib.color import rgb

pixel_pin1 = Pin(16)
pixel_pin2 = Pin(17)
PIXEL_COUNT = 1
COLOR = rgb(213, 43, 43)

MAX_BRIGHTNESS = 255
MIN_BRIGHTNESS = 0

strip1 = NeoPixel(pixel_pin1, PIXEL_COUNT)
strip2 = NeoPixel(pixel_pin2, PIXEL_COUNT)

GYRO_MIN_MAGNITUDE = 1.0
Z_OFFSET = 0.2
GYRO_READ_INTERVAL_MS = 10
MIN_MOVEMENT_FOR_SPEED = 0.0
MAX_MOVEMENT_FOR_SPEED = 0.5
SLOW_UPDATE_INTERVAL_MS = 75
FAST_UPDATE_INTERVAL_MS = 1
i2c = I2C(scl=Pin(21), sda=Pin(20))
gyro = MPU6050(i2c)

filtered_movement = 0.0  # Initialize filtered movement with the minimum magnitude
alpha = 0.005

PRINT_INTERVAL_MS = 250  # Print status every 1 second


def get_movement():
    global filtered_movement
    gyro_accel = gyro.read_accel_data()
    gyro_magnitude = (gyro_accel[0]**2 + gyro_accel[1]**2 + (gyro_accel[2]-Z_OFFSET)**2)**0.5 - GYRO_MIN_MAGNITUDE
    filtered_movement += alpha * (gyro_magnitude - filtered_movement)

    return abs(filtered_movement)


def get_sleep_duration(movement_value):
    """Map movement gradually to a light update interval."""
    movement_range = MAX_MOVEMENT_FOR_SPEED - MIN_MOVEMENT_FOR_SPEED
    movement_fraction = (movement_value - MIN_MOVEMENT_FOR_SPEED) / movement_range
    movement_fraction = max(0.0, min(1.0, movement_fraction))

    interval_range = SLOW_UPDATE_INTERVAL_MS - FAST_UPDATE_INTERVAL_MS
    return int(SLOW_UPDATE_INTERVAL_MS - movement_fraction * interval_range)


def init():
    strip1[0] = (0, 0, 0)
    strip1.write()
    strip2[0] = (0, 0, 0)
    strip2.write()

    gyro.wake()


def main():
    i = 0
    increment = 1
    movement_value = 0.0
    now = time.ticks_ms()
    last_gyro_read = now
    last_light_update = now
    last_status_print = now

    while True:
        now = time.ticks_ms()

        if time.ticks_diff(now, last_gyro_read) >= GYRO_READ_INTERVAL_MS:
            last_gyro_read = now
            movement_value = get_movement()
            gyro_read_duration = time.ticks_diff(time.ticks_ms(), last_gyro_read)

        sleep_duration = get_sleep_duration(movement_value)
        if time.ticks_diff(now, last_light_update) >= sleep_duration:
            last_light_update = now
            strip1[0] = (MIN_BRIGHTNESS + i, 0, 0)
            strip2[0] = (MAX_BRIGHTNESS - i, 0, 0)
            strip1.write()
            strip2.write()

            if i >= MAX_BRIGHTNESS - MIN_BRIGHTNESS:
                increment = -1
            elif i <= 0:
                increment = 1
            i += increment

            light_update_duration = time.ticks_diff(time.ticks_ms(), last_light_update)

        if time.ticks_diff(now, last_status_print) >= PRINT_INTERVAL_MS:
            last_status_print = now
            print(f"\rMovement: {movement_value:.2f} | Sleep Duration: {sleep_duration} | Brightness: {i} | Strip1: {strip1[0]} | Strip2: {strip2[0]} | Gyro Read Duration: {gyro_read_duration} | Light Update Duration: {light_update_duration}", end=' ')


        time.sleep_ms(1)



if __name__ == "__main__":
    init()
    main()
