from math import sqrt
import time
import lib.logging as logging
from lib.seesaw import Seesaw

# try:
#     import uasyncio as asyncio
# except ImportError:
#     import asyncio

#     async def sleep_ms(milliseconds: int, /) -> None:
#         await asyncio.sleep(milliseconds / 1000)
# else:
#     sleep_ms = asyncio.sleep_ms

import uasyncio as asyncio

sleep_ms = asyncio.sleep_ms

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

try:
    from machine import I2C, Pin
except ImportError:
    logger.info("Running on a computer, using mock MPU6050.")
    from mock.mpu6050 import MPU6050
    from mock.neopixel import NeoPixel
    import mock.bluetooth as bluetooth
    from mock.ble_peripheral import BLESimplePeripheral

    IS_LOCAL = True

else:
    from lib.mpu6050 import MPU6050
    from lib.neopixel import NeoPixel
    from lib.ble_peripheral import BLESimplePeripheral
    import bluetooth

    IS_LOCAL = False

BLE_CONNECT_LOOP_SLEEP_MS = 1000  # Sleep duration between BLE connection attempts in milliseconds
BLE_CONNECT_TIMEOUT_MS = 10000  # Timeout for BLE connection attempts in milliseconds

LOOP_SLEEP_MS = 100  # Sleep duration between iterations in milliseconds

# Adjust these pins to match the wiring and board variant.
I2C_ID_1 = 0
I2C_ID_2 = 1
SCL_PIN = 1
SDA_PIN = 0
I2C_FREQUENCY = 400_000
NEOPIXEL_PIN = 16
NEOPIXEL_COUNT1 = 2
NEOPIXEL_COUNT2 = 2

MIN_ACCELERATION = 0.0
MAX_ACCELERATION = 2.0

if IS_LOCAL:
    logger.debug("IS_LOCAL")
    i2c_1 = 1
    i2c_2 = 2
    neopixel_pin1 = None
    neopixel_pin2 = None
else:
    i2c_1 = I2C(
        I2C_ID_1,
        scl=Pin(SCL_PIN),
        sda=Pin(SDA_PIN),
        freq=I2C_FREQUENCY,
    )
    i2c_2 = I2C(
        I2C_ID_2,
        scl=Pin(SCL_PIN),
        sda=Pin(SDA_PIN),
        freq=I2C_FREQUENCY,
    )
    neopixel_pin1 = Pin(NEOPIXEL_PIN)
    neopixel_pin2 = Pin(NEOPIXEL_PIN)

pixels1 = NeoPixel(neopixel_pin1, NEOPIXEL_COUNT1)
pixels2 = NeoPixel(neopixel_pin2, NEOPIXEL_COUNT2)


def on_rx(data):
    logger.debug("Received data over BLE: %s", data)


async def main():
    sensor_1 = MPU6050(i2c_1)  # type: ignore[reportArgumentType]
    sensor_2 = MPU6050(i2c_2)  # type: ignore[reportArgumentType]

    seesaw1 = Seesaw("Seesaw 1", pixels1)
    seesaw2 = Seesaw("Seesaw 2", pixels2)

    # Setup BLE bluetooth and wait for connections
    ble = bluetooth.BLE()
    peripheral = BLESimplePeripheral(ble)

    peripheral.on_write(on_rx)

    # Wait for BLE connection if not running locally
    if not IS_LOCAL:
        start_time = time.ticks_ms()
        while not peripheral.is_connected() \
                and time.ticks_ms() - start_time < BLE_CONNECT_TIMEOUT_MS:
            logger.info("Waiting for BLE connection...")
            await sleep_ms(BLE_CONNECT_LOOP_SLEEP_MS)
        logger.info("BLE connected.")
    else:
        logger.info("Running in local mode, skipping BLE.")

    logger.debug("Starting seesaw task...")
    asyncio.create_task(seesaw1.run())
    asyncio.create_task(seesaw2.run())

    speed = 0
    toggle = 1
    while True:
        logger.debug("Main loop")
        seesaw1.set_speed(speed)
        if speed >= 100:
            toggle = -1
        elif speed <= 0:
            toggle = 1
        speed += toggle
        await sleep_ms(LOOP_SLEEP_MSzx)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
