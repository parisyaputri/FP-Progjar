import pygame
import threading
import pickle
from board import Board

# Game window dimensions and frame rate
WIDTH, HEIGHT = 1000, 600
FPS = 30

class BattleshipGame:
    def __init__(self, screen, is_host, conn):
        # Initialize game state and variables
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 32)
        self.conn = conn              # Connection socket
        self.is_host = is_host        # True = server, False = client
        self.reset_game()

    def reset_game(self):
        # Reset or initialize game state
        self.my_board = Board(100, 100)              # Player's board
        self.enemy_board = Board(600, 100)           # Opponent's board
        self.my_turn = self.is_host                  # Host starts first
        self.placed = False                          # Has player placed all ships?
        self.enemy_placed = False                    # Has enemy placed all ships?
        self.win_status = None                       # 'win' or 'lose'
        self.ships_to_place = [(5, True), (4, True), (3, True)]  # Ship sizes
        self.current_orientation = True              # True = horizontal
        # UI buttons
        self.orientation_button = pygame.Rect(100, 30, 200, 40)
        self.play_again_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 40)
        self.exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 40)

    def check_win(self, board):
        # Check if there are any ships left on the given board
        for row in board.grid:
            if '@' in row:
                return False
        return True

    def draw_orientation_button(self):
        # Draw button to toggle ship orientation
        pygame.draw.rect(self.screen, (0, 100, 200), self.orientation_button)
        text = self.font.render("Orientation: " + ("Horizontal" if self.current_orientation else "Vertical"), True, (255, 255, 255))
        self.screen.blit(text, (110, 38))

    def draw_legend(self):
        # Draw legend explaining colors (hit, miss)
        legend = [
            ("Miss (Blue)", (0, 0, 255)),
            ("Hit (Red)", (255, 0, 0))
        ]
        base_y = 520
        for i, (label, color) in enumerate(legend):
            pygame.draw.circle(self.screen, color, (100, base_y + i * 25), 8)
            text = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text, (120, base_y - 10 + i * 25))

    def draw_end_buttons(self):
        # Draw "Play Again" and "Exit Game" buttons after game over
        pygame.draw.rect(self.screen, (0, 180, 0), self.play_again_button)
        pygame.draw.rect(self.screen, (180, 0, 0), self.exit_button)
        play_text = self.font.render("Play Again", True, (255, 255, 255))
        exit_text = self.font.render("Exit Game", True, (255, 255, 255))
        self.screen.blit(play_text, (self.play_again_button.x + 40, self.play_again_button.y + 8))
        self.screen.blit(exit_text, (self.exit_button.x + 50, self.exit_button.y + 8))

    def draw(self):
        # Main draw function - updates entire screen
        self.screen.fill((0, 0, 0))  # Clear screen with black
        if self.win_status:
            # Game over screen
            msg = self.font.render("You Won!" if self.win_status == 'win' else "You Lose!", True, (0, 255, 0) if self.win_status == 'win' else (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
            self.draw_end_buttons()
        elif not self.placed:
            # Ship placement phase
            self.my_board.draw(self.screen, "Place Your Ships", self.font)
            self.draw_orientation_button()
        elif not self.enemy_placed:
            # Waiting for opponent to finish placing ships
            msg = self.font.render("Waiting for opponent to place ships...", True, (255, 255, 255))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        else:
            # Main gameplay screen
            self.my_board.draw(self.screen, "Your Board", self.font)
            self.enemy_board.draw(self.screen, "Enemy Board", self.font)

        self.draw_legend()
        pygame.display.flip()  # Update display

    def handle_click(self, pos):
        # Handle mouse clicks
        if self.win_status:
            # If game over, handle button clicks
            if self.play_again_button.collidepoint(pos):
                self.send({'type': 'reset'})
                self.reset_game()
            elif self.exit_button.collidepoint(pos):
                self.running = False
            return

        if not self.placed:
            # During ship placement
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
                    self.send({'type': 'ready'})
        elif self.my_turn and self.enemy_placed:
            # During attack phase
            cell = self.enemy_board.get_cell(pos)
            if cell:
                r, c = cell
                if self.enemy_board.grid[r][c] in ['X', 'O']:
                    return  # Already attacked this cell
                self.send({'type': 'attack', 'cell': cell})
                self.my_turn = False

    def send(self, data):
        # Send data to opponent
        try:
            self.conn.sendall(pickle.dumps(data))
        except Exception as e:
            print("[SEND ERROR]", e)

    def receive(self):
        # Threaded function to receive messages from opponent
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                msg = pickle.loads(data)

                # Process received message
                if msg['type'] == 'attack':
                    r, c = msg['cell']
                    hit = self.my_board.grid[r][c] == '@'
                    self.my_board.grid[r][c] = 'X' if hit else 'O'
                    if self.check_win(self.my_board):
                        # If player loses
                        self.send({'type': 'game_over'})
                        self.win_status = 'lose'
                    else:
                        self.send({'type': 'result', 'cell': (r, c), 'hit': hit})
                        self.my_turn = True
                elif msg['type'] == 'result':
                    # Update enemy board with attack result
                    r, c = msg['cell']
                    self.enemy_board.grid[r][c] = 'X' if msg['hit'] else 'O'
                elif msg['type'] == 'ready':
                    # Opponent finished ship placement
                    self.enemy_placed = True
                elif msg['type'] == 'game_over':
                    # Player wins
                    self.win_status = 'win'
                elif msg['type'] == 'reset':
                    # Opponent requested game reset
                    self.reset_game()
            except Exception as e:
                print("[RECEIVE ERROR]", e)
                break

    def run(self):
        # Main game loop
        threading.Thread(target=self.receive, daemon=True).start()
        while self.running:
            self.clock.tick(FPS)  # Limit FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            self.draw()
        # Clean up when exiting
        self.conn.close()
