"""Small host-side stand-in for MicroPython's bluetooth module."""

import lib.logging as logging

logger = logging.getLogger("mock.bluetooth")


class UUID:
    def __init__(self, value):
        self.value = value

    def __bytes__(self):
        if isinstance(self.value, int):
            size = 2 if self.value <= 0xFFFF else 4
            return self.value.to_bytes(size, "little")
        return bytes.fromhex(self.value.replace("-", ""))[::-1]

    def __eq__(self, other):
        return isinstance(other, UUID) and bytes(self) == bytes(other)

    def __hash__(self):
        return hash(bytes(self))

    def __repr__(self):
        return f"UUID({self.value!r})"


class BLE:
    def __init__(self):
        self._active = False
        self._irq_handler = None
        self._next_handle = 1
        self._values = {}
        self.notifications = []

    def active(self, state=None):
        if state is not None:
            self._active = state
        return self._active

    def irq(self, handler):
        self._irq_handler = handler

    def gap_advertise(self, interval_us, adv_data=None):
        logger.debug("BLE: advertising every %s us: %s", interval_us, adv_data)

    def gap_scan(self, duration_ms, interval_us=0, window_us=0):
        logger.debug("BLE: scan requested for %s ms", duration_ms)

    def gap_connect(self, addr_type, addr):
        logger.debug("BLE: connect requested to %s, %s", addr_type, addr)

    def gap_disconnect(self, conn_handle):
        logger.debug("BLE: disconnect requested for %s", conn_handle)

    def gatts_register_services(self, services):
        handles = []
        for _, characteristics in services:
            characteristic_handles = []
            for _, _ in characteristics:
                characteristic_handles.append(self._next_handle)
                self._next_handle += 1
            handles.append(tuple(characteristic_handles))
        return tuple(handles)

    def gatts_read(self, value_handle):
        return self._values.get(value_handle, b"")

    def gatts_notify(self, conn_handle, value_handle, data):
        notification = (conn_handle, value_handle, bytes(data))
        self.notifications.append(notification)
        logger.debug("BLE: notification %s", notification)

    def gattc_discover_services(self, conn_handle):
        logger.debug("BLE: discovering services for %s", conn_handle)

    def gattc_discover_characteristics(self, conn_handle, start_handle, end_handle):
        logger.debug("BLE: discovering characteristics for %s", conn_handle)

    def gattc_write(self, conn_handle, value_handle, data, mode):
        logger.debug("BLE: write %s, %s, %s, mode=%s", conn_handle, value_handle, bytes(data), mode)
