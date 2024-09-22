#!/usr/bin/python3

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPviewerCR+.py)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPviewerCR+.py serno [yyyymmdd]
#   (serno = micro inverter serial number, as registered with nepviewer.com)

from sys import argv
from datetime import datetime
from urllib.request import urlopen
import json
import re
import matplotlib.pyplot as plt
from matplotlib.dates import (datestr2num,DateFormatter)
from matplotlib.gridspec import GridSpec

# check params:
if len(argv)==2 or len(argv)==3 and re.match('^20\\d{6}$',argv[2]):
    serno = argv[1]
    if len(argv)>2: date = argv[2]
    else:
        now = datetime.today()
        date = '%04d%02d%02d' % (now.year, now.month, now.day)
else: raise SystemExit(f'Usage: {argv[0]} serno [yyyymmdd]')

print('Fetching data...')
what = f'SN={serno} on {date[0:4]}-{date[4:6]}-{date[6:]}'
base_url = 'http://user.nepviewer.com/pv_monitor/proxy/'

# load day data:
url = f'{base_url }history/{serno}/{date}/{date}/0/1/2'
data = json.loads(urlopen(url).read())['data']
time_s = []
w_s = []
kwh_s = []
if data:
    for line in data:
        f = []
        f = line.split()
        if len(f) == 12:
            date,time,kw,dc,ac,x1,hz,c,kwh,x2,s1,s2 = f
            time_s.append(datestr2num(time))
            w_s.append(int(float(kw)*1000))
            kwh_s.append(float(kwh))

# prepare plots:
fig = plt.figure(layout="constrained",figsize=(19.2,10.8))
gs = GridSpec(3,2,figure=fig)
ax_d = fig.add_subplot(gs[:,0])
ax_w = fig.add_subplot(gs[0,1],frameon=False)
ax_m = fig.add_subplot(gs[1,1],frameon=False)
ax_y = fig.add_subplot(gs[2,1],frameon=False)
ax_d_kwh = ax_d.twinx()

# day power:
c = 'blue'
ax_d.plot(time_s,w_s,label='Power [W]',marker='.',color=c)
ax_d.tick_params(axis='y',colors=c)
ax_d_kwh.spines['left'].set_color(c)
# day energy:
c = 'orange'
ax_d_kwh.plot(time_s,kwh_s,label='Energy [kWh]',marker='.',color=c)
ax_d_kwh.tick_params(axis='y',colors=c)
ax_d_kwh.spines['right'].set_color(c)
# day plot config:
title = what
if w_s: title += f' ({max(kwh_s)} kWh, max. {max(w_s)} W, {len(w_s)} samples)'
ax_d.set_title(title)
ax_d.xaxis.set_major_formatter(DateFormatter('%H:%M'))
if time_s: ax_d.set_xticks([min(time_s),max(time_s)])
else: ax_d.text(0,0,'(no data)',color='red',va='center',ha='center')
# combine labels from d and d_kwh into d legend:
lines_d,labels_d = ax_d.get_legend_handles_labels()
lines_d_kwh,labels_d_kwh = ax_d_kwh.get_legend_handles_labels()
ax_d.legend(lines_d+lines_d_kwh,labels_d+labels_d_kwh,loc='upper left')

def bar_chart(what,ax):
    url = f'{base_url}{what}/{serno}/0/2/'
    data = json.loads(urlopen(url).read())['arr']
    x = []
    y = []
    sum = 0
    for line in data:
        if x or line[1]:
            x.append(line[0].replace('.','-'))
            y.append(line[1])
            sum += line[1]
    ax.set_title(f'kWh by {what} (total={sum})')
    bar = ax.bar(x,y)
    ax.bar_label(bar)
    ax.get_yaxis().set_visible(False)
    if not x: ax.text(0,0,'(no data)',color='red',va='center',ha='center')

bar_chart('week',ax_w)
bar_chart('month',ax_m)
bar_chart('year',ax_y)
# plt.savefig(f'{what.replace(" ","_")}.png')
plt.show()
