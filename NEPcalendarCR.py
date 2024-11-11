#!/usr/bin/python3

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPcalendarCR.py: build *.png calendars from NEPgetCR.pl's *.json data)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPcalendarCR.py *.json

colorful = False  # set to True for green-to-red color coded energy bars

import json
from sys import argv

import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

month = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def plot_month(ax, m, kwh):
    # make each month 31 days wide, and fill in possible gaps:
    for d in range(1, 32):
        if not d in kwh:
            kwh[d] = 0
    total = int(sum(kwh.values()))
    high = f"(max/d={max(kwh.values()):.1f})"
    if colorful:
        color = []
        for d in kwh:  # hue: max:0=red to min:1/3=green
            color.append(hsv_to_rgb(((1 - kwh[d] / max_kwh_per_day) / 3, 1, 1)))
        ax.bar(kwh.keys(), kwh.values(), color=color)
    else:
        ax.bar(kwh.keys(), kwh.values())
    ax.set_ylim(0, max_kwh_per_day)
    ax.set_title(f"{month[m-1]}: {total:.0f} kWh {high}", y=-0.11)
    return total


def plot_calendar(y, kwh):
    cols, rows = 3, 4
    fig, ax = plt.subplots(rows, cols, figsize=(10, 10), layout="constrained")
    total = 0
    for m in kwh:
        total += plot_month(ax[(m - 1) // cols][(m - 1) % cols], m, kwh[m])
    fig.suptitle(f"{y}: {total:.0f} kWh", fontweight="bold")
    for a in ax.ravel():
        a.set_axis_off()
    fn = f"{y}.png"
    print("Writing", fn, "...")
    plt.savefig(fn)


# load data:
kwh = {}
max_kwh_per_day = 0
for fn in argv[1:]:
    with open(fn, "r") as file:
        d = json.load(file)["data"]
        if not d:
            continue
        d = [x for x in d if x]  # strip empty rows
        f = d[-1].split()  # day's total is in last row
        y, m, d = [int(x) for x in f[0].split("-")]
        k = float(f[8])
        if not y in kwh:
            kwh[y] = {}
        if not m in kwh[y]:
            kwh[y][m] = {}
        kwh[y][m][d] = k
        if k > max_kwh_per_day:
            max_kwh_per_day = k

# plot data:
for y in kwh:
    plot_calendar(y, kwh[y])
