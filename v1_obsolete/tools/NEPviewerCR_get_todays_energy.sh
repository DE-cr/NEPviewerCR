#!/bin/sh

# project: https://github.com/DE-cr/NEPviewerCR
# file: NEPviewerCR_get_todays_energy.sh

wget -qO- http://user.nepviewer.com/pv_monitor/home/index/<<SID>> |
perl -n00e 'print join(" kWh on ",/(?:Today|update):([-.: \d]+)/g),"\n"'
# remove ": " above to drop the time(!) of the last update in the output
