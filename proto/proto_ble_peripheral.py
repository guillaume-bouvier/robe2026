import bluetooth
import time
from machine import Pin, I2C
from lib.ble_peripheral import BLESimplePeripheral
from lib.mpu6050 import MPU6050


print("Starting BLE Peripheral...")
led = Pin("LED", Pin.OUT)

i2c = I2C(0, scl=Pin(21), sda=Pin(20))
gyro = MPU6050(i2c)
filtered_movement = 0.0
ALPHA = 0.02
Z_OFFSET = 0.2
GYRO_MIN_MAGNITUDE = 1.0

print("... initializing BLE Peripheral")
ble = bluetooth.BLE()
peripheral = BLESimplePeripheral(ble, name="myp-gyro")

def on_rx(v):
    print("Received: {}".format(v))


def get_movement():
    global filtered_movement
    gyro_accel = gyro.read_accel_data()
    gyro_magnitude = (gyro_accel[0]**2 + gyro_accel[1]**2 + (gyro_accel[2]-Z_OFFSET)**2)**0.5 - GYRO_MIN_MAGNITUDE
    filtered_movement += ALPHA * (gyro_magnitude - filtered_movement)

    return abs(filtered_movement)


def init():
    print("Initializing...")
    led.off()
    peripheral.on_write(on_rx)
    gyro.wake()


def main():
    print("Waiting for connections...")
    while not peripheral.is_connected():
        led.toggle()
        time.sleep_ms(100)
    print("Connected")
    led.on()
    while peripheral.is_connected():
        movement_value = get_movement()
        print(f"Movement value: {movement_value:.2f}")
        peripheral.send(str(f"{movement_value:.2f}\n").encode())
        time.sleep_ms(100)


if __name__ == "__main__":
    print("Starting init...")
    init()
    print("Starting main loop...")
    main()
