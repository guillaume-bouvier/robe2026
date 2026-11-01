"""Host-only BLE UART central mock."""


class BLESimpleCentral:
    def __init__(self, ble):
        self._ble = ble
        self._connected = False
        self._scan_callback = None
        self._connect_callback = None
        self._notify_callback = None
        self._ble.active(True)

    def is_connected(self):
        return self._connected

    def scan(self, callback=None):
        self._scan_callback = callback
        self._ble.gap_scan(20000, 16, 16)

    def connect(self, addr_type=None, addr=None, callback=None):
        if addr_type is None or addr is None:
            return False
        self._connect_callback = callback
        self._ble.gap_connect(addr_type, addr)
        self._connected = True
        if callback:
            callback()
        return True

    def disconnect(self):
        if self._connected:
            self._ble.gap_disconnect(0)
        self._connected = False

    def write(self, value, response=False):
        if self._connected:
            self._ble.gattc_write(0, 1, value, 1 if response else 0)

    def on_notify(self, callback):
        self._notify_callback = callback
