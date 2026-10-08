"""ESP32 WROOM USB and Pixhawk telemetry check.

Runs after reset as /main.py. Receives only: it cannot arm or move the drone.
"""

import sys
import time
from machine import UART

from mavlink_rx import HeartbeatParser


# ESP32 WROOM Dev Board 32S: UART1 keeps UART0 free for the USB REPL.
# Wire Pixhawk TELEM TX -> ESP32 GPIO32 (RX), and GND -> GND.
# GPIO33 is allocated as UART TX but deliberately left unconnected for now.
UART_ID = 1
UART_BAUD = 57600
UART_RX_GPIO = 32
UART_TX_GPIO = 33


def main():
    print("BANSHEE ESP32 MicroPython check")
    print("Runtime:", sys.platform)
    print("Listening for Pixhawk MAVLink HEARTBEAT on GPIO", UART_RX_GPIO)
    uart = UART(
        UART_ID, baudrate=UART_BAUD,
        tx=UART_TX_GPIO, rx=UART_RX_GPIO, timeout=0,
    )
    parser = HeartbeatParser()
    last_report = time.ticks_ms()
    byte_count = 0
    heartbeat_count = 0

    while True:
        if uart.any():
            data = uart.read(256)
            if data:
                byte_count += len(data)
                for heartbeat in parser.feed(data):
                    heartbeat_count += 1
                    print("HEARTBEAT", heartbeat)

        now = time.ticks_ms()
        if time.ticks_diff(now, last_report) >= 5000:
            print("Alive; UART bytes:", byte_count,
                  "valid heartbeats:", heartbeat_count)
            last_report = now
        time.sleep_ms(20)


if __name__ == "__main__":
    main()
