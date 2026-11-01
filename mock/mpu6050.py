"""Host-only MPU6050 replacement for testing without hardware."""

import lib.logging as logging

logger = logging.getLogger("mock.mpu6050")


class MPU6050:
    def __init__(self, _i2c):
        logger.debug("MPU6050: initialized")
        self.address = _i2c
        self.sample = 0

    def read_accel_data(self):
        logger.debug("MPU6050: read_accel_data() called")
        self.sample += 1
        return {"x": 0.01 * self.sample, "y": 0.02, "z": 1.0}

    def read_gyro_data(self):
        logger.debug("MPU6050: read_gyro_data() called")
        return {"x": 0.1, "y": 0.0, "z": -0.05}

    def read_temperature(self):
        logger.debug("MPU6050: read_temperature() called")
        return 24.0 + (self.sample * 0.1)
