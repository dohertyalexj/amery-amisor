import numpy as np

# Define a function to label the neutral density curves tangentially
def label_curve_tangent(ax, x_curve, y_curve, fraction, text, color, fontsize, **kwargs):
    n = len(x_curve)
    # Define an index for the anchor point based on the length of the curve and the fractional distance along it
    idx = int(fraction * (n - 1))
    # Define the anchor point
    anchor_point = (x_curve[idx], y_curve[idx])

    # Pick points neighbouring the anchoring point to estimate the tangent
    i0 = max(idx - 1, 0)
    i1 = min(idx + 1, n - 1)

    # Convert these points to display coordinates so the angle accounts of the axis scaling
    p0 = ax.transData.transform((x_curve[i0], y_curve[i0]))
    p1 = ax.transData.transform((x_curve[i1], y_curve[i1]))
    # Calculate the change in display in display coordinates in the x and y directions
    dx_display = p1[0] - p0[0] 
    dy_display = p1[1] - p0[1] 

    # Calculate the angle of the slope 
    angle = np.degrees(np.arctan2(dy_display, dx_display))
    
    # Find a perpendicular unit vector in display coordinates to create a buffer between the curve and the label 
    length = np.hypot(dx_display, dy_display)
    perp_x = -dy_display / length
    perp_y = dx_display / length

    # Find the anchor point and the offset point from here in display coordinates
    anchor_display = ax.transData.transform(anchor_point)
    offset_display = (anchor_display[0] + 10 * perp_x, anchor_display[1] + 10 * perp_y)

    # Convert this offset point back into data coordinates to be able to plot it correctly
    offset_point = ax.transData.inverted().transform(offset_display)

    # Check if the anchor point falls within the plot's visible area and if it doesn't we ignore this label
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    if not (xlim[0] <= anchor_point[0] <= xlim[1] and ylim[0] <= anchor_point[1] <= ylim[1]):
        return 

    ax.text(offset_point[0], offset_point[1], text, rotation=angle, rotation_mode="anchor", ha="center", va="center", color=color, fontsize=fontsize, **kwargs)