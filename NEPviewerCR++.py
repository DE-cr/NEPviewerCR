#!/usr/bin/env python
# coding: utf-8


# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPviewerCR++.py: get kWh/d values from NEP server and provide some plots)


import os
import requests
import calendar
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

# read NEP account info from environment:
account = os.environ["NEP_ACCOUNT"]
password = os.environ["NEP_PASSWORD"]

# common for all requests to NEP server:
base_url = "https://api.nepviewer.net/v2"
headers = {"oem": "NEP"}


def get_data(path, data):
    response = requests.post(f"{base_url}/{path}", headers=headers, json=data)
    return response.json()["data"]


def dmy2ymd(x):
    # convert DD/MM/YYYY hh:mm -> YYYY-MM-DD hh:mm
    # (DD/MM/YYYY is the date format I get when reading from the NEP server;
    #  this may need adapting for other NEP accounts, depending on their settings)
    return f"{x[6:10]}-{x[3:5]}-{x[0:2]}{x[10:]}"


## get authorization

headers["Authorization"] = get_data(
    "sign-in", {"account": account, "password": password}
)["tokenInfo"]["token"]


## get device(s)

data = get_data("device/list", {"page": {"size": 10}})

# there may be more registered devices, but we only use the first one:
data = data["list"][0]

sn = data["sn"]
first_day = dmy2ymd(data["createdAt"])[:10]
last_day = dmy2ymd(data["lastUpdate"])[:10]

print(
    f'Reading data for {data["modelName"]} #{data["sn"]},',
    f'registered {dmy2ymd(data["createdAt"])} in {data["city"]}',
)


## show device status

data = get_data("device/statistics/overview", {"sn": sn})

print(
    f'Last update: {data["totalNow"]} {data["totalNowUnit"]}',
    f'/ {data["production"]["today"]} {data["production"]["todayUnit"]}',
    f'at {dmy2ymd(data["lastUpdate"])}, status {data["alertTitle"]}',
)


## (try to) load old data from local file

fn = f"NEPviewerCR-{sn}.csv"
try:
    df = pd.read_csv(fn)
except:
    # not found? -> try loading data from obsolete tool set:
    old_fn = fn.replace("-", "_")
    try:
        dfo = pd.read_csv(old_fn)
        df = dfo.groupby("date").kWh.max().reset_index()
    except:
        # still not found? -> create empty df
        df = pd.DataFrame(columns=["date", "kWh"])

if len(df):
    # no need to re-fetch known data from NEP server, but
    # last day's value may have been incomplete
    first_day = df.date.max()


## get all days' kWh

y1, m1, d1 = [int(x) for x in first_day.split("-")]
y2, m2, d2 = [int(x) for x in last_day.split("-")]

date, kwh = [], []

for y in range(y1, y2 + 1):
    for m in range(1, 13):
        if y == y1 and m < m1:
            continue
        if y == y2 and m > m2:
            continue
        dd1 = d1 if y == y1 and m == m1 else 1
        dd2 = d2 if y == y2 and m == m2 else calendar.monthrange(y, m)[1]
        # NEP server doesn't handle rangeDate of a single day correctly:
        if dd1 == dd2:
            if dd1 == 1:
                dd2 = dd2 + 1
            else:
                dd1 = dd1 - 1
        rd = f"{y}-{m:02d}-{dd1:02d}~{y}-{m:02d}-{dd2:02d}"
        print("Getting data for", rd, "from NEP server")
        data = get_data(
            "device/statistics/echarts", {"sn": sn, "types": 3, "rangeDate": rd}
        )
        for d, k in zip(data["xAxisData"], data["series"][0]["data"]):
            if k != None:
                date.append(dmy2ymd(d))
                kwh.append(k)

# append newly fetched data to old data loaded from file:
df = pd.concat([df, pd.DataFrame({"date": date, "kWh": kwh})])

# drop duplicate/old values:
df = df.groupby("date").kWh.max().reset_index()

# save for next run:
df.to_csv(fn, index=False)

# create some helper columns:
df["sdate"] = df.date
df.date = pd.to_datetime(df.date)
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month
df["day"] = df.date.dt.day


## simple plots

# plot kWh/d:
df.plot(x="date", y="kWh", grid=True, figsize=(15, 5))
plt.tight_layout()
plt.show()

# plot kWh/month:
kWh_m = df.groupby(["year", "month"]).kWh.sum().reset_index()
dfx = kWh_m.pivot(index="month", columns="year", values="kWh")
ax = dfx.plot(kind="bar", width=0.8, figsize=(20, 5))
for c in ax.containers:
    ax.bar_label(c, fmt="%.0f")
ax.set_frame_on(False)
ax.set_yticks([])
ax.set_ylabel("kWh")
ax.legend(
    [
        f'{y}: {kWh_m.query("year=="+str(y)).kWh.sum():.0f} kWh'
        for y in kWh_m.year.unique()
    ]
)
ax.set_title(f"Overall Energy Production: {kWh_m.kWh.sum():.0f} kWh", weight="bold")
plt.tight_layout()
plt.show()

# boxplot for kWh/d, grouped by year,month:
dfx = df.query(f'date<"{last_day}"')
# usually incomplete last (current) day distorts box for current month
dfx.boxplot("kWh", ["year", "month"], rot=90, showmeans=True, figsize=(10, 5))
plt.tight_layout()
plt.show()

# plot highest kWh/d:
n = 30
df.groupby("sdate").max().nlargest(n, "kWh").plot.scatter(
    "date", "kWh", grid=True, rot=90, title=f"{n} Highest Daily Energies", alpha=0.5
)
plt.tight_layout()
plt.show()

# plot heatmap:
dfx = df.sort_values(["month", "day"]).pivot(
    index="year", columns=["month", "day"], values="kWh"
)
cmap = mcolors.LinearSegmentedColormap.from_list(
    "BlueGreenYellowRed", ["#00f", "#0f0", "#ff0", "#f00"]
)
sns.set(rc={"figure.figsize": (20, len(df.year.unique()))})
sns.heatmap(dfx, cmap=cmap)
plt.tight_layout()
plt.show()


## plot calendars:

max_kwh_per_day = df.kWh.max()

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
    total = round(sum(kwh.values()))
    high = f"(max/d={max(kwh.values()):.1f})"
    # hue: max:0=red to min:2/3=blue
    c = [
        mcolors.hsv_to_rgb(((1 - kwh[d] / max_kwh_per_day) * 2 / 3, 1, 1)) for d in kwh
    ]
    ax.bar(kwh.keys(), kwh.values(), color=c)
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
    plt.show()


kwh = {}
for y in df.year.unique():
    kwh[y] = {}
    dfy = df.query(f"year=={y}")
    for m in dfy.month.unique():
        kwh[y][m] = {}
        dfym = dfy.query(f"month=={m}")
        for d in dfym.day.unique():
            kwh[y][m][d] = dfym.query(f"day=={d}").kWh.max()
    plot_calendar(y, kwh[y])
