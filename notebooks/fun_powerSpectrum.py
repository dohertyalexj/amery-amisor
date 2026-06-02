import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as sg
from fun_tsOverlays import AVG_PRESSURES

POSITION_COLOURS = {
    "upper": "tab:blue",
    "middle": "tab:green",
    "lower": "tab:red",
}

def plot_psd_borehole(df, borehole, variable="conservative_temperature",
                     max_gap_days=14, nperseg=None, filter_cutoff_period=None, year=None):
    """
    Plot power spectral density for all microCATs at one borehole on log-log axes.
    
    variable: "conservative_temperature" or "absolute_salinity"
    nperseg: segment length for Welch's method. Larger = better frequency resolution, 
             less smoothing. Defaults to ~1/8 of the data length.
    """
    # Filter to the specified borehole
    df_bh = df[df["borehole"] == borehole]
    if df_bh.empty:
        print(f"No data for {borehole}")
        return
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    samples_per_day = 48
    # Define sampling frequency in samples per hour, setting the natural unit of frequency to cycles per hour (cph)
    fs = 2  # 2 samples per hour → frequency naturally in cph
    
    #Iterate over each position in the water column
    for position in ["upper", "middle", "lower"]:
        # Extract the unique cat at this position
        cats = df_bh[df_bh["water_column_position"] == position]["cat"].unique()
        # Iterate over each cat (there should only be one)
        for cat in cats:
            # Filter to this cat
            sub = df_bh[df_bh["cat"] == cat].copy()
            
            # ---- Index Data ----
            # Round each timestamp to its nearest 30-minute mark to account for time drift
            sub["time_snapped"] = sub["time"].dt.round("30min")
            # Set the snapped time column in the DataFrame as the index and sort chronologically
            series = sub.groupby("time_snapped")[variable].mean()
            # Reindex to a full regular 30-minute grid spanning the range of the data
            # This inserts NaN at any missing 30-minute timestamp, across which we will interpolate
            full_range = pd.date_range(series.index.min(), series.index.max(), freq="30min")
            series = series.reindex(full_range)
            
            # ---- Interpolate ----
            # Set up the maximum length of NaNs for interpolation
            limit = max_gap_days * samples_per_day
            # Interpolate across gaps of up to the limit specified
            series = series.interpolate(method="time", limit=limit, limit_area="inside")
            
            # ---- OPTIONAL????: Longest Continuous Stretch ----
            # Keep only the longest continuous (gap-free) stretch for the CWT
            # Keep track of which values are valid (not NaN) in the interpolated time series
            valid = series.notna()
            # Assign a unique ID to each contiguous run of valud data
            # valid != valid.shift() is True where the validity changes (e.g. where data start or ends), and cumsum() gives a unique ID
            run_id = (valid != valid.shift()).cumsum()
            # Find the ID of the longest run
            longest_run = series[valid].groupby(run_id[valid]).size().idxmax()
            # Keep only the values from the longest run, and drop any remaining NaNs
            series = series[run_id == longest_run].dropna()

            # Filter to the specified year if it has been set
            if year is not None:
                series = series[series.index.year == year]
            
            # Generally, for Welch's method we require a minimum of 256 samples to get a meaningful spectrum
            if len(series) < 256:
                print(f"Not enough continuous data for {borehole} cat{cat}")
                continue
            
            # Use Welch's method
            # Segment length (nperseg) determines the frequency resolution and the amount of smoothing.
            # Defaults to 1/8 of the data length, but capped at 8192 to avoid excessive computation time
            seg = nperseg if nperseg is not None else min(8192, len(series) // 8)
            # Welch's method returns the frequencies and the corresponding power spectral density estimates
            # Set detrend="linear" to remove any linear trend from each segment
            # Use a Hann window to reduce spectral leakage.
            f, Pxx = sg.welch(series.values, fs=fs, nperseg=seg, detrend="linear", window="hann")
            
            # Skip f=0 (the DC component is meaningless on log axes)
            mask = f > 0
            
            # Plot on log-log axes, coloured by position
            color = POSITION_COLOURS[position]
            avg_pressure = AVG_PRESSURES[f"{cat}"]
            ax.loglog(f[mask], Pxx[mask], color=color, linewidth=1.5, label=f"{avg_pressure:.0f} dbar")
    
    # ---- Vertical lines at notable periods ----
    # Define some notable periods in days
    notable_periods_days = [20, 10, 5, 3, 1]
    # Get the current y-axis limits to position the labels
    ylim = ax.get_ylim()
    # Iterate over the notable periods
    for p_days in notable_periods_days:
        f_cph = 1 / (p_days * 24)
        ax.axvline(f_cph, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
        # Label at top of plot
        ax.text(f_cph, ylim[1] * 0.7, f"{p_days}-d", 
                ha="center", va="bottom", fontsize=9, color="gray")
    
    # ---- Axis labels and styling ----
    if "temperature" in variable:
        units = r"$^\circ$C$^2$/cph"
        var_label = "Conservative Temperature"
    else:
        units = r"(g/kg)$^2$/cph"
        var_label = "Absolute Salinity"
    
    ax.set_xlabel("Frequency (cph)")
    ax.set_ylabel(f"Power Spectra ({units})")
    year_str = f" ({year})" if year is not None else ""
    ax.set_title(f"{var_label}, {borehole}{year_str}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="best", title="Pressure")

    # If a filter cutoff is specified, hide frequencies above it
    if filter_cutoff_period is not None:
        cutoff_freq = 1 / filter_cutoff_period
        ax.set_xlim(right=cutoff_freq)
        
        visible_max = 0
        visible_min = np.inf
        for line in ax.get_lines():
            if len(line.get_xdata()) == 2:  # skip axvline markers
                continue
            x_data, y_data = line.get_xdata(), line.get_ydata()
            in_range = x_data <= cutoff_freq
            if in_range.any():
                visible_y = y_data[in_range]
                visible_y = visible_y[visible_y > 0]
                if len(visible_y) > 0:
                    visible_max = max(visible_max, visible_y.max())
                    visible_min = min(visible_min, visible_y.min())
    
    ax.set_ylim(visible_min * 0.5, visible_max * 2)
    
    plt.tight_layout()
    plt.show()