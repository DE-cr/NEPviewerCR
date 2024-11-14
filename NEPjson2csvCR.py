#!/usr/bin/python

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPjson2csvCR.py: build *.csv from nepviewer.com *.json data)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: python3 NEPjson2csvCR.py *.json

import json
from sys import argv

import pandas as pd

# input:
data = []
csv_fn = ""
for fn in argv[1:]:
    if not csv_fn:  # first input file?
        # deduct output file name from first input file name:
        csv_fn = fn.split("/")[-1].split("\\")[-1]  # remove path
        csv_fn = csv_fn.split("_")[0]  # use serial number only
        csv_fn = f"NEPviewerCR_{csv_fn}.csv"
    with open(fn, "r") as file:
        d = json.load(file)["data"]
        if not d:  # skip empty files
            continue
        for row in d:
            f = row.split()
            if len(f) == 12:  # only log complete rows
                data.append(f)

# output:
if data:
    df = pd.DataFrame(
        data,
        columns=[
            "date",
            "time",
            "kW",
            "V_dc",  # ?
            "V_ac",
            "eng_offset",  # ?
            "Hz",
            "temperature",
            "kWh",
            "ratio",  # ?
            "ver",  # ?
            "status",
        ],
    )
    df.to_csv(csv_fn, index=False)
    print(f"Wrote {len(df)} rows of data to file {csv_fn}")
