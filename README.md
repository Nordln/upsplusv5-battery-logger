# UPSplus v5 Battery Logger V1.1
Original author: Ed Watson (mail@edwilldesign.com)
Contributors: leandroalbero

Logs uptime, battery voltage, battery current, battery temperature, device wattage and
battery %remaining from the GeeekPi UPSv5 (EP-0136) board connected to a Raspberry Pi, 
and writes to a timestamped CSV file for optional graphing via Pandas/Matplotlib 
(if installed). Built and tested on a Raspberry Pi4b 8gb running RaspiOS 2021-03-04 
(Debian Buster) w/ UPSplusV5 FW Ver.3.

Included are example graphs pngs, built from a 4-hour capture of running batteries down.

## Dependances:
* libatlas (needed for numpy): `apt-get -y install libatlas-base-dev`
* Pandas (which includes numpy) and matplotlib: `pip3 install pandas matplotlib`

## Usage: 
* 'python3 upspv5-batt-logger.py' - logs to local [timestamp].csv file
* 'python3 upspv5-batt-logger.py file.csv "[label for graph title]"' - graph results as local png images

## Method:
Run immmediately after a fresh booting after a full charge for best results. 
Recommend running from a USB stick and enabling 'Overlay FS' if using RasPi 
Debian Buster to make the FSread-only w/ RAM disk. This prevents FS damage 
when battery power becomes low and starts causing power outages. 
