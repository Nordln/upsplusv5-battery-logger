#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UPSplus v5 Battery Prometheus Exporter

- Reads from GeeekPi UPSv5 (EP-0136) via I2C + INA219.
- Exposes metrics over HTTP for Prometheus/Grafana instead of CSV.

Original CSV logger by Ed Watson.
Exporter adaptation for Grafana/Prometheus.
"""

import time
import sys

import smbus
from ina219 import INA219, DeviceRangeError
from prometheus_client import Gauge, start_http_server

# --------- Original constants ----------
I2C_DEVICE_BUS = 1
SMB_DEVICE_ADDR = 0x17
INA_DEVICE_ADDR = 0x40
INA_BATT_ADDR = 0x45
DELAY = 5  # seconds between reads
STOP_ON_ERR = 0  # keep running on error

# --------- I2C / INA219 setup ----------
bus = smbus.SMBus(I2C_DEVICE_BUS)

# Shunt values copied from your script
ina = INA219(0.00725, busnum=I2C_DEVICE_BUS, address=INA_DEVICE_ADDR)
ina.configure()
ina_batteries = INA219(0.005, busnum=I2C_DEVICE_BUS, address=INA_BATT_ADDR)
ina_batteries.configure()

# --------- Prometheus metrics ----------
# Battery-related
UPS_VOLTAGE_MV = Gauge(
    "upsplus_voltage_mv",
    "Battery voltage from UPS Plus v5 in millivolts",
)
UPS_POWER_MW = Gauge(
    "upsplus_power_mw",
    "Raspberry Pi power draw measured by UPS Plus v5 in milliwatts",
)
UPS_REMAINING_PERCENT = Gauge(
    "upsplus_remaining_percent",
    "Remaining battery percentage reported by UPS Plus v5",
)
UPS_BATT_CURRENT_MA = Gauge(
    "upsplus_battery_current_ma",
    "Battery current from UPS Plus v5 in milliamps (positive = discharge, negative = charge)",
)
UPS_BATT_TEMP_C = Gauge(
    "upsplus_battery_temp_celsius",
    "Battery temperature reported by UPS Plus v5 in degrees Celsius",
)

# Time / uptime reported by UPS board
UPS_TIME_SECONDS = Gauge(
    "upsplus_time_seconds",
    "Time value (seconds) provided by UPS Plus v5 (board register, not necessarily Unix time)",
)

def read_values():
    """
    Read all raw values from the UPS board and INA219 sensors.
    Mirrors the CSV row from the original script.
    Returns a dict of parsed values.
    """
    a_receive_buf = [0x00]

    # Read 1..254 just like original script
    for i in range(1, 255):
        a_receive_buf.append(bus.read_byte_data(SMB_DEVICE_ADDR, i))

    # Same fields as your csvdata list:
    # Time (s) = [39..36]
    time_s = (a_receive_buf[39] << 24 |
              a_receive_buf[38] << 16 |
              a_receive_buf[37] << 8  |
              a_receive_buf[36])

    # Volts (mV) = [6..5]
    volts_mv = (a_receive_buf[6] << 8 | a_receive_buf[5])

    # Remaining % = [20..19]
    remaining_pct = (a_receive_buf[20] << 8 | a_receive_buf[19])

    # Batt Temp (ºC) = [12..11]
    batt_temp_c = (a_receive_buf[12] << 8 | a_receive_buf[11])

    # INA219 power and current (float values)
    try:
        power_mw = ina.power()  # mW
    except DeviceRangeError:
        power_mw = float("nan")

    try:
        batt_current_ma = ina_batteries.current()  # mA
    except DeviceRangeError:
        batt_current_ma = float("nan")

    return {
        "time_s": float(time_s),
        "volts_mv": float(volts_mv),
        "remaining_pct": float(remaining_pct),
        "batt_temp_c": float(batt_temp_c),
        "power_mw": float(power_mw),
        "batt_current_ma": float(batt_current_ma),
    }


def update_metrics():
    """Read from UPS and update Prometheus gauges."""
    values = read_values()

    UPS_TIME_SECONDS.set(values["time_s"])
    UPS_VOLTAGE_MV.set(values["volts_mv"])
    UPS_POWER_MW.set(values["power_mw"])
    UPS_REMAINING_PERCENT.set(values["remaining_pct"])
    UPS_BATT_CURRENT_MA.set(values["batt_current_ma"])
    UPS_BATT_TEMP_C.set(values["batt_temp_c"])

    # Optional: log to stdout for debugging
    print(
        f'time={values["time_s"]:.0f}s '
        f'voltage={values["volts_mv"]:.0f}mV '
        f'power={values["power_mw"]:.0f}mW '
        f'remaining={values["remaining_pct"]:.0f}% '
        f'batt_current={values["batt_current_ma"]:.0f}mA '
        f'batt_temp={values["batt_temp_c"]:.0f}C'
    )


def main():
    # Start Prometheus HTTP server on port 9105
    port = 9105
    if len(sys.argv) > 1:
        # allow overriding port: `python3 upsplus_exporter.py 9200`
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port '{sys.argv[1]}', using default {port}")

    print(f"Starting UPSPlus v5 Prometheus exporter on port {port} ...")
    start_http_server(port)

    while True:
        try:
            update_metrics()
            time.sleep(DELAY)
        except KeyboardInterrupt:
            print("Exiting on Ctrl+C")
            sys.exit(0)
        except Exception as e:
            print("Unexpected error:", e)
            if STOP_ON_ERR == 1:
                raise
            # If not stopping on error, just wait and retry
            time.sleep(DELAY)


if __name__ == "__main__":
    main()