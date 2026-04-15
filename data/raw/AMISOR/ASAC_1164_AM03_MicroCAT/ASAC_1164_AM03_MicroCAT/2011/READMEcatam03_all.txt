
AMISOR borehole AM03 MICROCAT data: 27/12/2005 to 22/12/2010
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



matlab
------
contained in matlab format files catxxxx_all.mat, where
xxxx = microcat serial number. 



