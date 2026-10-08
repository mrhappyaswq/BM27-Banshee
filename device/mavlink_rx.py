"""Small read-only MAVLink HEARTBEAT decoder for MicroPython.

Supports MAVLink 1 and 2 framing, including the optional MAVLink 2 signature.
This is not a general-purpose MAVLink library and never sends commands.
"""

HEARTBEAT_CRC_EXTRA = 50


def _crc_step(crc, value):
    tmp = (value ^ (crc & 0xFF)) & 0xFF
    tmp ^= (tmp << 4) & 0xFF
    return ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF


def _heartbeat_crc(frame, payload_end):
    crc = 0xFFFF
    for value in frame[1:payload_end]:
        crc = _crc_step(crc, value)
    return _crc_step(crc, HEARTBEAT_CRC_EXTRA)


class HeartbeatParser:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data):
        """Return decoded heartbeat dictionaries from new UART bytes."""
        if not data:
            return []
        buf = self.buffer
        buf.extend(data)
        heartbeats = []

        while buf:
            if buf[0] not in (0xFE, 0xFD):
                del buf[0]
                continue

            v2 = buf[0] == 0xFD
            header_size = 10 if v2 else 6
            if len(buf) < header_size:
                break

            payload_size = buf[1]
            signed = v2 and (buf[2] & 0x01) != 0
            frame_size = header_size + payload_size + 2 + (13 if signed else 0)
            if len(buf) < frame_size:
                break

            # Unknown MAVLink 2 incompatibility flags require the packet
            # to be ignored; bit 0 is the known signing flag.
            if v2 and (buf[2] & 0xFE):
                del buf[:frame_size]
                continue

            message_id = (buf[7] | buf[8] << 8 | buf[9] << 16) if v2 else buf[5]
            if message_id != 0 or payload_size < 9:
                del buf[:frame_size]
                continue

            payload_end = header_size + payload_size
            expected_crc = buf[payload_end] | (buf[payload_end + 1] << 8)
            if _heartbeat_crc(buf, payload_end) != expected_crc:
                # Shift one byte so a valid frame inside corrupt data can
                # still be found.
                del buf[0]
                continue

            p = header_size
            custom_mode = (
                buf[p] | (buf[p + 1] << 8) |
                (buf[p + 2] << 16) | (buf[p + 3] << 24)
            )
            heartbeats.append({
                "system_id": buf[5] if v2 else buf[3],
                "component_id": buf[6] if v2 else buf[4],
                "vehicle_type": buf[p + 4],
                "autopilot": buf[p + 5],
                "base_mode": buf[p + 6],
                "custom_mode": custom_mode,
                "system_status": buf[p + 7],
            })
            del buf[:frame_size]

        return heartbeats
