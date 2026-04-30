# Apply Filters to Data

## Define a function to apply the low-pass Butterworth filter for a desired period

#### scipy.signal.butter(N, Wn, btype='low', analog=False, output='ba', fs=None) is used to design an N-th order Butterworth digital or analog filter.
#### Type of output: numerator/denominator (‘ba’), pole-zero (‘zpk’), or second-order sections (‘sos’). Default is ‘ba’ for backwards compatibility, but ‘sos’ should be used for general-purpose filtering. 
#### For info: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html

#### scipy.signal.sosfiltfilt applies the filter forward through the data and then backwards. Since the forward filtering shifts the signal slightly in time, the backward filtering shifts it back, creating net zero time shift. 

from scipy import signal
import pandas as pd
import numpy as np

def lowpass_filter(series, cutoff_period, sampling_interval, order=2, max_gap_hours=0):
    """
    series:            column of the DataFrame to filter - "series" is what pandas calls a single column of data in a DataFrame (no NaNs)
    cutoff_period:     period to filter at, in same units as sampling_interval
                       e.g. 24 hours — anything faster gets removed
    sampling_interval: time between samples, i.e. 0.5 for 30-minute data in hours for AMISOR MicroCATs
    order:             filter order
    """
    # Calculate the minimum chunk size in terms of number of data points
    # This is chosen as 4 times the number of valid data points in the cut off period, which is a common rule of thumb for reliable filtering
    # e.g. 400 — this is 4 times a 48h cutoff period for 30-minute data
    min_chunk_size = int(4 * cutoff_period * (1 / sampling_interval))
    
    # Calculate the sampling frequency of the filter using the provided time between sampling
    fs = 1 / sampling_interval
    # Calculate the cutoff frequency using the desired cutoff period defined in the function call
    cutoff_freq = 1 / cutoff_period        # cutoff frequency
    
    # Design the Butterworth low-pass filter using second-order sections (SOS)
    # SOS provides better numerical stability for higher-order filters
    sos = signal.butter(order, cutoff_freq, btype='low', fs=fs, output='sos')

    if max_gap_hours > 0:
        # Calculate the maximum number of consecutive NaNs to be filled by interpolation
        max_gap_points = int(max_gap_hours / sampling_interval)
        # Interpolate across gaps sufficiently small for the cutoff period of smoothing
        filled = pd.Series(series).interpolate(limit=max_gap_points).values
    else:
        filled = series.copy()

    # Create a 'blank' array of the same size and shape as the input series, filled with NaN values
    # Valid data points (i.e. not NaNs) will be added as defined chunks, which filtering can be applied to
    # The filtered results will be stored in this array
    result = np.full_like(series, np.nan, dtype=float)

    # Create a boolean array to identify non-NaN values
    valid = ~np.isnan(filled)
    # Convert this boolean to 1s and 0s, then take the difference to find where valid data chunks start and end 
    changes = np.diff(valid.astype(int))
    starts = np.where(changes == 1)[0] + 1   # invalid -> valid
    ends = np.where(changes == -1)[0] + 1    # valid -> invalid
    # Handle edge cases where the series starts or ends with valid data
    if valid[0]:
        starts = np.insert(starts, 0, 0)
    if valid[-1]:
        ends = np.append(ends, len(filled))

    # Iterate over each chunk of valid data that is defined by a start and end point
    for s, e in zip(starts, ends):
        # Extract the data for the current iteration of valid data chunk
        chunk = filled[s:e]
        # Skip chunks that are too short to filter reliably (as defined by the user with min_chunk_size)
        if min_chunk_size and len(chunk) < min_chunk_size:
            # Keep commented out so as not to retain unfiltered chunks
            # result[s:e] = chunk  # keep unfiltered
            continue
        # Apply the filter to the input series using filtfilt, which applies the filter forward and backward to avoid phase distortion
        try:
            result[s:e] = signal.sosfiltfilt(sos, chunk)
        # If the filtering process fails (e.g. due to insufficient data points in the chunk), catch the ValueError and keep the original unfiltered chunk in the result
        except ValueError:
            result[s:e] = chunk 

    return result

## Call the filter function for each MicroCAT, using the desired filtering parameters

#### Herraiz-Borreguro et al. (2013, 2015) uses a 40h period, while Herraiz-Borreguero et al. (2016) uses a 48h period for MicroCAT time series data from the AMISOR project.

### Smooth each series in the DataFrame

# Define a function to apply the low-pass filter to the relevant columns of the DataFrame, grouped by borehole and category
def apply_lowpass_filter(df, cutoff_period, sampling_interval, max_gap_hours=0):
    # Iterate over each unique combination of borehole and category in the DataFrame
    for (bh, cat), group in df.groupby(["borehole", "cat"]):
        # Create a boolean mask to identify the rows corresponding to the current iteration of borehole and cat
        mask = (df["borehole"] == bh) & (df["cat"] == cat)
        # Apply the low-pass filter to the "in_situ_temperature" column 
        # Assign the results back to a new "in_situ_temperature_smooth" column 
        df.loc[mask, "in_situ_temperature_smooth"] = lowpass_filter(
            group["in_situ_temperature"].values,
            cutoff_period=cutoff_period,
            sampling_interval=sampling_interval,
            max_gap_hours=max_gap_hours
        )
        df.loc[mask, "potential_temperature_smooth"] = lowpass_filter(
            group["potential_temperature"].values,
            cutoff_period=cutoff_period,
            sampling_interval=sampling_interval,
            max_gap_hours=max_gap_hours
        )
        df.loc[mask, "conservative_temperature_smooth"] = lowpass_filter(
            group["conservative_temperature"].values,
            cutoff_period=cutoff_period,
            sampling_interval=sampling_interval,
            max_gap_hours=max_gap_hours
        )
        df.loc[mask, "practical_salinity_smooth"] = lowpass_filter(
            group["practical_salinity"].values,
            cutoff_period=cutoff_period,
            sampling_interval=sampling_interval,
            max_gap_hours=max_gap_hours
        )
        df.loc[mask, "absolute_salinity_smooth"] = lowpass_filter(
            group["absolute_salinity"].values,
            cutoff_period=cutoff_period,
            sampling_interval=sampling_interval,
            max_gap_hours=max_gap_hours
        )
    return df