import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os

# Grid dimensions
MARGIN = 1
BACKGROUND_COLOR = (30, 30, 30)

# Rotation mappings (precomputed)
TILE_ROTATIONS = {
    0b0000: (0, "empty"),   # No bits set: empty tile
    0b0001: (270, "mid"),   # Single opening on left
    0b0010: (0, "mid"),     # Single opening on bottom
    0b0100: (90, "mid"),    # Single opening on right
    0b1000: (180, "mid"),   # Single opening on top
    0b0011: (180, "angle"), # Angle (left-bottom)
    0b0110: (270, "angle"), # Angle (bottom-right)
    0b1100: (0, "angle"),   # Angle (right-top)
    0b1001: (90, "angle"),  # Angle (top-left)
    0b0101: (90, "line"),   # Line (left-right)
    0b1010: (0, "line"),    # Line (top-bottom)
    0b0111: (180, "te"),    # T-junction (bottom-right-left)
    0b1011: (90, "te"),     # T-junction (top-left-bottom)
    0b1101: (0, "te"),      # T-junction (right-top-left)
    0b1110: (270, "te"),    # T-junction (top-right-bottom)
    0b1111: (0, "cross"),   # Cross (four openings)
}

def load_tile_images(image_folder, cell_size):
    """
    Load tile images and pre-rotate all variants for fast lookup.
    """
    base_images = {
        "empty": Image.open(f"{image_folder}/empty.png"),
        "mid": Image.open(f"{image_folder}/mid.png"),
        "line": Image.open(f"{image_folder}/line.png"),
        "angle": Image.open(f"{image_folder}/angle.png"),
        "te": Image.open(f"{image_folder}/te.png"),
        "cross": Image.open(f"{image_folder}/cross.png"),
    }

    # Resize to cell size
    for key in base_images:
        base_images[key] = base_images[key].resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    
    # Pre-rotate all variants and store as numpy arrays for fast rendering
    rotated_images = {}
    for tile_value, (rotation, tile_type) in TILE_ROTATIONS.items():
        img = base_images[tile_type]
        if rotation != 0:
            img = img.rotate(rotation, expand=False)
        rotated_images[tile_value] = np.array(img)
    
    return rotated_images

def display_grid(grid, images, cell_size):
    """
    Generate and display a matplotlib image of the grid.
    Uses pre-rotated images and direct numpy composition for speed.
    
    Args:
        grid: numpy array representing the grid
        images: dictionary of pre-rotated tile images as numpy arrays
        cell_size: size of each cell in pixels
    """
    rows, cols = grid.shape
    
    # Compose the full grid image as a numpy array
    canvas_height = rows * (cell_size + MARGIN)
    canvas_width = cols * (cell_size + MARGIN)
    canvas = np.ones((canvas_height, canvas_width, 4), dtype=np.uint8) * 30
    
    # Place each pre-rotated tile directly on canvas
    for row in range(rows):
        for col in range(cols):
            tile_value = grid[row, col]
            tile_img = images[tile_value]
            
            y_start = row * (cell_size + MARGIN)
            x_start = col * (cell_size + MARGIN)
            
            canvas[y_start:y_start + cell_size, 
                   x_start:x_start + cell_size] = tile_img
    
    # Create figure and display
    fig, ax = plt.subplots(figsize=(cols * cell_size / 100, rows * cell_size / 100), dpi=100)
    ax.imshow(canvas)
    ax.axis('off')
    fig.patch.set_facecolor('#1e1e1e')
    
    plt.tight_layout(pad=0)
    plt.show()
