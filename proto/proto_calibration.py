from machine import I2C, Pin
import time

from lib.mpu6050 import MPU6050
from lib.neopixel import NeoPixel, SeeSaw


# Keep these sensor settings aligned with main.py.
I2C_ID = 1
SCL_PIN = 19
SDA_PIN = 18
NEOPIXEL_PIN = 28
PIXEL_COUNT = 25
GYRO_MIN_MAGNITUDE = 1.0
Z_OFFSET = 0.0
ALPHA = 0.005

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
SAMPLE_INTERVAL_MS = 10
SAMPLE_DURATION_MS = 3000
CAPTURE_COUNTDOWN_SECONDS = 5
SPEED_PREVIEW_MS = 2000

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
    (20, 21),
    (22, 23),
    (24, 24),
]

i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
gyro = MPU6050(i2c)
strip = NeoPixel(Pin(NEOPIXEL_PIN), PIXEL_COUNT)
seesaw = SeeSaw(strip, PIXEL_MAP)


def capture_movement(label):
    """Return the 90th-percentile movement after a guided 3-second capture."""
    print(
        "\n{}: get ready. Capture starts in {} seconds.".format(
            label, CAPTURE_COUNTDOWN_SECONDS
        )
    )
    for seconds_left in range(CAPTURE_COUNTDOWN_SECONDS, 0, -1):
        print("{}...".format(seconds_left))
        time.sleep_ms(1000)
    print("Capturing... perform the movement steadily.")

    filtered_movement = 0.0
    movement_values = []
    sample_count = SAMPLE_DURATION_MS // SAMPLE_INTERVAL_MS

    for _ in range(sample_count):
        accel_x, accel_y, accel_z = gyro.read_accel_data()
        magnitude = (
            accel_x ** 2
            + accel_y ** 2
            + (accel_z - Z_OFFSET) ** 2
        ) ** 0.5 - GYRO_MIN_MAGNITUDE
        filtered_movement += ALPHA * (magnitude - filtered_movement)
        movement_values.append(abs(filtered_movement))
        time.sleep_ms(SAMPLE_INTERVAL_MS)

    movement_values.sort()
    calibrated_value = movement_values[int((len(movement_values) - 1) * 0.9)]
    print(
        "{} movement: p90={:.4f}, median={:.4f}, peak={:.4f}".format(
            label,
            calibrated_value,
            movement_values[len(movement_values) // 2],
            movement_values[-1],
        )
    )
    return calibrated_value


def read_speed_level(prompt, minimum=0):
    while True:
        response = input(prompt).strip()
        try:
            speed_level = int(response)
        except ValueError:
            print(
                "Enter a whole number from {} to {}.".format(
                    minimum, len(SPEED_MAPPING) - 1
                )
            )
            continue

        if minimum <= speed_level < len(SPEED_MAPPING):
            return speed_level
        print(
            "Speed level must be from {} to {}.".format(
                minimum, len(SPEED_MAPPING) - 1
            )
        )


def preview_speed_levels():
    print("\nPreviewing each configured NeoPixel speed level.")
    print("Level 0 is slowest; higher levels are progressively faster.")

    for speed_level, (sleep_ms, increment) in enumerate(SPEED_MAPPING):
        seesaw.set_speed(sleep_ms)
        seesaw.set_increment(increment)
        print(
            "Level {}: sleep={} ms, increment={}".format(
                speed_level, sleep_ms, increment
            )
        )
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < SPEED_PREVIEW_MS:
            seesaw.update()
            time.sleep_ms(1)


def main():
    strip.fill((0, 0, 0))
    strip.write()
    gyro.wake()

    print("MPU6050 and NeoPixel seesaw calibration")
    print("Connect to the board's serial terminal for prompts and results.")
    print(
        "For each movement capture, move the sensor as instructed until "
        "the capture finishes."
    )

    min_movement = capture_movement(
        "Minimum movement that should start increasing speed"
    )
    max_movement = capture_movement(
        "Strongest movement that should reach maximum speed"
    )

    while min_movement >= max_movement:
        print(
            "\nThe measured minimum ({:.4f}) must be less than the maximum "
            "({:.4f}). Please repeat the movement captures.".format(
                min_movement, max_movement
            )
        )
        min_movement = capture_movement(
            "Minimum movement that should start increasing speed"
        )
        max_movement = capture_movement(
            "Strongest movement that should reach maximum speed"
        )

    preview_speed_levels()
    min_speed = read_speed_level(
        "\nEnter the slowest speed level to use (0-{}): ".format(
            len(SPEED_MAPPING) - 1
        )
    )
    max_speed = read_speed_level(
        "Enter the fastest speed level to use ({}-{}): ".format(
            min_speed, len(SPEED_MAPPING) - 1
        ),
        min_speed,
    )

    print("\nCalibration results - copy these values into main.py:")
    print("MIN_MOVEMENT_FOR_SPEED = {:.4f}".format(min_movement))
    print("MAX_MOVEMENT_FOR_SPEED = {:.4f}".format(max_movement))
    print("MIN_SPEED = {}".format(min_speed))
    print("MAX_SPEED = {}".format(max_speed))

    strip.fill((0, 0, 0))
    strip.write()


if __name__ == "__main__":
    main()
