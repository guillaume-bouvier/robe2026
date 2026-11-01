from machine import Pin, I2C
import time
from mpu6050 import MPU6050

GYRO_MIN_MAGNITUDE = 1.0
Z_OFFSET = 0.2

i2c = I2C(scl=Pin(21), sda=Pin(20))
gyro = MPU6050(i2c)

print("MPU6050 Who Am I:", hex(gyro.who_am_i()))
gyro.wake()

filtered_movement = 0.0  # Initialize filtered movement with the minimum magnitude
alpha = 0.01
movement_window = []
window_duration = 2.0

while True:
    gyro_accel = gyro.read_accel_data()
    gyro_magnitude = (gyro_accel[0]**2 + gyro_accel[1]**2 + (gyro_accel[2]-Z_OFFSET)**2)**0.5 - GYRO_MIN_MAGNITUDE
    filtered_movement += alpha * (gyro_magnitude - filtered_movement)

    now = time.ticks_ms() / 1000.0
    movement_value = abs(filtered_movement)
    movement_window.append((now, movement_value))
    movement_window = [entry for entry in movement_window if now - entry[0] <= window_duration]
    max_last_2s = max((value for _, value in movement_window), default=0.0)

    print("\rFiltered Movement: {:.2f} | Max last 2s: {:.2f} | X: {:.2f} Y: {:.2f} Z: {:.2f}".format(
        movement_value,
        max_last_2s,
        gyro_accel[0],
        gyro_accel[1],
        gyro_accel[2]
    ), end="")

    time.sleep_ms(10)
