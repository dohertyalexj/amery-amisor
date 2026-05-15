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

def get_gade_anchors(cat, plot_data, ax, fig, year=None, average="median"):
    """Interactively select or retrieve saved Gade anchor points for this cat."""
    key = (cat, year if year is not None else average)

    # Ask the user if they would like to select an anchoring point for the meltwater mixing line interactively
    response = input(f"Would you like to select a new meltwater mixing (Gade) line for cat{cat}? [y/n]: ").strip().lower()
    
    # Handle if the user response is negative
    if response != "y":
        # Return previously saved anchors or an empty list if none previously saved
        return GADE_ANCHORS.get(key, [])
    
    # Initialise an empty list to add new selected anchoring points to
    anchors = []

    # Add an invisible pickable scatter on top of the data to make the approach a bit cleaner
    sa = plot_data["absolute_salinity"].values
    ct = plot_data["conservative_temperature"].values
    picker_scatter = ax.scatter(sa, ct, picker=True, pickradius=10, alpha=0, zorder=10)
    
    # Define a mutable container to hold the selected points
    selected = {"point": None}

    def on_pick(event):
        # Check click was on invisible scatter
        if event.artist == picker_scatter:
            # Find the index of the point clicked
            idx = event.ind[0]
            # Store data coordinates of clicked point
            selected["point"] = (sa[idx], ct[idx])
            # Break out of event loop
            fig.canvas.stop_event_loop()

    # Register on_pick as a callback
    cid = fig.canvas.mpl_connect("pick_event", on_pick)
    
    # Define an inner helper function to retrieve the one click
    def get_one_click(prompt):
        # Reset the container before each click so that we know the user has actually something
        selected["point"] = None
        # Display the prompt for the user and redraw the plot 
        print(prompt)
        fig.canvas.draw_idle()
        # Run matplotlib's event loop and block function (remains interactive)
        fig.canvas.start_event_loop(timeout=-1) 
        return selected["point"]
    
    # Prompt the user to make their first anchoring point selection
    p1 = get_one_click("Click a data point for the first Gade anchor...")
    if p1:
        # Add the selected point to the list of new selected anchoring points
        anchors.append(p1)
        # Plot and redraw an open circle to show which point has been selected
        ax.plot(*p1, "ko", markersize=10, mfc="none", mew=2)
        fig.canvas.draw_idle()
    
    # Ask the user if they would like to make a second anchoring point selection
    response2 = input(f"Select a second Gade line for cat{cat}? [y/n]: ").strip().lower()
    if response2 == "y":
        # Prompt the user to make their secibd anchoring point selection
        p2 = get_one_click("Click a data point for the second Gade anchor...")
        if p2:
            anchors.append(p2)
            ax.plot(*p2, "ko", markersize=10, mfc="none", mew=2)
            fig.canvas.draw_idle()
            
    # Disconnects the callback
    fig.canvas.mpl_disconnect(cid)

    # Clean up the invisible picker scatter
    picker_scatter.remove()
    
    GADE_ANCHORS[key] = anchors
    return anchors

# Define a function to take the (SA, CT) tuple of points just clicked and compare them to our dataset of actual (SA, CT) points
def _snap_to_nearest(clicked_point, plot_data):
    """Find the nearest actual data point to a clicked location."""
    clicked_x, clicked_y = clicked_point
    # Compute the Euclidean distance from the clicked point to every data point
    # Distances is a pandas Series
    distances = np.hypot(plot_data["absolute_salinity"] - clicked_x,plot_data["conservative_temperature"] - clicked_y)
    # Find the index label in distances for the minimum distance value
    nearest_idx = distances.idxmin()
    # Look up the row for the nearest datapoint 
    nearest = plot_data.loc[nearest_idx]
    return (nearest["absolute_salinity"], nearest["conservative_temperature"])

# Define a function to plot different overlays to aid in identifying and interpreting the source water masses
def ts_plot_overlays(ax, fig, plot_data, cat, ylim_temp, xlim_sal, allow_selection=True, year=None, average="median"):
    # Define the range of temp and salinity over which we will plot these
    salinity_range = np.linspace(xlim_sal[0], xlim_sal[1], 100)
    temp_range = np.linspace(ylim_temp[0], ylim_temp[1], 100)
    pressure_average = AVG_PRESSURES[f"{cat}"]

    # 1. Freezing point temperature line at 0 dbar (saturation fraction = 0)
    CT_freeze_0 = gsw.CT_freezing(salinity_range, 0, 0)
    ax.plot(salinity_range, CT_freeze_0, "b--", lw=1, label="_")
    label_curve_tangent(ax, salinity_range, CT_freeze_0, 0.125, r"$\Theta_f$ (0 dbar)", "b", 14)

    # 2. Freezing point temperature line at average mooring pressure (determined at deployment)
    CT_freeze_p = gsw.CT_freezing(salinity_range, pressure_average, 0)
    ax.plot(salinity_range, CT_freeze_p, "b-", lw=1, label="_")
    label_curve_tangent(ax, salinity_range, CT_freeze_p, 0.125, fr"$\Theta_f$ ({pressure_average:.0f} dbar)", "b", 14)

    # 3. Neutral density curves from Blanckensee et al. (2024)
    ax.plot(x_curve1, y_curve1, "r-", lw=1.5)
    ax.plot(x_curve2, y_curve2, "r-", lw=1.5)
    # Add labels to neutral density curves
    label_curve_tangent(ax, x_curve2, y_curve2, 0.5, r"$\mathrm{\gamma_n=28.00}$", "red", 14)
    label_curve_tangent(ax, x_curve1, y_curve1, 0.5, r"$\mathrm{\gamma_n=28.27}$", "red", 14)

    # 4. Isopycnals (potential density anomaly contours) referenced to 0 dbar (sigma_0)
    # This is the anomaly, i.e. density minus 1000 kg/m^3 (appropriate for shallowish waters)
    salinity_grid, temp_grid = np.meshgrid(salinity_range, temp_range)
    sigma = gsw.sigma0(salinity_grid, temp_grid)
    cs = ax.contour(salinity_grid, temp_grid, sigma, colors="grey", linestyles=":", linewidths=0.6)
    ax.clabel(cs, inline=True, fontsize=10, fmt="%.2f")

    # 5. Meltwater (Gade) line — anchored at warmest/saltiest source water
    # To anchor this meltwater mixing line, we want to anchor it to the warmest/saltiest water mass observed (meltwater modified ISW should freshen
    # and cool from this point, along the meltwater mixing line)
    # First we check if we will be allowing a new selection to occur in this function call, if not, we see if there is a previously
    # anchor available to use
    if allow_selection:
        # Interactive choose anchoring point(s)
        anchors = get_gade_anchors(cat, plot_data, ax, fig, year=year)
    else:
        key = (cat, year if year is not None else average)
        anchors = GADE_ANCHORS.get(key, [])

    # Iterate over the selected anchors, and plot a meltwater mixing line for each
    for salinity_source, temp_source in anchors:
        # Ice temperature: in situ freezing temperature at source pressure
        t_ice = gsw.t_freezing(salinity_source, pressure_average, 0)

        # Get dSA/dCT from gsw, invert to get dCT/dSA for plotting
        dSA_dCT = gsw.ice.melting_ice_SA_CT_ratio(salinity_source, temp_source, pressure_average, t_ice)
        slope = 1 / dSA_dCT  # dCT/dSA
        
        CT_gade = temp_source + slope * (salinity_range - salinity_source)
        ax.plot(salinity_range, CT_gade, "k--", lw=1.5, label="Meltwater mixing line")
        ax.plot(salinity_source, temp_source, "ko", markersize=6)

    
        
    
        
   