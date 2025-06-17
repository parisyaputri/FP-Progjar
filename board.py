import pygame

CELL_SIZE = 40
BOARD_SIZE = 10

# A nice color for the ships
SHIP_COLOR = (150, 160, 180) 

class Board:
    def __init__(self, x_offset, y_offset):
        # Grid stores: '~' water, 'X' hit, 'O' miss, or a tuple (ship_id, length) for a ship part
        self.grid = [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.x_offset = x_offset
        self.y_offset = y_offset

    def draw(self, screen, title, font, show_ships=True):
        # Draws the board, title, and ships.
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (self.x_offset, self.y_offset - 40))

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                rect = pygame.Rect(
                    self.x_offset + x * CELL_SIZE,
                    self.y_offset + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                # Draw cell with a border
                pygame.draw.rect(screen, (40, 50, 70), rect) # Dark sea color
                pygame.draw.rect(screen, (60, 80, 110), rect, 2) # Lighter border

                value = self.grid[y][x]
                if isinstance(value, tuple) and show_ships:
                    # It's a ship piece, draw a rectangle for it
                    pygame.draw.rect(screen, SHIP_COLOR, rect.inflate(-4, -4)) # Inset rect
                elif value == 'X': # Hit
                    pygame.draw.circle(screen, (255, 60, 30), rect.center, CELL_SIZE // 3)
                elif value == 'O': # Miss
                    pygame.draw.circle(screen, (150, 180, 220), rect.center, CELL_SIZE // 4)

    def get_cell(self, pos):
        # Converts mouse position to grid coordinates.
        x, y = pos
        if not (self.x_offset <= x < self.x_offset + BOARD_SIZE * CELL_SIZE and
                self.y_offset <= y < self.y_offset + BOARD_SIZE * CELL_SIZE):
            return None
        grid_x = (x - self.x_offset) // CELL_SIZE
        grid_y = (y - self.y_offset) // CELL_SIZE
        return grid_y, grid_x

    def place_ship(self, start, length, horizontal):
        # Places a ship on the grid, storing its ID and length.
        r, c = start
        ship_id = f'ship_{length}_{r}_{c}' # Unique ID for each ship
        for i in range(length):
            if horizontal:
                self.grid[r][c + i] = (ship_id, length)
            else:
                self.grid[r + i][c] = (ship_id, length)
        return ship_id

    def is_valid_placement(self, start, length, horizontal=True):
        # Checks if a ship placement is valid.
        r, c = start
        for i in range(length):
            if horizontal:
                if c + i >= BOARD_SIZE or self.grid[r][c + i] != '~':
                    return False
            else:
                if r + i >= BOARD_SIZE or self.grid[r + i][c] != '~':
                    return False
        return True