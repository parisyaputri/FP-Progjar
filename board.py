import pygame

# size of each cell in pixels
CELL_SIZE = 40
# 10 x 10 board
BOARD_SIZE = 10

class Board:
    def __init__(self, x_offset, y_offset):
        # Initialize an empty board with '~' as water
        self.grid = [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.x_offset = x_offset    # X offset for drawing the board
        self.y_offset = y_offset    # Y offset for drawing the board

    def draw(self, screen, title, font):
        # Draw board title
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (self.x_offset, self.y_offset - 30))
        # Draw cells
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                # Define each cell rectangle
                rect = pygame.Rect(self.x_offset + x * CELL_SIZE,
                                   self.y_offset + y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                # Draw cell border
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                value = self.grid[y][x]
                # Draw symbols: X (hit), O (miss), @ (ship)
                if value in ['X', 'O', '@']:
                    color = (255, 0, 0) if value == 'X' else (0, 0, 255) if value == 'O' else (0, 255, 0)
                    pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 3)

    def get_cell(self, pos):
        # Convert mouse position to grid coordinates
        x, y = pos
        grid_x = (x - self.x_offset) // CELL_SIZE
        grid_y = (y - self.y_offset) // CELL_SIZE
        # Return cell if inside bounds
        if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
            return grid_y, grid_x
        return None

    def update_cell(self, row, col, value):
        # Set value at given cell
        self.grid[row][col] = value

    def place_ship(self, start, length, horizontal=True):
        # Place a ship ('@') of given length starting from `start`
        r, c = start
        for i in range(length):
            if horizontal:
                self.grid[r][c+i] = '@'
            else:
                self.grid[r+i][c] = '@'

    def is_valid_placement(self, start, length, horizontal=True):
        # Check if a ship can be placed at the start location
        r, c = start
        for i in range(length):
            if horizontal:
                # Out of bounds or not empty
                if c+i >= BOARD_SIZE or self.grid[r][c+i] != '~':
                    return False
            else:
                if r+i >= BOARD_SIZE or self.grid[r+i][c] != '~':
                    return False
        return True
