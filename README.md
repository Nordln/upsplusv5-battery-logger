# UPSplus v5 Battery Logger V1.0
Author: Ed Watson (mail@edwilldesign.com)

Logs uptime, battery voltage, device wattage and battery %remaining from the
GeeekPi UPSv5 (EP-0136) board connected to a Raspberry Pi, and writes to a
timestamped CSV file for optional graphing via Pandas/Matplotlib (if installed). Built 
and tested on a Raspberry Pi4 8gb.

Included are example graphs pngs, built from a 4-hour capture of running batteries down.

## Usage: 
* 'python3 upspv5-batt-logger.py' - logs to local [timestamp].csv file
* 'python3 upspv5-batt-logger.py file.csv "[label for graph title]"' - graph results as local png images

Use to capture battery discharge profile. Run immmediately after a fresh booting
after a full charge for best results. Recommend enablling 'Overlay FS' if using
RasPi Debian Buster to make the FSread-only w/ RAM disk. This prevents FS damage
when battery power becomes low and starts causing power outages. 
