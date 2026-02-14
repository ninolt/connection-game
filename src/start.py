import src.solver as solve

import numpy as np

# Percentage of effective connections between vertices
# Example: 0.8 will generate a grid with many more "connections between cells" than 0.1
FILLED_RATIO = 0.5

# Function to generate a puzzle
# n: Height
# m: Width
def initiate(n: int, m: int) -> np.ndarray:
    if n <= 1 or m <= 1:
        raise Exception("Grid must have a positive size of at least 2x2")

    # Add a line all around the grid to represent a wall
    grid = np.full((n+2, m+2), fill_value=0b1111, dtype=np.uint8)

    # Create empty walls at top/bottom
    grid[0, :] = 0b0000
    grid[-1, :] = 0b0000

    # Create empty walls left/right except for entrance/exit
    grid[2:-1, 0] = 0b0000
    grid[1:-2, -1] = 0b0000

    # Initialize entrance/exit as unidirectional pipes towards the grid
    grid[1, 0] = 0b0100
    grid[-2, -1] = 0b0001

    # Remove connections between grid and walls (except entrance/exit)
    # Via XOR applied to all borders
    grid[1, 1:-1] = np.bitwise_xor(grid[1, 1:-1], np.full((m,), fill_value=0b1000, dtype=np.uint8))
    grid[-2, 1:-1] = np.bitwise_xor(grid[-2, 1:-1], np.full((m,), fill_value=0b0010, dtype=np.uint8))

    # Ignore entrance
    grid[2:-1, 1] = np.bitwise_xor(grid[2:-1, 1], np.full((n-1,), fill_value=0b0001, dtype=np.uint8))
    # Ignore exit
    grid[1:-2, -2] = np.bitwise_xor(grid[1:-2, -2], np.full((n-1,), fill_value=0b0100, dtype=np.uint8))

    # Select connections to remove
    nb_delete = round((1 - FILLED_RATIO) * (m - 1) * n)

    # We use -1 because rightmost tiles have no right neighbor, and same for bottom
    # A cell and its right neighbor
    horizontal_delete = np.random.choice((m - 1) * n, size=nb_delete, replace=False)
    # A cell and its bottom neighbor
    vertical_delete = np.random.choice((n - 1) * m, size=nb_delete, replace=False)

    # Extract coordinates in the grid
    horizontal_rows, horizontal_cols = np.unravel_index(horizontal_delete, (n, m - 1))
    vertical_rows, vertical_cols = np.unravel_index(vertical_delete, (n - 1, m))

    # Add 1 to indices to account for walls
    horizontal_rows += 1
    horizontal_cols += 1
    vertical_rows += 1
    vertical_cols += 1

    # Remove right connection of selected cells
    grid[horizontal_rows, horizontal_cols] = np.bitwise_xor(
        grid[horizontal_rows, horizontal_cols],
        np.full((nb_delete,), fill_value=0b0100)
    )

    # Remove left connection of right neighbors of selected cells
    grid[horizontal_rows, horizontal_cols + 1] = np.bitwise_xor(
        grid[horizontal_rows, horizontal_cols + 1],
        np.full((nb_delete,), fill_value=0b0001)
    )

    # Remove bottom connection of selected cells
    grid[vertical_rows, vertical_cols] = np.bitwise_xor(
        grid[vertical_rows, vertical_cols],
        np.full((nb_delete,), fill_value=0b0010)
    )

    # Remove top connection of neighbors below selected cells
    grid[vertical_rows + 1, vertical_cols] = np.bitwise_xor(
        grid[vertical_rows + 1, vertical_cols],
        np.full((nb_delete,), fill_value=0b1000)
    )
    
    # Randomly rotate tiles
    grid[1:-1, 1:-1] = np.vectorize(solve.left_rotate)(grid[1:-1, 1:-1],np.reshape(np.random.choice(4, size=n*m), (n, m)))

    return grid