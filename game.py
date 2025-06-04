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

        self.my_board = Board(100, 100)
        self.enemy_board = Board(600, 100)

        self.conn = conn
        self.is_host = is_host
        self.my_turn = is_host
        self.placed = False
        self.enemy_placed = False
        self.win_status = None

        self.ships_to_place = [(5, True), (4, True), (3, True)]
        self.current_orientation = True

        self.orientation_button = pygame.Rect(100, 30, 200, 40)
        self.play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 40)
        self.exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40)

    def reset_game(self):
        self.__init__(self.screen, self.is_host, self.conn)

    def check_win(self, board):
        for row in board.grid:
            if '@' in row:
                return False
        return True

    def draw_orientation_button(self):
        pygame.draw.rect(self.screen, (0, 100, 200), self.orientation_button)
        text = self.font.render("Orientation: " + ("Horizontal" if self.current_orientation else "Vertical"), True, (255, 255, 255))
        self.screen.blit(text, (110, 38))

    def draw_end_buttons(self):
        pygame.draw.rect(self.screen, (0, 200, 100), self.play_again_button)
        pygame.draw.rect(self.screen, (200, 0, 0), self.exit_button)
        play_text = self.font.render("Play Again", True, (255, 255, 255))
        exit_text = self.font.render("Exit Game", True, (255, 255, 255))
        self.screen.blit(play_text, (self.play_again_button.x + 50, self.play_again_button.y + 8))
        self.screen.blit(exit_text, (self.exit_button.x + 60, self.exit_button.y + 8))

    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.win_status:
            msg = self.font.render("You Won!" if self.win_status == 'win' else "You Lose!", True, (0, 255, 0) if self.win_status == 'win' else (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 60))
            self.draw_end_buttons()
        elif not self.placed:
            self.my_board.draw(self.screen, "Place Your Ships", self.font)
            self.draw_orientation_button()
        elif not self.enemy_placed:
            msg = self.font.render("Waiting for opponent to place ships...", True, (255, 255, 255))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        else:
            self.my_board.draw(self.screen, "Your Board", self.font)
            self.enemy_board.draw(self.screen, "Enemy Board", self.font)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.win_status:
            if self.play_again_button.collidepoint(pos):
                self.reset_game()
                return
            elif self.exit_button.collidepoint(pos):
                self.running = False
                return

        if not self.placed:
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
            cell = self.enemy_board.get_cell(pos)
            if cell:
                r, c = cell
                if self.enemy_board.grid[r][c] in ['X', 'O']:
                    return
                self.send({'type': 'attack', 'cell': cell})
                self.my_turn = False

    def send(self, data):
        try:
            self.conn.sendall(pickle.dumps(data))
        except Exception as e:
            print("[SEND ERROR]", e)

    def receive(self):
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                msg = pickle.loads(data)
                if msg['type'] == 'attack':
                    r, c = msg['cell']
                    hit = self.my_board.grid[r][c] == '@'
                    self.my_board.grid[r][c] = 'X' if hit else 'O'
                    if self.check_win(self.my_board):
                        self.send({'type': 'game_over'})
                        self.win_status = 'lose'
                    else:
                        self.send({'type': 'result', 'cell': (r, c), 'hit': hit})
                        self.my_turn = True
                elif msg['type'] == 'result':
                    r, c = msg['cell']
                    self.enemy_board.grid[r][c] = 'X' if msg['hit'] else 'O'
                elif msg['type'] == 'ready':
                    self.enemy_placed = True
                elif msg['type'] == 'game_over':
                    self.win_status = 'win'
            except Exception as e:
                print("[RECEIVE ERROR]", e)
                break

    def run(self):
        threading.Thread(target=self.receive, daemon=True).start()
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            self.draw()
        self.conn.close()
