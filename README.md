## board.py
  ### Board Class initialization
  ```py
  class Board:
    def __init__(self, x_offset, y_offset):
        self.grid = [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.x_offset = x_offset
        self.y_offset = y_offset
  ```
  ### Draw the board on the screen
  ```py
  def draw(self, screen, title, font):
    # draw title and board grid
    # draw markers (X = hit, O = miss, @ = ship)
  ```
  ### Get Cell from mouse position
  ``` py
  def get_cell(self, pos):
    # Convert mouse coordinates to grid cell indices
  ```
  ### Update Cell
  ```py
  def update_cell(self, row, col, value):
  ```
  ### Place the ships
  ```py
  def place_ship(self, start, length, horizontal=True):
    # Place a ship on the grid horizontally or vertically
  ```
  ### Validate ship placement
  ```py
  def is_valid_placement(self, start, length, horizontal=True):
    # Check if a ship can be placed without overlap or going out of bounds
  ```

## client.py
  ### main func
  ```py
  def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Battleship Client")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))
    print("Connected to server")

    game = BattleshipGame(screen, is_host=False, conn=s)
    game.run()

    pygame.quit()
  ```
  - this creates TCP socket, connects battleship server, create the BattleshipGame, then runs the game in loop
## game.py
