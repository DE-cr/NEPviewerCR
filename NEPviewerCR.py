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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import datestr2num,DateFormatter
from scipy.interpolate import make_interp_spline

smooth = True  # set to False for jagged curves

def smoothen(x,y,k=3,n=1000):
    if not smooth: return x,y
    spline = make_interp_spline(x,y,k=k)
    x_smooth = np.linspace(x[0],x[-1],n)
    y_smooth = spline(x_smooth)
    return x_smooth,y_smooth

def my_plot(ax,x,y,c,l):
    ax.scatter(x,y,marker='.',color=c)
    ax.plot(*smoothen(x,y),lw=1,color=c)
    ax.set_ylabel(l,color=c)

# check params:
if len(argv)==2 or len(argv)==3 and re.match('^20\\d{6}$',argv[2]):
    serno = argv[1]
    if len(argv)>2: date = argv[2]
    else:
        now = datetime.today()
        date = '%04d%02d%02d' % (now.year, now.month, now.day)
else: raise SystemExit(f'Usage: {argv[0]} serno [yyyymmdd]')

# load data:
what = f'SN={serno} on {date[0:4]}-{date[4:6]}-{date[6:]}'
url = 'http://user2.nepviewer.com/pv_monitor/proxy/' \
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
my_plot(ax1,time_s,w_s  ,color_s[0],'Power [W]')
my_plot(ax2,time_s,kwh_s,color_s[1],'Energy [kWh]')
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
plt.xticks([min(time_s),max(time_s)])
what += f'\n({max(kwh_s)} kWh, max. {max(w_s)} W, {len(w_s)} samples)'
plt.title(what)
plt.show()
