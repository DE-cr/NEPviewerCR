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
    f = []
    f = line.split()
    if len(f) >= 9:
        date,time,kw,dc,ac,x1,hz,c,kwh = f[:9]
        time_s.append(datestr2num(time))
        w_s.append(int(float(kw)*1000))
        kwh_s.append(float(kwh))

# do plot:
color_s = plt.rcParams['axes.prop_cycle'].by_key()['color']
fig,ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(time_s,w_s  ,marker='.',color=color_s[0],lw=1)
ax2.plot(time_s,kwh_s,marker='.',color=color_s[1],lw=1)
ax1.set_ylabel('Power [W]'   ,color=color_s[0])
ax2.set_ylabel('Energy [kWh]',color=color_s[1])
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
plt.xticks([min(time_s),max(time_s)])
plt.title(what)
plt.show()
