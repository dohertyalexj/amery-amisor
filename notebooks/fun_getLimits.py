# Define a helper function to return the appropriate limits for the T-S plots
def _get_limits(regional):
    """Return (xlim_sal, ylim_temp) appropriate for the chosen plot mode."""
    xlim_sal = (34.3, 34.8)
    ylim_temp = (-2.4, 0.0) if regional else (-2.4, -1.7)
    return xlim_sal, ylim_temp