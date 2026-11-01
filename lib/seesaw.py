from lib.logging import getLogger
try:
    from asyncio import sleep_ms
except ImportError:
    import asyncio

    async def sleep_ms(milliseconds: int, /) -> None:
        await asyncio.sleep(milliseconds / 1000)


logger = getLogger("seesaw")


LOOP_SLEEP_MS = 1000  # Sleep duration between iterations in milliseconds
COLOR = (255, 0, 0)  # Color to display when acceleration is above the threshold

class Seesaw:
    def __init__(self, name, pixel_strip):
        self.name = name
        self.running = False
        self.pixel_strip = pixel_strip
        self.sleep_duration = LOOP_SLEEP_MS
        self.pixel_strip.fill((0, 0, 0))
        self.pixel_strip.write()

    async def run(self):
        logger.debug("run() called")
        self.running = True
        self.pixel_strip[0] = COLOR
        self.pixel_strip.write()
        toggle = 1
        color = 255
        while self.running:
            if color == 255:
                toggle = -1
            elif color == 0:
                toggle = 1
            color += toggle
            self.pixel_strip[0] = (color, 0, 0)
            self.pixel_strip[1] = (255 - color, 0, 0)
            self.pixel_strip.write()
            await sleep_ms(self.sleep_duration)

        self.pixel_strip.fill((0, 0, 0))
        self.pixel_strip.write()

    def stop(self):
        logger.debug("%s: stop() called", self.name)
        self.running = False

    def set_speed(self, speed):
        logger.debug("%s: set_speed() called with speed: %d", self.name, speed)
        if speed <= 0:
            self.sleep_duration = LOOP_SLEEP_MS
        else:
            self.sleep_duration = max(10, LOOP_SLEEP_MS - int(LOOP_SLEEP_MS * (speed / 100)))
