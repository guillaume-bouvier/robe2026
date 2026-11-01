# NeoPixel driver for MicroPython
# MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared
from machine import bitstream
import time


def _get_gamma_table():
    """Return gamma-corrected values for all 8-bit input values."""
    gamma = 2.8
    return tuple(int(pow(i / 255, gamma) * 255 + 0.5) for i in range(256))


class NeoPixel:
    # G R B W
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3, timing=1):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
        # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
        self.timing = (
            ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900))
            if isinstance(timing, int)
            else timing
        )
        self.gamma_table = _get_gamma_table()

    def __len__(self):
        return self.n

    def __setitem__(self, i, v):
        offset = i * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = self.gamma_table[v[i]]

    def __getitem__(self, i):
        offset = i * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]] for i in range(self.bpp))

    def fill(self, v):
        b = self.buf
        l = len(self.buf)
        bpp = self.bpp
        for i in range(bpp):
            c = self.gamma_table[v[i]]
            j = self.ORDER[i]
            while j < l:
                b[j] = c
                j += bpp

    def write(self):
        # BITSTREAM_TYPE_HIGH_LOW = 0

        bitstream(self.pin, 0, self.timing, self.buf)


    def set_no_gamma(self, i, v):
        """Set pixel value without gamma correction."""
        offset = i * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = v[i]


class SeeSaw:
    def __init__(self, strip, pairs):
        self.strip = strip
        self.pairs = pairs # [(0, 1), (2, 3), ...] for each pair of pixels to mirror
        bpp = strip.bpp
        self.pair_offsets = tuple((a * bpp, b * bpp) for a, b in pairs)
        self.channel_offsets = strip.ORDER[:3]
        self.i = 1 # Start with 1 to avoid issue in update() when i=0 and increment is positive
        self.increment = 1
        self.increase = True
        self.last_update_time = 0
        self.speed = 100

    def set_speed(self, speed):
        """Set the speed of the animation."""
        self.speed = speed

    def set_increment(self, increment):
        """Set the increment value for the animation."""
        self.increment = increment

    def update(self):
        delta_ticks = time.ticks_diff(time.ticks_ms(), self.last_update_time)
        if delta_ticks < self.speed:
            return False
        self.last_update_time = time.ticks_ms()

        # Avoid per-pixel method calls and temporary tuples for large strips.
        buf = self.strip.buf
        gamma = self.strip.gamma_table

        red_a = gamma[self.i]
        red_b = gamma[255 - self.i]
        zero = gamma[0]
        r, g, b = self.channel_offsets
        for a, b_offset in self.pair_offsets:
            buf[a + r] = red_a
            buf[a + g] = zero
            buf[a + b] = zero
            buf[b_offset + r] = red_b
            buf[b_offset + g] = zero
            buf[b_offset + b] = zero
        self.strip.write()

        if self.i >= 255 - self.increment:
            self.increase = False
        elif self.i <= 0 + self.increment:
            self.increase = True

        self.i += self.increment if self.increase else -self.increment

        return True

__version__ = '0.1.0'
