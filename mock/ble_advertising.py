"""Host-compatible BLE advertising payload helpers."""

import struct

from . import bluetooth


_ADV_TYPE_FLAGS = 0x01
_ADV_TYPE_NAME = 0x09
_ADV_TYPE_UUID16_COMPLETE = 0x03
_ADV_TYPE_UUID32_COMPLETE = 0x05
_ADV_TYPE_UUID128_COMPLETE = 0x07
_ADV_TYPE_APPEARANCE = 0x19


def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def append_field(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type) + value)

    flags = (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)
    append_field(_ADV_TYPE_FLAGS, struct.pack("B", flags))

    if name:
        append_field(_ADV_TYPE_NAME, name.encode())

    if services:
        for service in services:
            value = bytes(service)
            if len(value) == 2:
                append_field(_ADV_TYPE_UUID16_COMPLETE, value)
            elif len(value) == 4:
                append_field(_ADV_TYPE_UUID32_COMPLETE, value)
            elif len(value) == 16:
                append_field(_ADV_TYPE_UUID128_COMPLETE, value)

    if appearance:
        append_field(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    if len(payload) > 31:
        raise ValueError("advertising payload too large")
    return payload


def decode_field(payload, adv_type):
    result = []
    index = 0
    while index + 1 < len(payload):
        length = payload[index]
        if payload[index + 1] == adv_type:
            result.append(payload[index + 2 : index + length + 1])
        index += 1 + length
    return result


def decode_name(payload):
    fields = decode_field(payload, _ADV_TYPE_NAME)
    return fields[0].decode("utf-8") if fields else ""


def decode_services(payload):
    services = []
    for value in decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<h", value)[0]))
    for value in decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
        services.append(bluetooth.UUID(struct.unpack("<I", value)[0]))
    for value in decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
        services.append(bluetooth.UUID(value[::-1].hex()))
    return services
