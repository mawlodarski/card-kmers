
import argparse
import os
import pandas as pd
# may need to do pip install umap-learn
import umap.umap_ as umap
import plotly.express as px
import numpy as np

# Load data
df = pd.read_csv('unclassified_table.csv')
df_binary = pd.get_dummies(df.set_index('card_short_term')['species'], dtype=float)

# UMAP projection
umap_3d = umap.UMAP(n_neighbors=3, n_components=3, metric='jaccard', init='random', random_state=0)
proj_3d = umap_3d.fit_transform(df_binary)

# Add UMAP coordinates to DataFrame
df['umap_x'] = proj_3d[:, 0]
df['umap_y'] = proj_3d[:, 1]
df['umap_z'] = proj_3d[:, 2]

# Clip 'count' column to ensure minimum marker size
min_marker_size = 10
df['newcount'] = df['count'].clip(lower=min_marker_size)

# Define a custom color scale based on magma with green at the end
colour_gradient = [
    [0.0, "#000000"],   # Black at 0.0
    [0.25, "#320000"],  # Very dark red at 0.25
    [0.5, "#640000"],   # Dark red at 0.5
    [0.75, "#8B0000"],  # Redder dark red at 0.75
    [1.0, "#8B0000"]    # Dark red at 1.0
]

# Plot 3D scatter with hidden x, y, z in hover data
fig_3d = px.scatter_3d(
    df,
    x='umap_x',
    y='umap_y',
    z='umap_z',
    hover_data={
        "umap_x": False,  # Hide x coordinate
        "umap_y": False,  # Hide y coordinate
        "umap_z": False,  # Hide z coordinate
        "species": True,
        "card_short_term": True,
        "newcount": False
    },
    #text='card_short_term',
    text='species',
    size='newcount',
    size_max=130,
    color='count',
    color_continuous_scale=colour_gradient 
)

# Hide axes in the scene
fig_3d.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)

# Save and display the plot
fig_3d.write_html('umap_mutants_species_labels.html')
#fig_3d.show()

