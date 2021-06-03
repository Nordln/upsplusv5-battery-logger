#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UPSplus v5 Battery Logger V1.1
Original author: Ed Watson (mail@edwilldesign.com)
Contributors: leandroalbero

Logs uptime, battery voltage, device wattage and battery %remaining from the
GeeekPi UPSv5 (EP-0136) board, connected to a Raspberry Pi,and writes to a
timestamped CSV file for optional graphing via Pandas (if installed).

Usage:
'python3 upspv5-batt-logger.py' - logs to local [timestamp].csv file
'python3 upspv5-batt-logger.py file.csv "[label for graph title]"' - graph results as local png images

Use to capture battery discharge profile. Run immediately after booting the device
following a full charge for best results. Recommend enabling 'Overlay FS' if using
RasPi Debian Buster to make the FS read-only w/ RAM disk. This prevents FS damage
when battery power becomes low, causing power outages. 

Note: "% remaining" is not accurate during charging.
"""

import sys
import time
import io
import csv
from datetime import datetime

import smbus
from ina219 import INA219, DeviceRangeError

I2C_DEVICE_BUS = 1
SMB_DEVICE_ADDR = 0x17
INA_DEVICE_ADDR = 0x40
INA_BATT_ADDR = 0x45
DELAY = 5  # delay between I2C reads (in seconds)
STOP_ON_ERR = 0  # stop logging on bus read error

now = datetime.now()
T = now.strftime("%Y-%m-%d_%H%M%S")
CSV_FILE = "batt_log_" + T + ".csv"

bus = smbus.SMBus(I2C_DEVICE_BUS)
ina = INA219(0.00725, address=INA_DEVICE_ADDR)
ina.configure()
ina_batteries = INA219(0.005, address=INA_BATT_ADDR)
ina_batteries.configure()


def make_graph():
    # test for pandas, then graph file referenced as argument if available
    try:
        # check dependencies
        print("Checking: Pandas library installed.")
        import pandas as pd
        print("Checking: MatplotLib library installed.")
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter

        # buld and save voltage graph
        df = pd.read_csv(sys.argv[1])
        df['Time (H:M)'] = pd.to_datetime(df['Time (s)'], unit='s')

        df.plot(x="Time (H:M)", y=["Volts (mV)"], grid=True, color='Red')  # items to plot
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        plt.title("Time/voltage plot of " + str(sys.argv[2]))
        plt.savefig("Graph_voltage_" + sys.argv[1] + ".png")  # save as png

        # build and save voltage, wattage and % graphs
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1)
        df.plot(x="Time (H:M)", y=["Volts (mV)"], legend=True, ax=ax1, figsize=(10, 10), grid=True,
                color='Red')  # items to plot
        ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax1.set_title("Time/Voltage plot of " + str(sys.argv[2]))

        df.plot(x="Time (H:M)", y=["Power (mW)"], legend=True, ax=ax2, figsize=(10, 10), grid=True,
                color='Green')  # items to plot
        ax2.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax2.set_title("Time/Power plot of " + str(sys.argv[2]))

        df.plot(x="Time (H:M)", y=["Remaining %"], legend=True, ax=ax3, figsize=(10, 10), grid=True,
                color='Blue')  # items to plot
        ax3.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax3.set_title("Time/Remaining% plot of " + str(sys.argv[2]))

        df.plot(x="Time (H:M)", y=["Battery Current (mA)"], legend=True, ax=ax4, figsize=(10, 10), grid=True,
                color='Blue')  # items to plot
        ax4.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax4.set_title("Time/BattCurrent mA plot of " + str(sys.argv[2]))

        df.plot(x="Time (H:M)", y=["Batt. Temp (ºC)"], legend=True, ax=ax5, figsize=(10, 10), grid=True,
                color='Blue')  # items to plot
        ax5.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        ax5.set_title("Time/BattTempºC plot of " + str(sys.argv[2]))

        plt.tight_layout()
        plt.savefig("Graphs_full_" + sys.argv[1] + ".png")  # save as png

        print("Graphs saved sucessfully")

    except ImportError:
        print("Error: Cannot build graph - Pandas and/or matplotlib library not installed.")
        print("")
        print(
            "To install dependancies, use 'pip3 install pandas matplotlib'. If you encounter errors over the Pandas "
            "dependancy 'numpy', you are probably running Debian Buster on a Pi, and so also need to install OpenBLAS "
            "('apt-get install libatlas-base-dev")


def check_args():
    # test for graph argument, build graph, then exit
    if len(sys.argv) == 2:
        print("Error: Please enter a graph title in double-quotes after file name")
        sys.exit()

    if len(sys.argv) > 2:
        make_graph()
        sys.exit()


def create_file():
    # create csv file and write headers 
    with open(CSV_FILE, 'x', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        csvtitles = [
            "Time (s)",
            "Volts (mV)",
            "Power (mW)",
            "Remaining %",
            "Battery Current (mA)",
            "Batt. Temp (ºC)"]
        writer.writerow(csvtitles)
        print(csvtitles)


def main():
    check_args()
    create_file()
    while True:
        # Loop indefinately whilst reading and writing data, until user hits Ctrl-C 
        try:
            a_receive_buf = [0x00]
            for i in range(1, 255):
                a_receive_buf.append(bus.read_byte_data(SMB_DEVICE_ADDR, i))
            csvdata = [
                "%d" % (a_receive_buf[39] << 24 | a_receive_buf[38] << 16 | a_receive_buf[37] << 8 | a_receive_buf[36]),
                "%d" % (a_receive_buf[6] << 8 | a_receive_buf[5]),
                "%.0f" % ina.power(),
                "%d" % (a_receive_buf[20] << 8 | a_receive_buf[19]),
                "%.0f" % ina_batteries.current(),
                "%d" % (a_receive_buf[12] << 8 | a_receive_buf[11])]
            print(csvdata)
            with open(CSV_FILE, 'a', newline='') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(csvdata)
            time.sleep(DELAY)
        except KeyboardInterrupt:
            sys.exit()
        except:
            if STOP_ON_ERR == 1:
                print("Unexpected error:", sys.exc_info()[0])
                raise
            pass


main()

"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""
