# UPSplus v5 Battery Logger V1.0

Logs uptime, battery voltage, device wattage and battery %remaining from the
GeeekPi UPSv5 (EP-0136) board, connected to a Raspberry Pi,and writes to a
timestamped CSV file for optional graphing via Pandas (if installed).

## Usage: 
'python3 upspv5-batt-logger.py' - logs to local [timestamp].csv file
'python3 upspv5-batt-logger.py file.csv "[test batt label]"' - graph results as local png images

Use to capture battery discharge profile. Run immmediately after a fresh booting
after a full charge for best results. Recommend enablling 'Overlay FS' if using
RasPi Debian Buster to make the FSread-only w/ RAM disk. This prevents FS damage
when battery power becomes low, causing power outages. 
