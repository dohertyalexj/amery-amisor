import math
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.lines as mlines

# Import helper functions
from fun_getLimits import _get_limits

from fun_tsOverlays import ts_plot_overlays, GADE_ANCHORS
from fun_tsPrepareData import prepare_ts_data
from fun_tsSeasonColourbar import add_season_colorbars
from fun_tsPlotMonth import plot_ts_months
from fun_tsPlotSeasonal import plot_ts_seasonal_wrapper

try:
    from IPython.display import display as ipy_display
    _HAS_IPYTHON = True
except ImportError:
    _HAS_IPYTHON = False

# ── Constants ──────────────────────────────────────────────────────────────────
POSITION_COLOURS = {
    "upper": "tab:red",
    "middle": "tab:green",
    "lower": "tab:blue",
}

POSITION_MARKERS = {
    "upper": "o",
    "middle": "s",
    "lower": "^",
}

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

# Marker shapes cycling across cats in seasonal/doy modes
CAT_MARKERS = ["o", "s", "^", "D", "v", "P", "*"]

# Colormap for the DOY gradient plot — cyclic, maps naturally to a year
DOY_CMAP = "twilight_shifted"

# Load saved Gade anchors
try:
    GADE_ANCHORS[("all", None)] = [(34.49, -1.9), (34.68, -1.9), (34.7, -1.9)]
    with open("../data/pickles/gade_anchors.pkl", "rb") as f:
        GADE_ANCHORS.update(pickle.load(f))
except (FileNotFoundError, EOFError):
    pass

# ── DOY gradient mode ──────────────────────────────────────────────────────────

def _doy_month_ticks(doy_min, doy_max):
    """Return (tick_positions, tick_labels) for month starts within [doy_min, doy_max]."""
    ref = 2001  # non-leap reference year
    ticks, labels = [], []
    for m in range(1, 13):
        ts = pd.Timestamp(ref, m, 1)
        doy = ts.timetuple().tm_yday
        # In year-specific austral plots, December is shifted to negative DOY
        if doy_min < 0 and m == 12:
            doy -= 365
        if doy_min <= doy <= doy_max:
            ticks.append(doy)
            labels.append(ts.strftime("%b"))
    return ticks, labels


def plot_ts_doy(df, borecats, year, average, regional):
    """Render a T-S plot coloured by day-of-year gradient for one or more cats."""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    xlim_sal, ylim_temp = _get_limits(regional)
    ax.set_xlim(*xlim_sal)
    ax.set_ylim(*ylim_temp)

    # WANT TO MOVE THIS TO ONLY THE BOTTOM SUBPLOTS
    ax.set_xlabel(r"Absolute Salinity $(\mathrm{S_{A}) \ g \ kg^{-1}}$", fontsize=14)

    multi_cat = sum(len(cats) for cats in borecats.values()) > 1
   
    # First pass: collect data and DOY values for shared colormap normalisation
    # Initialise an empty list to hold (borehole, cat, sub, doys) typle - one per successfully loaded instrument
    cat_subsets = []
    all_doys = []
    all_cats, all_data = [], []

    # Iterate over each borehole and cat
    for borehole, cats in borecats.items():
        for cat in cats:
            sub = prepare_ts_data(df, borehole, cat, year=year, average=average)
            
            # Guard against missing data
            if sub is None:
                continue

            # Choose where to read DOY values
            if year is not None:
                # If specific year given, "doy" colum holds day of year
                doys = sub["doy"].values  
            else: 
                # If aggregating across years, indexed by DOY directly
                doys = sub.index.values

            cat_subsets.append((borehole, cat, sub, doys))

            # Add this iterated cats DOY values so we can compute a shared min/max
            all_doys.extend(doys)

            all_cats.append(cat)
            all_data.append(sub)

    # Guard against all cats returning None
    if not cat_subsets:
        return

    # Linear normaliser mapping DOY range -> [0,1]
    norm = mcolors.Normalize(vmin=min(all_doys), vmax=max(all_doys))
    sc = None

    # Second pass: scatter each cat with shared normalisation
    # Iterate over each tuple in the collected data representative of each cat
    handles = []
    for j, (borehole, cat, sub, doys) in enumerate(cat_subsets):
        # Allocate a unique marker (up to 7) for each different cat
        marker = CAT_MARKERS[j % len(CAT_MARKERS)]
        # Plot every observation for this iterated cat, mapping each DOY value with the linear normaliser and the chosen colour map
        sc = ax.scatter(sub["absolute_salinity"], sub["conservative_temperature"],
                        c=doys, cmap=DOY_CMAP, norm=norm, marker=marker, s=12, zorder=3)
        if multi_cat:
            handles.append(mlines.Line2D([], [], marker=CAT_MARKERS[j % len(CAT_MARKERS)], color="grey",
                  linestyle="None", markersize=6, label=f"({borehole}-{AVG_PRESSURES[cat]:.0f} dbar)"))

    # Draw the colourbar labelled with calender months
    # Only draw the colourbar is at least one scatter was drawn
    if sc is not None:
        # Add the colourbar to the figure
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        # Lable the colourbar axis
        cbar.set_label("Day of Year", fontsize=12)
        # Call the helper function to find which month start DOYs fall in the data's range, returning positions and abbreviated names
        ticks, tick_labels = _doy_month_ticks(min(all_doys), max(all_doys))
        # Set the ticks and tick labels
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(tick_labels)

    # Produce a legend for the markers defining different cats, if there is more than one cat
    if multi_cat:
        ax.legend(handles=handles, fontsize=10, loc="best")

    ts_plot_overlays(ax, fig, all_data, all_cats, ylim_temp, xlim_sal,
                         allow_selection=False, year=year, average=average)

    ax.set_ylabel(r"Conservative Temperature ($\Theta$) (°C)", fontsize=14)

    plt.tight_layout()
    plt.show()


# ── Public wrapper ─────────────────────────────────────────────────────────────
def plot_ts(df, mode, boreholes=None, borecats=None, year=None, average="median", regional=False,
            season_by_season=False, months=None, columns=2, allow_selection=True):
    """
    Unified T-S plot dispatcher.

    Parameters
    ----------
    mode : {"month", "seasonal", "doy"}
        "month"    — one panel per month, cats coloured by depth position.
        "seasonal" — all data on one plot (or 2×2 by season), coloured by
                     season/month using discrete colourmap shading.
        "doy"      — continuous day-of-year colour gradient, with a labelled
                     colourbar showing the seasonal progression.

    borecats : {borehole: [cats]} dict 

    year : int or None
        Specific austral year (Dec year-1 through Nov year); None aggregates
        across all years using median or mean.
    average : {"median", "mean"}
        Statistic used when year is None.
    regional : bool
        True → wide temperature axis; False → ice-shelf-water cavity scale.
    season_by_season : bool
        seasonal mode only — if True, produce a 2×2 panel split by season.
    months : list[int] or None
        month mode only — which months to show as panels (default: all 12).
    columns : int
        month mode only — number of subplot columns.
    allow_selection : bool
        seasonal mode only — enable interactive Gade anchor selection.
    """
    if mode == "month":
        plot_ts_months(df, boreholes, borecats, months, year, average, regional, columns)

    elif mode == "seasonal":
        plot_ts_seasonal_wrapper(df, borecats, season_by_season, regional, year, average, allow_selection)

    elif mode == "doy":
        plot_ts_doy(df, borecats, year, average, regional)
        
    else:
        raise ValueError(f"Unknown mode {mode!r}. Choose 'month', 'seasonal', or 'doy'.")
