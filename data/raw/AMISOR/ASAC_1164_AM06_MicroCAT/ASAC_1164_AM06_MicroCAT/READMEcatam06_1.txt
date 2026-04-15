
AMISOR borehole AM06 MICROCAT data for 2010/2011 season
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

* For cat7323, conductivity/salinity data spikes have been removed for
the following decimal times: 3396.16668, 3654.97918

* For cat7325, conductivity/salinity data spikes have been removed for
the following decimal times: 3657.29168, 3657.37501-3657.43751

* Linear clock correction applied to "compress" times, to correct
for clock drift - very small for these microcats.

* Mean pressures over this latest download:

cat7325 =  551.4 dbar
cat7324 =  680.8 dbar
cat7323 =  790.3 dbar


* Original pressure data for microcat 7325 are suspect, with a steady drift of
~7 dbar over the year, a drift not evident in the other 2 microcats. This pressure
trend was removed from the data, and conductivity/salinity values recalculated.
(The original uncorrected data are in the files cat7325_1uncorrected.dat and
cat7325_1uncorrected.mat.)


matlab
------
contained in matlab format files catxxxx_1.mat, where
xxxx = microcat serial number. 



