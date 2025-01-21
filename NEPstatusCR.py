#!/usr/bin/python

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPstatusCR.py)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python NEPstatusCR.py sn ...
#   (sn = micro inverter serial number, as registered with nepviewer.com)

import re
import sys

import requests

for sn in sys.argv[1:]:
    data = requests.get(f"http://user2.nepviewer.com/pv_monitor/proxy/status/{sn}/0/2/").text
    match = re.search(r'"LastUpDate":"([^"]+).*"now":(\d+).*"today":(\d+).*"total_status":(\d+)', data)
    if match:
        last_update, now, today, total_status = match.groups()
        print(f"{int(now)} W / {int(today) / 1000} kWh on {last_update} ({int(total_status) / 1000} kWh total)")
