#!/usr/bin/python3

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPpowertempCR.py: build *.png calendar from NEPjson2csvCR.py's *.csv)
# (showing power and module temperature distribution by month)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPpowertempCR.py file.csv

import re
from sys import argv

import matplotlib.pyplot as plt
import pandas as pd

# check params:
if len(argv) != 2:
    raise SystemExit(f"Usage: {argv[0]} file.csv")

# try to find serial number in file name given:
sn = re.search("[0-9a-f]{8}", argv[1])
sn = sn.group() if sn else "unknown"

df = pd.read_csv(argv[1])

# fix data types:
df.date = pd.to_datetime(df.date)
df.time = pd.to_datetime(df.time, format="%H:%M")

# create other helpful columns:
df["W"] = df.kW * 1000
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month
df["day"] = df.date.dt.day
df["hour"] = df.time.dt.hour
df["minute"] = df.time.dt.minute
df["hour_float"] = df.hour + df.minute / 60
df["hour_rounded"] = df.hour_float.round()

# save for later quick use:
# df.to_feather(argv[1].replace(".csv", ".feather"))

month_name = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

# let's plot:
alpha = 0.25  # for W dots and axis/grid
rows, cols = 4, 3
fig, ax = plt.subplots(
    rows, cols, figsize=(15, 15), sharex=True, sharey=True, layout="constrained"
)
for a in ax.flat:  # hide all months
    a.set_axis_off()
year_kwh = {}
for month in df.month.unique():
    dfm = df.query(f"month=={month}")
    row, col = (month - 1) // cols, (month - 1) % cols
    ax1 = ax[row][col]
    ax2 = ax1.twinx()
    ax1.set_axis_on()  # unhide axes for month with data
    for year in sorted(dfm.year.unique()):
        dfmy = dfm.query(f"year=={year}")
        k = dfmy.groupby("day").kWh.max()
        if not year in year_kwh:
            year_kwh[year] = 0
        year_kwh[year] += k.sum()
        x, y = [], []
        for hour in sorted(dfmy.hour_rounded.unique()):
            x.append(hour)
            y.append(dfmy[dfmy.hour_rounded == hour].temperature.mean())
        ax1.plot(x, y, lw=3, label=f"{year}: {k.sum():.0f} kWh")
        ax2.scatter(dfmy.hour_float, dfmy.W, 1, alpha=alpha)
    ax1.set_title(month_name[month - 1])
    ax1.legend()
    ax1.grid()
    ax1.set_xlim(0, 24)
    ax1.set_xticks(range(0, 25, 2))
    ax1.set_ylim(df.temperature.min(), df.temperature.max())
    if row == rows - 1:  # on bottom months row only
        ax1.set_xlabel("time of day [hour]")
    if col == 0:  # on leftmost months column only
        ax1.set_ylabel("mean system temperature", fontweight="bold")
    ax2.set_ylim(0, df.W.max())
    ax2.grid(axis="y", alpha=alpha)
    ax2.tick_params(colors=str(1 - alpha))
    # show secondary y axis on rightmost months column only:
    if col == cols - 1:
        ax2.set_ylabel("power [W]", alpha=alpha)
    else:
        ax2.yaxis.set_ticklabels([])
# add informative overall title:
kwh_s = ", ".join([f"{y}: {k:.0f} kWh" for y, k in year_kwh.items()])
plt.suptitle(f"SN={sn} ({kwh_s})", fontweight="bold")
plt.savefig(f"NEPviewerCR_{sn}.png")
plt.show()
