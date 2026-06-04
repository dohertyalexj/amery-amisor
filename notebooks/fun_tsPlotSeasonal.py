import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from fun_tsSeasonColourbar import add_season_colorbars
from fun_tsOverlays import ts_plot_overlays
from fun_tsPrepareData import prepare_ts_data
from IPython.display import display

try:
    from IPython.display import display as ipy_display
    _HAS_IPYTHON = True
except ImportError:
    _HAS_IPYTHON = False

# Define a dictionary mapping each season to a distinctive colourmap and their month numbers
SEASON_CMAPS = {
    "Summer (Dec–Feb)": ("Reds",   [12, 1, 2]),
    "Autumn (Mar–May)": ("YlOrBr", [3, 4, 5]),
    "Winter (Jun–Aug)": ("Blues",  [6, 7, 8]),
    "Spring (Sep–Nov)": ("Greens", [9, 10, 11]),
}

# Marker shapes cycling across cats in seasonal/doy modes
CAT_MARKERS = ["o", "s", "^", "D", "v", "P", "*"]

# Define three discrete shades per season — light, medium, dark
# This will be used to differentiate months within each season
SHADE_LEVELS = [0.4, 0.65, 0.9]

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
    with open("../data/pickles/gade_anchors.pkl", "rb") as f:
        GADE_ANCHORS.update(pickle.load(f))
except (FileNotFoundError, EOFError):
    pass

def plot_ts_seasonal(df, ax, fig, borecats, year=None, average="median", ylim_temp=None, xlim_sal=None, season=None, allow_selection=True):
    """Render one seasonal panel (all seasons or a single season) for one or more cats."""
    if ylim_temp is not None: ax.set_ylim(*ylim_temp)
    if xlim_sal  is not None: ax.set_xlim(*xlim_sal)

    if season is not None:
        ax.set_title(season, fontsize=14)

    multi_cat = sum(len(cats) for cats in borecats.values()) > 1
    all_cats, all_data = [], []
    first_cat = True

    # Iterate over each borehole and cat
    handles = []
    j = 0
    for borehole, cats in borecats.items():
        for cat in cats:
            sub = prepare_ts_data(df, borehole, cat, year=year, average=average)
            
            if sub is None:
                continue

            all_cats.append(cat)
            all_data.append(sub)
            marker = CAT_MARKERS[j % len(CAT_MARKERS)]

            # Iterate over each season and its respective colourmap and months in SEASON_CMAPS
            for season_name, (cmap_name, months) in SEASON_CMAPS.items():
                if season is not None and season_name != season:
                    continue
                elif season is not None and season_name == season:
                    # Filter to just this season's months
                    sub = sub[sub["month"].isin(months)]
                    ax.set_title(season_name, fontsize=14) 

                # Extract the colourmap 
                cmap = plt.get_cmap(cmap_name)

                for i, month in enumerate(months):
                    # Filter the dataframe to include only the month included in this iteration
                    sub_month = sub[sub["month"] == month]

                    if sub_month.empty:
                        continue

                    # Only label months for the first cat to avoid duplicate legend entries
                    # Extract the month name
                    month_name = pd.Timestamp(2001, month, 1).strftime("%b")

                    label = month_name if (first_cat and not multi_cat) else "_"

                    ax.scatter(sub_month["absolute_salinity"], sub_month["conservative_temperature"],
                            c=[cmap(SHADE_LEVELS[i])], marker=marker, s=8, label=label)
            first_cat = False
            if multi_cat:
                handles.append(mlines.Line2D([], [], marker=CAT_MARKERS[j % len(CAT_MARKERS)], color="grey",
                  linestyle="None", markersize=6, label=f"({borehole}-{AVG_PRESSURES[cat]:.0f} dbar)"))
            j += 1

    # When multiple cats are shown, add a marker-shape legend to identify each cat
    if multi_cat:
        ax.legend(handles=handles, fontsize=10, loc="best")

    # Force figure render before any interactive Gade-selection prompt
    if allow_selection and _HAS_IPYTHON:
        ipy_display(fig.canvas)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
    ts_plot_overlays(ax, fig, all_data, all_cats, ylim_temp, xlim_sal, allow_selection=False, year=year, average=average)
        
    ax.set_xlabel(r"Absolute Salinity $(\mathrm{S_{A}) \ g \ kg^{-1}}$", fontsize=14)

def plot_ts_seasonal_wrapper(df, borecats, season_by_season=False, regional=False, year=None, average="median", allow_selection=True):
    xlim_sal, ylim_temp = _get_limits(regional)

    if season_by_season:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12), sharey=True, gridspec_kw={"wspace": 0.1, "hspace": 0.25})
        axes_flat = axes.flatten()

        # Iterate over each season 
        for i, (season_name, _) in enumerate(SEASON_CMAPS.items()):
            plot_ts_seasonal(df, axes_flat[i], fig, borecats, year, average, ylim_temp, xlim_sal, season=season_name, allow_selection=False)
        
        # Put the y-axis label only on the leftmost plot
        axes_flat[0].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=12)
        axes_flat[2].set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=12)
        axes_flat[0].set_xlabel("")
        axes_flat[1].set_xlabel("")

        fig.subplots_adjust(top=0.93, bottom=0.18, left=0.08, right=0.95, wspace=0.1, hspace=0.25)
    else:
        fig, ax = plt.subplots(figsize=(15, 12))

        plot_ts_seasonal(df, ax, fig, borecats, year, average, ylim_temp, xlim_sal, allow_selection=allow_selection)

        ax.set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=14)

        plt.tight_layout()
    
    add_season_colorbars(fig, SEASON_CMAPS, SHADE_LEVELS)

    plt.show()

    # Save the selected meltwater mixing line anchoring points, guarding against an empty list
    if GADE_ANCHORS and allow_selection:
        with open("../data/pickles/gade_anchors.pkl", "wb") as f:
            pickle.dump(GADE_ANCHORS, f)