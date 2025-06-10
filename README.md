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
  ### Initialization
  ```py
  def __init__(self, screen, is_host, conn):
        ...
  ```
  - sets up the screen, stores the network connection, use reset_game to start fresh
  ### Reset game
    ```py
    def reset_game(self):
    ...
    ```
  - create new boards, tracks whether ship are placed or not, defines the ships to place, UI button
  ### Check win
  ```py
  def check_win(board)
  ...
  ```
  - Returns True if there are no ships ('@') left on the board → player has won
  ### Orientation Button
  ```py
  def draw_orientation_button()
  ...
  ```
  - draws button for player to press for ship orientation
  ### draw legend
  ```py
  def draw_legend()
  ...
  ```
  - Blue : miss
  - Red : hit
  ### draw end buttons
  ```py
  def draw_end_buttons()
  ...
  ```
  - user choose between play again or exit game button
  ### draw game screen
  ```py
  def draw(self)
  ...
  ```
  - shows win/lose message
  - when placing ship, show the board and orientation button
  - shows wait for opponent msg
  - show both board (player's board and enemy's board to be hit)
  ### Handle mouse click
  ```py
  def handle_click(pos)
  ...
  ```
  - If game over: play again will reset the game, exit game will quit the game
  - Placing ships: orientation button to change horizontal/vertical, click on valid cell to place ship
  - during turn: clicking on enemy's board will result in sending attack to opponent
  ### Send data to server
  ```py
  def send(data)
  ...
  ```
  - sends data using pickle through socket to other player
  ### Receive data
  ```py
  def receive(self)
  ...
  ```
  - Continuously listens for incoming messages:
    - 'attack' → process enemy attack, send result.

    - 'result' → update enemy board with result.

    - 'ready' → opponent has finished placing ships.

    -  'game_over' → game over message from opponent.

    - 'reset' → reset game.
  ### game loop
  ```py
  def run(self)
  ...
  ```
  - runs main game in loop
## server.py
  ### main function
  ```py
  def main():
  pygame.init()
  screen = pygame.display.set_mode((1000, 600))
  pygame.display.set_caption("Battleship Server")
  ```
  - sets up the pygame window
  ### setup server socket
  ```py
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(1)
  ```
  - creates TCP socket, binds it to host and port, listen for incoming connection
  ### accept connection
  ```py
  conn, addr = s.accept()
  print("Client connected from", addr)
  ```
  - waits for client to connect
  ### run game
  ```py
  game = BattleshipGame(screen, is_host=True, conn=conn)
  game.run()
  ```

