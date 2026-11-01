import time
import bluetooth
from lib.ble_central import BLESimpleCentral

ble = bluetooth.BLE()
central = BLESimpleCentral(ble)
device_not_found = False



def on_scan(addr_type, addr, name):
    if addr_type is not None:
        print("Found peripheral:", addr_type, addr, name)
        central.connect()
    else:
        global device_not_found
        device_not_found = True
        print("No peripheral found.")


def connect_to_peripheral():
    global device_not_found
    device_not_found = False
    central.scan(callback=on_scan)
    while not central.is_connected():
        if device_not_found:
            return False
        else:
            time.sleep_ms(100)

    return True



def init():
    pass


def main():
    if connect_to_peripheral():
        print("Connected to peripheral.")
    else:
        print("Failed to connect to peripheral.")

if __name__ == "__main__":
    init()
    main()
