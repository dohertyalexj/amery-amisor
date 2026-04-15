
AMISOR borehole AM01 MICROCAT data: 15/01/2002 to 07/01/2009
------------------------------------------------------------

data from all the downloads, joined into a single file for each microcat

ascii format
------------
contained in column formatted files catxxxx_all.dat, where
xxxx = microcat serial number. The columns are:

1. decimal time - decimal days, where 0.0 = 0000 on January 1st 2001.
So, for example, midday on 15th January 2001 is decimal time 14.5
 (corrected for clock drift, if applicable)
2. temperature (deg. C, T90)
3. conductivity (mS/cm)
4. pressure (dbar)
5. salinity (PSS78)
6. to 11. day, month, year, hour, minute, second
 (corrected for clock drift, if applicable)
12. decimal time - no correction for clock drift
13. to 18. day, month, year, hour, minute, second - no correction for
 clock drift

* Note that all times are UTC.

* There is a line of data for each recording interval (i.e. no gaps),
and null data is represented by -999.0

* Linear clock corrections applied are described in README files
for each season.

* For AM01, pressure sensor data were bad for all 3 instruments,
and a constant pressure value was selected for each instrument (from
inspection of data near the start in January 2002), and this constant
value was used to recalculate conductivity, and in the salinity calculation.
Pressure column is -999.0 for all instruments. Assumed pressure of
AM01 instruments is:
cat1969 = 441.1 dbar
cat1970 = 581.5 dbar
cat1971 = 743.0 dbar


matlab
------
contained in matlab format files catxxxx_all.mat, where
xxxx = microcat serial number. 
Pressure vectors cat1969_all_press, cat1970_all_press and cat1971_all_press are all NaN.
Pressure for these instruments is set in the values:
cat1969_all_p = 441.1
cat1970_all_p = 581.5
cat1971_all_p = 743.0



