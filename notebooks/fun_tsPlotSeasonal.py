import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from fun_tsSeasonColourbar import add_season_colorbars
from fun_tsOverlays import ts_plot_overlays
from fun_tsPrepareData import prepare_ts_data
from IPython.display import display

# Define a dictionary mapping each season to a distinctive colourmap and their month numbers
season_cmaps = {
    "Summer (Dec–Feb)": ("Reds",   [12, 1, 2]),
    "Autumn (Mar–May)": ("YlOrBr", [3, 4, 5]),
    "Winter (Jun–Aug)": ("Blues",  [6, 7, 8]),
    "Spring (Sep–Nov)": ("Greens", [9, 10, 11]),
}

# Define three discrete shades per season — light, medium, dark
# This will be used to differentiate months within each season
shade_levels = [0.4, 0.65, 0.9]

# Access the previously saved meltwater mixing line anchoring points 
from fun_tsOverlays import GADE_ANCHORS
try:
    with open("../data/pickles/gade_anchors.pkl", "rb") as f:
        GADE_ANCHORS.update(pickle.load(f))
except (FileNotFoundError, EOFError):
    pass

def plot_ts_seasonal(df, fig, ax, borehole, cat, year=None, average="median", season=None, ylim_temp=None, xlim_sal=None, allow_gade_selection=True):
    if ylim_temp is not None: ax.set_ylim(*ylim_temp)
    if xlim_sal  is not None: ax.set_xlim(*xlim_sal)
    
    sub = prepare_ts_data(df, borehole, cat, year=year, average=average)
    full_data = sub.copy()

    # Plot each season with its own colourmap, normalised to that season's DOY range
    # Iterate over each season and its respective colourmap and months in season_cmaps
    for season_name, (cmap_name, months) in season_cmaps.items():
        if season is not None and season_name != season:
            continue
        elif season is not None and season_name == season:
            # Filter to just this season's months
            sub = sub[sub["month"].isin(months)]
            ax.set_title(season_name, fontsize=14)
        
        # Extract the colourmap
        cmap = plt.get_cmap(cmap_name)

        # Iterate over each month in the season
        for i, month in enumerate(months):
            # Filter the dataframe to include only the month included in this iteration
            sub_month = sub[sub["month"] == month]

            if sub_month.empty:
                continue
            
            # Extract the month name
            month_name = pd.Timestamp(2001, month, 1).strftime("%b")

            ax.scatter(sub_month["absolute_salinity"], sub_month["conservative_temperature"], c=[cmap(shade_levels[i])], s=8, label=month_name)

    # Force the figure to display before any interactive prompts
    display(fig.canvas)
    fig.canvas.draw_idle()
    fig.canvas.flush_events()
    
    ts_plot_overlays(ax, fig, full_data, cat, ylim_temp, xlim_sal, allow_selection=allow_gade_selection, year=year, average=average)
    
    ax.set_xlabel(r"Absolute Salinity $(\mathrm{S_{A}) \ g \ kg^{-1}}$", fontsize=14)


def plot_ts_seasonal_wrapper(df, borehole, cat, season_by_season=False, regional=False, year=None, average="median", allow_selection=True):
    # Define the limits for plots of temperature and salinity
    ylim_temp_regional = (-2.4, 2.0)
    ylim_temp_cavity = (-2.4, -1.7)
    xlim_sal = (34, 35)

    # Toggle the below boolean to see the T-S for a broader regional scale (True) or just in the cavity context (False), i.e. predominantly ISW
    if regional:
        ylim_temp = ylim_temp_regional
    else:
        ylim_temp = ylim_temp_cavity
    
    if season_by_season:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12), sharey=True, gridspec_kw={"wspace": 0.1, "hspace": 0.25})
        axes_flat = axes.flatten()

        # Iterate over each season
        for i, (season_name, (cmap_name, months)) in enumerate(season_cmaps.items()):
            plot_ts_seasonal(df, fig, axes_flat[i], borehole, cat, year=year, average=average, season=season_name, ylim_temp=ylim_temp, xlim_sal=xlim_sal, allow_gade_selection=False)

        # Put the y-axis label only on the leftmost plot
        axes_flat[0].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=12)
        axes_flat[2].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=12)
        axes_flat[0].set_xlabel("")
        axes_flat[1].set_xlabel("")

        fig.subplots_adjust(top=0.93, bottom=0.18, left=0.08, right=0.95, wspace=0.1, hspace=0.25)
    else:
        fig, ax = plt.subplots(figsize=(15, 12))
        
        plot_ts_seasonal(df, fig, ax, borehole, cat, year=year, average=average, ylim_temp=ylim_temp, xlim_sal=xlim_sal, allow_gade_selection=allow_selection)
        
        ax.set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=14)

        plt.tight_layout()

    add_season_colorbars(fig, season_cmaps, shade_levels)

    plt.show()

    # Save the selected meltwater mixing line anchoring points, guarding against an empty list
    if GADE_ANCHORS and allow_selection:
        with open("../data/pickles/gade_anchors.pkl", "wb") as f:
            pickle.dump(GADE_ANCHORS, f)