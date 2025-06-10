import pygame

# Constants for cell size and board size
CELL_SIZE = 40
BOARD_SIZE = 10

class Board:
    def __init__(self, x_offset, y_offset):
        # Initialize a BOARD_SIZE x BOARD_SIZE grid filled with water '~'
        self.grid = [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        # Position offsets to draw this board on screen
        self.x_offset = x_offset
        self.y_offset = y_offset

    def draw(self, screen, title, font):
        # Draw the board title above the grid
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (self.x_offset, self.y_offset - 30))

        # Draw the board grid and any markers inside cells
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                # Draw grid cell rectangle
                rect = pygame.Rect(
                    self.x_offset + x * CELL_SIZE,
                    self.y_offset + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)

                # Draw marker if cell contains hit, miss, or ship
                value = self.grid[y][x]
                if value in ['X', 'O', '@']:
                    if value == 'X':
                        color = (255, 0, 0)       # Hit = Red
                    elif value == 'O':
                        color = (0, 0, 255)       # Miss = Blue
                    elif value == '@':
                        color = (0, 255, 0)       # Ship = Green
                    pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 3)

    def get_cell(self, pos):
        # Convert screen position to corresponding grid cell (row, col)
        x, y = pos
        grid_x = (x - self.x_offset) // CELL_SIZE
        grid_y = (y - self.y_offset) // CELL_SIZE
        # Return cell if inside grid, otherwise None
        if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
            return grid_y, grid_x
        return None

    def update_cell(self, row, col, value):
        # Update value of a specific grid cell
        self.grid[row][col] = value

    def place_ship(self, start, length, horizontal=True):
        # Place ship of given length on the grid starting at 'start'
        r, c = start
        for i in range(length):
            if horizontal:
                self.grid[r][c + i] = '@'  # Mark horizontal ship cells
            else:
                self.grid[r + i][c] = '@'  # Mark vertical ship cells

    def is_valid_placement(self, start, length, horizontal=True):
        # Check if ship placement is valid (inside grid and no overlap)
        r, c = start
        for i in range(length):
            if horizontal:
                if c + i >= BOARD_SIZE or self.grid[r][c + i] != '~':
                    return False
            else:
                if r + i >= BOARD_SIZE or self.grid[r + i][c] != '~':
                    return False
        return True
