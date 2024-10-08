# NEPviewerCR

**(Partial) NEPViewer replacement for desktop/laptop computers**

Utility files to view selected data uploaded by [NEP micro inverter 
systems](https://northernep.com/products/microinverters/) to the cloud, instead 
of using the official iOS/Android NEPViewer app. (Note: This also works for 
rebranded NEP micro inverters, e.g. those distributed by Anker or Nuasol.)

## NEPviewerCR+.html

Use this if you want an interactive day display ... and are willing to do the 
following: Temporarily disable CORS in your web browser (e.g. using [CORS 
Everywhere](https://github.com/spenibus/cors-everywhere-firefox-addon) with 
Firefox, which thankfully automatically enables the CORS security feature again 
on each start of Firefox),
then load `NEPviewerCR+.html`, with your micro inverter's serial number 
appended in the address like this `file:///.../NEPviewerCR+.html?SN=efcdab78`. 
The serial number must be as provided in registering your micro inverter with 
the [NEPViewer server](https://nepviewer.com/).

Initially the current day's power and energy curves, the most recent seven 
days', the most recent twelve months', and the most recent years' cumulative 
energy will be displayed graphically. Using the date selection control in the 
top left of the screen, the power curve for any other day can be displayed.

Try moving your mouse pointer over the day curves or their legend, or
zooming in on that plot for (much) more interactivity! (...with the data
for your solar system, once you see it in your browser, as described here.
The example screenshot I provide below is static.)

**Example:**

![NEPviewerCR+.html](NEPviewerCR+.png)

## NEPviewerCR+.py

If a static snapshot of your solar system's performance is sufficient for you 
(or you're not willing to (temporarily) disable CORS in your browser), there's 
also `NEPviewerCR+.py`.

`Usage: python3 NEPviewerCR+.py serno [yyyymmdd]`

**Example:**

![NEPviewerCR+.py](SN=efcdab78_on_2024-08-12.png)

## NEPviewerCR.py

If all you want is a non-interactive plot of a day's power and energy curves, 
you can also use `NEPviewerCR.py`.

`Usage: python3 NEPviewerCR.py serno [yyyymmdd]`

**Example:**

![NEPviewerCR.py](NEPviewerCR.png)

## NEPstatusCR.pl

There's also `NEPstatusCR.pl`, which can be used on the command line to get the 
most recent status of a micro inverter registered with the [NEPViewer 
server](https://nepviewer.com/).

**Example:**

(Replace `efcdab78` with your micro inverter's serial number!)
```
$ perl NEPstatusCR.pl efcdab78
80 W / 0.048 kWh on 2024-08-20 07:38 (941.257 kWh total)
```
