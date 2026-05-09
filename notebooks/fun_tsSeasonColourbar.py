import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Define a function to build the legend with a nice colour scale
def add_season_colorbars(fig, season_cmaps, shade_levels):
    # Reserve space at the bottom of the figure for the legend (as a percentage of the figure size)
    fig.subplots_adjust(bottom=0.14)
    
    # Define the coordinates and dimensions of the legend
    legend_x = 0.10     # starts the legend 10% from the left edge of the figure
    legend_y = 0.06     # starts the legend 6% from the bottom of the figure
    legend_w = 0.80     # the legend spans 80% of the figure width (i.e. spans 10 to 90% of the width lenght, centering it)
    bar_height = 0.01   # each bar is 1% of the figure height

    n_seasons = len(season_cmaps)
    # Divide the legend into equal width sections, of which there will be 4 (as there are 4 seasons)
    section_width = legend_w / n_seasons    # each season gets 1/4 of the legend width
    # Define the proportion of each section which the block of three bars will take up
    block_total_width = section_width * 0.8 # colour bars together will take up 50% of the section
    # Define the y-coordinate (bottom edge) of each bar
    bar_y = legend_y - bar_height / 2

    # Iterate over each season
    for i, (season_name, (cmap_name, months)) in enumerate(season_cmaps.items()):
        # Extract the colour map and evaluate it at the three different shading levels specified earlier
        cmap = plt.get_cmap(cmap_name)
        block_colors = [cmap(s) for s in shade_levels]

        # Compute the x-coordinate (left edge) of the section for this iteration of season
        section_x = legend_x + i * section_width

        # Compute the x-coordinate (left edge) of the first colour block 
        block_x = section_x + (section_width - block_total_width) / 2

        # Find the x-coordinate of the centre of the colour blocks (to use later to label the season)
        block_centre_x = block_x + block_total_width / 2

        # Iterates through the three colour blocks
        for j, color in enumerate(block_colors):
            # Construct a rectangle patch for each coloured, ensuring x-position shift with each iteration of colour block
            block = mpl.patches.Rectangle((block_x + j * (block_total_width / 3), bar_y), block_total_width / 3, bar_height, transform=fig.transFigure, facecolor=color, edgecolor="none", zorder=6)
            fig.add_artist(block)

            # Abbreviate the month to the first letter of that month
            month_letter = pd.Timestamp(2001, months[j], 1).strftime("%b")[0]
            # Draw the month letter centred 0.5% of the figure height above the colour block
            fig.text(block_x + (j + 0.5) * (block_total_width / 3), bar_y + bar_height + 0.005, month_letter, ha="center", va="bottom", fontsize=9, zorder=6)

        # Draw the season label 0.5% of the figure height below colour block 
        fig.text(block_centre_x, bar_y - 0.005, season_name.split(" ")[0], ha="center", va="top", fontsize=10, zorder=6)