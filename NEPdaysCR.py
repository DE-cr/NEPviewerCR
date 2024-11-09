#!/usr/bin/python3

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPdaysCR.py: plot course of daily output from NEPgetCR.pl's *.json)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPdaysCR.py *.json

import json
from statistics import mean
from sys import argv

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

days_to_average = 30  # adjust, if you prefer a different averaging window

# read data:
date, kwh, kwh_avg, w_max, w_max_avg = [], [], [], [], []
total = 0
for fn in argv[1:]:
    with open(fn, "r") as file:
        d = json.load(file)["data"]
        if not d:
            continue
        d = [x for x in d if x]  # strip empty rows
        f = d[-1].split()  # day's total is in last row
        date.append(mdates.datestr2num(f[0]))
        k = float(f[8])
        total += k
        kwh.append(k)
        kwh_avg.append(mean(kwh[-days_to_average:]))
        w_max.append(max([1000 * float(x.split()[2]) for x in d]))
        w_max_avg.append(mean(w_max[-days_to_average:]))

# plot data:
ax = plt.gca()
ax.grid(which="both")
ax.plot(date, kwh)
ax.plot(date, kwh_avg, lw=3)
ax.set_ylabel("kWh")
# max(W) faintly on 2nd y axis:
alpha = 0.25
ax2 = ax.twinx()
ax2.grid(axis="y", alpha=alpha)
ax2.plot(date, w_max, alpha=alpha)
ax2.plot(date, w_max_avg, lw=3, alpha=alpha)
ax2.set_ylabel("max(W)", alpha=alpha)
ax2.tick_params(colors=str(1 - alpha))
# format x tics:
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 13)))  # every year
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%m"))
for label in ax.get_xticklabels(which="major"):
    label.set(rotation=90)
ax.set_title(f"Total = {total:.0f} kWh")
plt.show()
