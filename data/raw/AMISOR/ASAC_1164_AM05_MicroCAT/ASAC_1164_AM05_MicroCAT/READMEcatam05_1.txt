
AMISOR borehole AM05 MICROCAT data for 2010/2011 season
-------------------------------------------------------

Data from the first download.

ascii format
------------
contained in column formatted files catxxxx_1.dat, where
xxxx = microcat serial number. The columns are:

1. decimal time - decimal days, where 0.0 = 0000 on January 1st 2001.
So, for example, midday on 15th January 2001 is decimal time 14.5
2. temperature (deg. C, T90)
3. conductivity (mS/cm)
4. pressure (dbar)
5. salinity (PSS78)
6. to 11. day, month, year, hour, minute, second.

* Note that all times are UTC.

* There is a line of data for each recording interval (i.e. no gaps),
and null data is represented by -999.0

* For cat7322, conductivity/salinity data spikes have been removed for
the following decimal times: 3275.91668

* Records of clock error were lost, so no clock drift corrections have been applied
for this latest download.

* Mean pressures over this latest download (including all pressure steps):

cat7327 =  580.5 dbar
cat7326 =  738.8 dbar
cat7322 =  876.6 dbar

* The pressure changes around decimal time 3600 appear to be real, as they occur
for all 3 microcats.

* Original pressure data for microcat 7327 are suspect, with a steady drift of
~13 dbar over the year, a drift not evident in the other 2 microcats. This pressure
trend was removed from the data, and conductivity/salinity values recalculated.
(The original uncorrected data are in the files cat7327_1uncorrected.dat and
cat7327_1uncorrected.mat.)


matlab
------
contained in matlab format files catxxxx_1.mat, where
xxxx = microcat serial number. 



