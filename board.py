import pygame

CELL_SIZE = 40
BOARD_SIZE = 10

class Board:
    def __init__(self, x_offset, y_offset):
        self.grid = [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.x_offset = x_offset
        self.y_offset = y_offset

    def draw(self, screen, title, font):
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (self.x_offset, self.y_offset - 30))

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                rect = pygame.Rect(
                    self.x_offset + x * CELL_SIZE,
                    self.y_offset + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)

                value = self.grid[y][x]
                if value in ['X', 'O', '@']:
                    if value == 'X':
                        color = (255, 0, 0)       # Hit = Merah
                    elif value == 'O':
                        color = (0, 0, 255)       # Miss = Biru
                    elif value == '@':
                        color = (0, 255, 0)       # Ship = Hijau
                    pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 3)

    def get_cell(self, pos):
        x, y = pos
        grid_x = (x - self.x_offset) // CELL_SIZE
        grid_y = (y - self.y_offset) // CELL_SIZE
        if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
            return grid_y, grid_x
        return None

    def update_cell(self, row, col, value):
        self.grid[row][col] = value

    def place_ship(self, start, length, horizontal=True):
        r, c = start
        for i in range(length):
            if horizontal:
                self.grid[r][c + i] = '@'
            else:
                self.grid[r + i][c] = '@'

    def is_valid_placement(self, start, length, horizontal=True):
        r, c = start
        for i in range(length):
            if horizontal:
                if c + i >= BOARD_SIZE or self.grid[r][c + i] != '~':
                    return False
            else:
                if r + i >= BOARD_SIZE or self.grid[r + i][c] != '~':
                    return False
        return True
