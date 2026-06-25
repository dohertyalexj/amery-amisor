import gsw
import numpy as np
import pickle
import matplotlib.pyplot as plt 
from fun_curveLabel import label_curve_tangent

# Load in the neutral density contours as determined by Blanckensee et al. (2024)
with open("../data/external/SiennaNeve-CDObs-203a48c/Notebooks/neu_dens_contours.pkl", "rb") as f: 
    nd_contours = pickle.load(f)
x_curve1 = nd_contours["x_curve1"]  # 28.27 contour
y_curve1 = nd_contours["y_curve1"]
x_curve2 = nd_contours["x_curve2"]  # 28.00 contour
y_curve2 = nd_contours["y_curve2"]

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

# Initialise a resuable dictionary keyed by cat and year (or average)
GADE_ANCHORS = {}

# Define a function to plot different overlays to aid in identifying and interpreting the source water masses
def ts_plot_overlays(ax, fig, plot_data, cat, ylim_temp, xlim_sal, allow_selection=True, year=None, average="median"):
    # Define the range of temp and salinity over which we will plot these
    salinity_range = np.linspace(xlim_sal[0], xlim_sal[1], 100)
    temp_range = np.linspace(ylim_temp[0], ylim_temp[1], 100)

    # Normalise cat input to always be a list
    cats = [cat] if isinstance(cat, str) else list(cat)
    pressures = [AVG_PRESSURES[f"{c}"] for c in cats]

    # ---------- 1. Freezing point temperature line at 0 dbar (saturation fraction = 0) ----------
    CT_freeze_0 = gsw.CT_freezing(salinity_range, 0, 0)
    ax.plot(salinity_range, CT_freeze_0, "b--", lw=1, label="_")
    label_curve_tangent(ax, salinity_range, CT_freeze_0, 0.125, r"$\Theta_f$ (0 dbar)", "b", 14)

    # ---------- 2. Freezing point temperature line at average mooring pressure (determined at deployment) ----------
    # Sort by pressure so colours step from light (shallow) to dark (deep)
    cats_sorted = sorted(zip(cats, pressures), key=lambda x: x[1])
    n_cats = len(cats_sorted)
    
    # Shades from light grey to black
    if n_cats == 1:
        shades = ["black"]
    else:
        shades = [str(0.6 - 0.6 * i / (n_cats - 1)) for i in range(n_cats)]
        # "0.6" is light grey, "0.0" is black — interpolated in between
    
    # Iterate over each cat and corresponding pressure
    for (c, p), shade in zip(cats_sorted, shades):
        CT_freeze_p = gsw.CT_freezing(salinity_range, p, 0)
        ax.plot(salinity_range, CT_freeze_p, "-", color=shade, lw=1, label="_")
        label_curve_tangent(ax, salinity_range, CT_freeze_p, 0.125, fr"$\Theta_f$ ({p:.0f} dbar)", shade, 14)

    # ---------- 3. Neutral density curves from Blanckensee et al. (2024) ----------
    ax.plot(x_curve1, y_curve1, "r-", lw=1.5)
    ax.plot(x_curve2, y_curve2, "r-", lw=1.5)
    # Add labels to neutral density curves
    label_curve_tangent(ax, x_curve2, y_curve2, 0.5, r"$\mathrm{\gamma_n=28.00}$", "red", 14)
    label_curve_tangent(ax, x_curve1, y_curve1, 0.5, r"$\mathrm{\gamma_n=28.27}$", "red", 14)

    # ---------- 4. Isopycnals (potential density anomaly contours) referenced to 0 dbar (sigma_0) ----------
    # This is the anomaly, i.e. density minus 1000 kg/m^3 (appropriate for shallowish waters)
    salinity_grid, temp_grid = np.meshgrid(salinity_range, temp_range)
    sigma = gsw.sigma0(salinity_grid, temp_grid)
    cs = ax.contour(salinity_grid, temp_grid, sigma, colors="grey", linestyles=":", linewidths=0.6)
    ax.clabel(cs, inline=True, fontsize=10, fmt="%.2f")

    # ---------- 5. Meltwater (Gade) line — anchored at warmest/saltiest source water ----------
    # To anchor this meltwater mixing line, we want to anchor it to the warmest/saltiest water mass observed (meltwater modified ISW should freshen
    # and cool from this point, along the meltwater mixing line)
    if len(cats) == 1:
        key_single = (cats[0], year if year is not None else average)
        anchors = GADE_ANCHORS.get(key_single, [])
    else:
        key_all = ("all", None)
        anchors = GADE_ANCHORS.get(key_all, [])

    if len(cats) == 1:
        gade_pressure = AVG_PRESSURES[f"{cats[0]}"]
    else:
        gade_pressure = np.mean(pressures)  # or max(pressures), or whatever you prefer

    # Iterate over the selected anchors, and plot a meltwater mixing line for each
    for salinity_source, temp_source in anchors:
        # Ice temperature: in situ freezing temperature at source pressure
        t_ice = gsw.t_freezing(salinity_source, gade_pressure, 0)

        # Get dSA/dCT from gsw, invert to get dCT/dSA for plotting
        dSA_dCT = gsw.ice.melting_ice_SA_CT_ratio(salinity_source, temp_source, gade_pressure, t_ice)
        slope = 1 / dSA_dCT  # dCT/dSA
            
        CT_gade = temp_source + slope * (salinity_range - salinity_source)
        ax.plot(salinity_range, CT_gade, "k--", lw=1.5, label="_")
        #ax.plot(salinity_source, temp_source, "ko", markersize=6)