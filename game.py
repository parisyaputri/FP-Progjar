import pygame
import threading
import pickle
from board import Board

WIDTH, HEIGHT = 1000, 600
FPS = 30

class BattleshipGame:
    def __init__(self, screen, is_host, conn):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 32)

        # create both boards
        self.my_board = Board(100, 100)
        self.enemy_board = Board(600, 100)

        self.conn = conn            # TCP connection to server
        self.is_host = is_host      # determines who starts first
        self.my_turn = is_host      # host starts first
        self.placed = False         # check if all ships are placed 
        self.enemy_placed = False   # check if all ships are placed (enemy)

        # Ships to place: (length, orientation)
        self.ships_to_place = [(5, True), (4, True), (3, True)]
        # to use vertical press the "Orientation" button
        self.current_orientation = True  # True = horizontal, False = vertical

        # orientation toggle button
        self.orientation_button = pygame.Rect(100, 30, 200, 40)

    def draw_orientation_button(self):
        # draw the orientation toggle button
        pygame.draw.rect(self.screen, (0, 100, 200), self.orientation_button)
        text = self.font.render("Orientation: " + ("Horizontal" if self.current_orientation else "Vertical"), True, (255, 255, 255))
        self.screen.blit(text, (110, 38))

    def draw(self):
        # Main draw method for UI
        self.screen.fill((0, 0, 0))
        if not self.placed:
            self.my_board.draw(self.screen, "Place Your Ships", self.font)
            self.draw_orientation_button()
        elif not self.enemy_placed:
            # Waiting screen
            self.screen.fill((0, 0, 0))
            msg = self.font.render("Waiting for opponent to place ships...", True, (255, 255, 255))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        else:
            # Gameplay mode
            self.my_board.draw(self.screen, "Your Board", self.font)
            self.enemy_board.draw(self.screen, "Enemy Board", self.font)

        pygame.display.flip()  # Update the screen

    def handle_click(self, pos):
        # Handle mouse click events
        if not self.placed:
            # Toggle orientation if button clicked
            if self.orientation_button.collidepoint(pos):
                self.current_orientation = not self.current_orientation
                return
            if not self.ships_to_place:
                return
            length, _ = self.ships_to_place[0]
            cell = self.my_board.get_cell(pos)
            if cell and self.my_board.is_valid_placement(cell, length, self.current_orientation):
                self.my_board.place_ship(cell, length, self.current_orientation)
                self.ships_to_place.pop(0)
                if not self.ships_to_place:
                    self.placed = True
                    self.send({'type': 'ready'})  # Notify opponent
        elif self.my_turn and self.enemy_placed:
            # Attack phase
            cell = self.enemy_board.get_cell(pos)
            if cell:
                self.send({'type': 'attack', 'cell': cell})
                self.my_turn = False

    def send(self, data):
        # Send data to the other player
        try:
            self.conn.sendall(pickle.dumps(data))
        except Exception as e:
            print("[SEND ERROR]", e)

    def receive(self):
        # Receive data from the other player in a separate thread
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                msg = pickle.loads(data)
                if msg['type'] == 'attack':
                    # Handle incoming attack
                    r, c = msg['cell']
                    hit = self.my_board.grid[r][c] == '@'
                    self.my_board.grid[r][c] = 'X' if hit else 'O'
                    self.send({'type': 'result', 'cell': (r, c), 'hit': hit})
                    self.my_turn = True
                elif msg['type'] == 'result':
                    # Update enemy board with result of our attack
                    r, c = msg['cell']
                    self.enemy_board.grid[r][c] = 'X' if msg['hit'] else 'O'
                elif msg['type'] == 'ready':
                    self.enemy_placed = True  # Opponent is ready
            except Exception as e:
                print("[RECEIVE ERROR]", e)
                break

    def run(self):
        # Start the game loop and receiving thread
        threading.Thread(target=self.receive, daemon=True).start()
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            self.draw()
        self.conn.close()  # Close connection on quit
