#!/usr/bin/python3

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPviewerCR.py)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPviewerCR.py serno [yyyymmdd]
#   (serno = micro inverter serial number, as registered with nepviewer.com)

from sys import argv
from datetime import datetime
import urllib.request
import json
import re
import matplotlib.pyplot as plt
from matplotlib.dates import (datestr2num,DateFormatter)

# check params:
if len(argv)==2 or len(argv)==3 and re.match('^20\\d{6}$',argv[2]):
    serno = argv[1]
    if len(argv)>2: date = argv[2]
    else:
        now = datetime.today()
        date = '%04d%02d%02d' % (now.year, now.month, now.day)
else: raise SystemExit(f'Usage: {argv[0]} serno [yyyymmdd]')

# load data:
what = f'{serno} on {date}'
url = 'http://user.nepviewer.com/pv_monitor/proxy/' \
    + f'history/{serno}/{date}/{date}/0/1/2'
data = json.loads(urllib.request.urlopen(url).read())['data']
if not data: raise SystemExit(f'No data available for {what}')
time_s = []
w_s = []
kwh_s = []
for line in data:
    date,time,kw,dc,ac,x1,hz,c,kwh,x2,s1,s2 = line.split()
    time_s.append(datestr2num(time))
    w_s.append(int(float(kw)*1000))
    kwh_s.append(float(kwh))

# do plot:
color_s = [ 'blue', 'orange' ]
fig,ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(time_s,w_s  ,marker='.',color=color_s[0])
ax2.plot(time_s,kwh_s,marker='.',color=color_s[1])
ax1.set_ylabel('W'  ,color=color_s[0])
ax2.set_ylabel('kWh',color=color_s[1])
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
plt.title(what)
plt.show()
