import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from fun_tsOverlays import ts_plot_overlays
from fun_tsPrepareData import prepare_ts_data

# Colour MicroCATs by water column position to ensure consistency across all panels
POSITION_COLOURS = {
    "upper": "tab:red",
    "middle": "tab:green",
    "lower": "tab:blue",
}

# Access the previously saved meltwater mixing line anchoring points 
from fun_tsOverlays import GADE_ANCHORS
try:
    GADE_ANCHORS[("all", None)] = [(34.49, -1.9), (34.68, -1.9), (34.7, -1.9)]
    with open("../data/pickles/gade_anchors.pkl", "rb") as f:
        GADE_ANCHORS.update(pickle.load(f))
except (FileNotFoundError, EOFError):
    pass

def plot_ts_months(df, borehole, months, year=None, average="median", regional=False, columns=2):
    """Plot T-S for one borehole, with one panel per chosen month, cats coloured by position."""
    # Define the limits for plots of temperature and salinity
    ylim_temp_regional = (-2.4, 0.0)
    ylim_temp_cavity = (-2.4, -1.7)
    xlim_sal = (34.3, 34.8)

    # Toggle the below boolean to see the T-S for a broader regional scale (True) or just in the cavity context (False), i.e. predominantly ISW
    if regional:
        ylim_temp = ylim_temp_regional
    else:
        ylim_temp = ylim_temp_cavity
    
    rows = math.ceil(len(months) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(10 * columns, 5 * rows), sharey=True, gridspec_kw={"wspace": 0.1}, constrained_layout=True)

    # Flatten — but handle the single-row and single-column edge cases
    if rows == 1 and columns == 1:
        axes_flat = [axes]
    elif rows == 1 or columns == 1:
        axes_flat = axes  # already a 1D array
    else:
        axes_flat = axes.flatten()
    
    # Prepare data once per cat at this borehole
    df_bh = df[df["borehole"] == borehole]
    # Initialise dictionaries to hold the data for each cat
    cat_data = {}      # {cat_id: prepared_dataframe}
    cat_positions = {} # {cat_id: "upper"/"middle"/"lower"}
    
    # Iterate over each position at this borehole
    for position in ["upper", "middle", "lower"]:
        # Extract the cat corresponding to the iterated position
        cats = df_bh[df_bh["water_column_position"] == position]["cat"].unique()
        # Iterate over each cat
        for cat in cats:
            # Prepare the data for this cat
            data = prepare_ts_data(df, borehole, cat, year=year, average=average)
            # Add this data to the dictionaries initialised above
            if data is not None:
                cat_data[cat] = data
                cat_positions[cat] = position
    
    all_cats = list(cat_data.keys())

    # Iterate over each month
    for col, month in enumerate(months):
        # Create a new subplot for this month
        ax = axes_flat[col]
        ax.set_xlim(*xlim_sal)
        ax.set_ylim(*ylim_temp)
        
        # Extract the month name
        month_name = pd.Timestamp(2001, month, 1).strftime("%B")
        ax.set_title(month_name, fontsize=14)
        ax.set_xlabel(r"Absolute Salinity $(\mathrm{S_{A}) \ g \ kg^{-1}}$", fontsize=14)
        
        # Iterate over each cat
        for cat, data in cat_data.items():
            # Extract the data pertaining to the iterated month, for this iterated cat
            month_data = data[data["month"] == month]
            if month_data.empty:
                continue
            # Extract the position of the iterated cat
            position = cat_positions[cat]
            # Plot the T-S points for this month and cat, coloured by position
            ax.scatter(month_data["absolute_salinity"], month_data["conservative_temperature"], c=POSITION_COLOURS[position], s=8, label=f"{position.capitalize()} (cat{cat})" if col == 0 else "_")
        
        # Combine data from all cats in this month for the overlays plot_data
        combined = pd.concat([data[data["month"] == month] for data in cat_data.values()])
    
        # Call overlays once per panel, with all cats
        ts_plot_overlays(ax, fig, combined, all_cats, ylim_temp, xlim_sal, allow_selection=False, year=year, average=average)
    
    # Hide any unused subplots
    for j in range(len(months), rows * columns):
        axes_flat[j].axis("off")

    # Set the y-axis label for the leftmost plots only 
    for row in range(rows):
        axes_flat[row * columns].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=14)

    axes_flat[0].legend(fontsize=10, loc="best")
    
    fig.suptitle(f"Borehole {borehole} in {year}" if year is not None else f"Borehole {borehole}", fontsize=16, y=1.02)
    plt.show()