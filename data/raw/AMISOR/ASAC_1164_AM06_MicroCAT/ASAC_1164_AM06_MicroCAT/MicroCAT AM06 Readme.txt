
MicroCAT AM06 Readme.txt

Latest Update:	November 2011

Instrument: 	Seabird SBE37-IM MicroCAT CTD, Nos. 7325, 7324, & 7323   

Accuracy & Precision: 	
			(See file : 37IMbrochureMay05.pdf)  
			SPECIFICATIONS
			Measurement Range
			Conductivity: 0 - 7 S/m (0 - 70 mS/cm)
			Temperature: -5 to 35 °C
			Optional Pressure: 20/100/350/600/1000/2000/3500/7000 m
			(meters of deployment depth capability)
			Initial Accuracy
			Conductivity: 0.0003 S/m (0.003 mS/cm)
			Temperature: 0.002 °C
			Optional Pressure: 0.1% of full scale range
			Typical Stability (per month)
			Conductivity: 0.0003 S/m (0.003 mS/cm)
			Temperature: 0.0002 °C
			Optional Pressure: 0.004% of full scale range
			Resolution
			Conductivity: 0.00001 S/m (0.0001 mS/cm)
			Temperature: 0.0001 °C
			Optional Pressure: 0.002% of full scale range 

			Annual internal clock drifts are < 5 mins, reset each season to UTC 

Location:		AM06, epoch January 2010
			Latitude: 			-70.24583(S)
			Longitude:		 	71.36383 (E) 
			Elevation: 		 	TBA m, asl (GRACE geoid)
			Surface speed: 	 	357 m/a 
			Flow direction: 	 	25 wrt True North 
			Ice Thickness:	 	607 m 
			Sea floor depth:		TBA m, asl (295 m thick ocean cavity) 
			Depth to well:		TBA m, below the surface 

Data storage:	\\ice\grease\amisor\AM06 data\MicroCAT\*

Raw Files written:	
			*.dat		ascii files with header information & data columns 

Data collection, instruments moored at AM06, initial installation: 

	cat7325	positioned 18 m below ice shelf base 
			average depth = 551.2 dBar 

	cat7324	positioned 145 m below ice shelf base 
			average depth = 681.2 dBar 

	cat7323	positioned 253 m below ice shelf base, 42 m up from sea floor  
			average depth = 790.6 dBar 

Data is uploaded by polling each instrument separately upon return visits to the site

Data collection, data files from instruments moored at AM05: 

	All data collected at 0.5 hour sampling rate ... 

Initial data: 

	None collected, instruments set for annual data collection, visual computer output data inspection 

Annual data 2010:

	20110108_MC7325.dat	07-Jan 2010 to 08-Jan 2011, 0.5 hr sample rate 

	20110108_MC7324.dat	07-Jan 2010 to 08-Jan 2011, 0.5 hr sample rate 

	20110108_MC7323.dat	07-Jan 2010 to 08-Jan 2011, 0.5 hr sample rate 

Annual data 2011 :

	To be collected 2011-12 summer season ... 

Calibration:

	Applied by Mark Rosenberg 
	Clock adjustment applied
	See "Readmecatam06.txt" 

Analysis:

*.dat files can be parsed into Excel spreadsheets (along with header information contained therein)

Salinities can be calculated from C, T, P measurements using an algorithm entered into the file "conductivity to salinity.xls" 

Plots of C-P, T-P, S-P, and T-S can be produced  

See: borehole2010_11.pdf, Rosenberg et al., for full details of calibrations

Further Analysis:


Data processing includes: 

T90	> measured by MicroCAT
T90	> converted to T68 for calculations of salinity, density, etc ... 
	> seawater algorithms written prior to new Temperature scale acceptance ... 
Potential temperatures produced (Theta-T68) for Theta-S diagrams 
	> constant density lines (isopycnals) produced for plots 
	> potential freezing point lines produced for plots 
	> melt-freeze gradient for no heat exchange with ice shelf produced for plots 
	> Theta-S diagrams plotted for seasonal, monthly data breakdown 




