#!/usr/bin/python

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPgetCR.py: get each day's output data and store it locally)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python NEPgetCR.py serno
#   (serno = micro inverter serial number, as registered with nepviewer.com)

import sys
import os
import requests
from datetime import datetime, timedelta

max_empty = 1  # more consecutive days without data? => stop program

if len(sys.argv) != 2 or not sys.argv[1].isalnum() or len(sys.argv[1]) != 8:
    raise SystemExit(f"Usage: {argv[0]} serno")

sn = sys.argv[1]

empty_files = []
current_date = datetime.now()

while True:
    current_date -= timedelta(days=1)
    ymd = current_date.strftime("%Y-%m-%d")

    fn = f"{sn}_{ymd}.json"
    if os.path.isfile(fn):
        break

    print(f"{ymd} ... ", end="")
    ymd_no_dash = ymd.replace("-", "")
    url = f"https://user2.nepviewer.com/pv_monitor/proxy/history/{sn}/{ymd_no_dash}/{ymd_no_dash}/0/1/2"

    response = requests.get(url)
    if response.status_code != 200:
        print("failed!")
        break

    with open(fn, 'wb') as file:
        file.write(response.content)

    if os.path.getsize(fn) < 40:
        print("empty")
        empty_files.append(fn)
    else:
        print("okay")
        empty_files = []

    if len(empty_files) > max_empty:
        break

for file in empty_files:
    os.remove(file)

# converted from *.pl using https://www.codeconvert.ai/perl-to-python-converter
