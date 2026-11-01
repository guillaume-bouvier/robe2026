"""Host-only NeoPixel replacement for testing without hardware."""

import lib.logging as logging

logger = logging.getLogger("mock.neopixel")


def _get_gamma_table():
    gamma = 2.8
    return tuple(int(pow(i / 255, gamma) * 255 + 0.5) for i in range(256))


class NeoPixel:
    def __init__(self, _pin, n, bpp=3, timing=1):
        logger.debug("NeoPixel: initialized with n=%s, bpp=%s, timing=%s", n, bpp, timing)
        self.n = n
        self.bpp = bpp
        self.timing = timing
        self.gamma_table = _get_gamma_table()
        self.buf = [tuple(0 for _ in range(bpp)) for _ in range(n)]
        self.last_write = None

    def __len__(self):
        logger.debug("NeoPixel: __len__ called, returning %s", self.n)
        return self.n

    def __setitem__(self, index, color):
        logger.debug("NeoPixel: __setitem__ called with index=%s, color=%s", index, color)
        self.buf[index] = tuple(self.gamma_table[value] for value in color)

    def __getitem__(self, index):
        logger.debug("NeoPixel: __getitem__ called with index=%s", index)
        return self.buf[index]

    def fill(self, color):
        logger.debug("NeoPixel: fill called with color=%s", color)
        value = tuple(self.gamma_table[value] for value in color)
        self.buf = [value for _ in range(self.n)]

    def write(self):
        self.last_write = tuple(self.buf)
        logger.debug("NeoPixel: %s", self.last_write)
