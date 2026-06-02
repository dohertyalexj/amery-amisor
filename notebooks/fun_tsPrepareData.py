import pandas as pd

def prepare_ts_data(df, borehole, cat, year=None, average="median"):
    """Filter to borehole/cat and either pick a year or aggregate across years."""
    # Create a mask to filter the dataframe for the specified borehole and cat
    mask = (df["borehole"] == borehole) & (df["cat"] == cat)
    sub = df[mask].copy()

    # Extract the position of the iterated MicroCAT in the water column at its respective borehole
    position = sub["water_column_position"].dropna().iloc[0]
    
    # Extract day of year and year from the time column
    sub["doy"] = sub["time"].dt.dayofyear + sub["time"].dt.hour / 24 + sub["time"].dt.minute / 1440

    # Round to nearest half-hour (1/48 of a day) since each MicroCAT records data with a half-hour interval, although due to time drift
    # the equivalent timestamp on different years may not be exactly the same time to the second
    sub["doy_bin"] = (sub["doy"] * 48).round() / 48
    
    # Only plot the single year if a year has been provided, else we will plot the median/mean
    # Create a mask for the year including the December the year before, and excluding the December of the same year
    if year is not None:
        year_mask = (((sub["time"].dt.year == year - 1) & (sub["time"].dt.month == 12)) | 
                     ((sub["time"].dt.year == year) & (sub["time"].dt.month <= 11)))
        sub = sub[year_mask].copy()
        if sub.empty:
            print(f"No data for {borehole} cat{cat} in austral year {year}")
            return None
        
        # Create a mask to filter the dataframe to just December timestamps
        dec_mask = sub["time"].dt.month == 12
        # Create boolean variable that represents whether the actual year Dec sits in is a leap year or not
        leap_year = sub.loc[dec_mask, "time"].dt.is_leap_year
        # Shift December DOY negative so it sits before January
        sub.loc[dec_mask, "doy"] -= leap_year.map({True: 366, False: 365})

        # Add a "month" to each binned DOY so we can assign it to a season
        sub["month"] = sub["time"].dt.month
    else:
        agg = "mean" if average == "mean" else "median"
        # Calculate the median/mean temp and salinity values on the equivalent timestamp between different years
        sub = sub.groupby("doy_bin")[["conservative_temperature", "absolute_salinity"]].agg(agg).dropna()
        
        # Add a "month" to each binned DOY so we can assign it to a season
        # Use a non-leap reference year to convert DOY back to month
        sub["month"] = pd.to_datetime(sub.index, unit="D", origin="2001-01-01").month
    
    return sub