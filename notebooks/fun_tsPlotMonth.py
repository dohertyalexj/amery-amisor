import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from fun_tsOverlays import ts_plot_overlays
from fun_tsPrepareData import prepare_ts_data
from fun_getLimits import _get_limits

# Colours assigned to boreholes in month mode (when multiple boreholes are shown)
BOREHOLE_COLOURS = {
    "AM01": {"upper": "#e48b8b", "middle": "#cf3030", "lower": "#7c1d1d"},
    "AM02": {"upper": "#e4b88b", "middle": "#cf8130", "lower": "#7c4d1d"},
    "AM03": {"upper": "#8de48b", "middle": "#34cf30", "lower": "#1f7c1d"},
    "AM04": {"upper": "#8be4e4", "middle": "#30cfcf", "lower": "#1d7c7c"},
    "AM05": {"upper": "#8ba4e4", "middle": "#305dcf", "lower": "#1d387c"},
    "AM06": {"upper": "#d28be4", "middle": "#af30cf", "lower": "#691d7c"}
}

# Define a dictionary mapping each MicroCAT to it's pre-calculated average pressure
# Average pressure is the mean pressure on deployment
AVG_PRESSURES = {
    "1969": 441.1,    "1970": 581.6,   "1971": 743.4,
    "1623": 338.5,    "1624": 562.7,   "1174": 770.2,
    "4055": 653.6,    "4054": 861.5,   "3883": 1211.1,
    "1972": 550.4,    "1973": 693.0,   "1974": 814.7,
    "7327": 580.5,    "7326": 738.8,   "7322": 876.6,
    "7325": 551.4,    "7324": 680.8,   "7323": 790.3,
}

# Access the previously saved meltwater mixing line anchoring points 
from fun_tsOverlays import GADE_ANCHORS
try:
    GADE_ANCHORS[("all", None)] = [(34.49, -1.9), (34.68, -1.9), (34.7, -1.9)]
    with open("../data/pickles/gade_anchors.pkl", "rb") as f:
        GADE_ANCHORS.update(pickle.load(f))
except (FileNotFoundError, EOFError):
    pass

def plot_ts_months(df, boreholes, borecats, months, year, average, regional, columns):
    # Handle if month mode has been selected, but user has not specified which months
    if months is None:
        months = list(range(1, 13))

    # Build borecats from boreholes if not explicitly provided
    if borecats is None:
        borecats = {}
        for borehole in (boreholes or []):
            df_bh = df[df["borehole"] == borehole]
            cats = []
            for position in ["upper", "middle", "lower"]:
                cats.extend(df_bh[df_bh["water_column_position"] == position]["cat"].unique().tolist())
            borecats[borehole] = cats

    boreholes_list = list(borecats.keys())

    rows = math.ceil(len(months) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(10 * columns, 5 * rows), sharey=True, gridspec_kw={"wspace": 0.1}, constrained_layout=True)

    # Flatten — but handle the single-row and single-column edge cases
    if rows == 1 and columns == 1:
        axes_flat = [axes]
    elif rows == 1 or columns == 1:
        axes_flat = list(axes)
    else:
        axes_flat = list(axes.flatten())


    # Define the limits for plots of temperature and salinity based on the plot mode (regional vs cavity-focused)
    xlim_sal, ylim_temp = _get_limits(regional)

    # Create a dictionary to store the prepared data for each cat, keyed by borehole
    cat_data_by_borehole = {}

    # Iterate over each borehole
    for borehole, cats_list in borecats.items():
        df_bh = df[df["borehole"] == borehole]
        # Initialise dictionaries to hold the data for each cat
        cat_data = {}      # {cat_id: prepared_dataframe}
        cat_positions = {} # {cat_id: "upper"/"middle"/"lower"}

        # Iterate over each cat at this borehole
        for cat in cats_list:
            # Look up water column position from the dataframe
            pos_values = df_bh[df_bh["cat"] == cat]["water_column_position"].unique()
            position = pos_values[0] if len(pos_values) > 0 else "upper"
            # Prepare the data for this cat
            data = prepare_ts_data(df, borehole, cat, year=year, average=average)
            # Add this data to the dictionaries initialised above
            if data is not None:
                cat_data[cat] = data
                cat_positions[cat] = position

        # Add the prepared data to the main dictionary keyed by borehole
        if cat_data:
            cat_data_by_borehole[borehole] = (cat_data, cat_positions)

    for col, month in enumerate(months):
        # Create a new subplot for this month
        ax = axes_flat[col]
        ax.set_xlim(*xlim_sal)
        ax.set_ylim(*ylim_temp)

        # Extract the month name and add as the subplot title
        ax.set_title(pd.Timestamp(2001, month, 1).strftime("%B"), fontsize=14)

        # WANT TO MOVE THIS TO ONLY THE BOTTOM SUBPLOTS
        ax.set_xlabel(r"Absolute Salinity $(\mathrm{S_{A}) \ g \ kg^{-1}}$", fontsize=14)
        
        all_cats, combined = [], []

        # Iterate over each borehole
        for borehole, (cat_data, cat_positions) in cat_data_by_borehole.items():
            # Iterate over each cat
            for cat, data in cat_data.items():
                # Extract the data pertaining to the iterated month, for this iterated cat
                month_data = data[data["month"] == month]
                if month_data.empty:
                    continue
                # Extract the position of the iterated cat
                position = cat_positions[cat]
                # Plot the T-S points for this month and cat, coloured by position
                ax.scatter(month_data["absolute_salinity"], month_data["conservative_temperature"], c=BOREHOLE_COLOURS[borehole][position], s=8, label=f"{borehole}-{AVG_PRESSURES[f"{cat}"]:.0f} dbar)" if col == 0 else "_")
                all_cats.append(cat)
                combined.append(month_data)

        # Call overlays once per panel, with all cats
        ts_plot_overlays(ax, fig, combined, all_cats, ylim_temp, xlim_sal, allow_selection=False, year=year, average=average)

    # Hide any unused subplots
    for j in range(len(months), rows * columns):
        axes_flat[j].axis("off")

    # Set the y-axis label for the leftmost plots only
    for row in range(rows):
        axes_flat[row * columns].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=14)

    axes_flat[0].legend(fontsize=10, loc="best")

    bh_label = " & ".join(boreholes_list)
    fig.suptitle(f"Borehole(s) {bh_label} — {year}" if year is not None else f"Borehole(s) {bh_label}", fontsize=16, y=1.02)
    plt.show()