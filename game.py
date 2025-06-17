import pygame
import threading
import pickle
from board import Board, CELL_SIZE

# --- UI and Game Settings ---
WIDTH, HEIGHT = 1000, 600
FPS = 60
FONT_SIZE = 28
NOTIFICATION_FONT_SIZE = 40
TITLE_FONT_SIZE = 90

# --- Colors ---
WHITE = (255, 255, 255)
BG_COLOR = (20, 30, 50) 
BUTTON_COLOR = (80, 100, 140)
BUTTON_HOVER_COLOR = (110, 130, 170)
VALID_PREVIEW_COLOR = (0, 255, 0)
INVALID_PREVIEW_COLOR = (255, 0, 0)
HIT_COLOR = (255, 60, 30)
SUNK_COLOR = (255, 180, 0)

class BattleshipGame:
    def __init__(self, screen, is_host, conn):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.conn = conn
        self.is_host = is_host
        
        self.font = pygame.font.Font(None, FONT_SIZE + 4)
        self.notification_font = pygame.font.Font(None, NOTIFICATION_FONT_SIZE + 4)
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        
        self.game_state = "title_screen" 
        self.reset_game()

    def reset_game(self):
        self.my_board = Board(50, 100)
        self.enemy_board = Board(530, 100)
        self.my_turn = self.is_host
        self.placed = False
        self.enemy_placed = False
        self.game_over = False
        self.winner = None
        self.ships_to_place = {5: "Aircraft Carrier", 4: "Battleship", 3: "Cruiser"}
        self.current_ship_len = 5
        self.current_orientation_h = True
        self.notification_text = ""
        self.notification_end_time = 0
        
        self.orientation_button = pygame.Rect(50, 30, 220, 40)
        self.play_again_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)
        self.exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50)
    
    def set_notification(self, text, duration_ms=2500, color=WHITE):
        self.notification_text = text
        self.notification_color = color
        self.notification_end_time = pygame.time.get_ticks() + duration_ms

    def check_sunk(self, ship_id):
        for row in self.my_board.grid:
            for cell in row:
                if isinstance(cell, tuple) and cell[0] == ship_id:
                    return False
        return True

    def check_game_over(self):
        for row in self.my_board.grid:
            for cell in row:
                if isinstance(cell, tuple):
                    return False
        return True

    def draw_title_screen(self):
        self.screen.fill(BG_COLOR)
        title_text = self.title_font.render("BATTLESHIP", True, WHITE)
        self.screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        instructions1 = self.font.render("Sink your opponent's fleet before they sink yours.", True, WHITE)
        self.screen.blit(instructions1, instructions1.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        start_text = self.notification_font.render("Click anywhere to Start", True, VALID_PREVIEW_COLOR)
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            self.screen.blit(start_text, start_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 / 3)))
        pygame.display.flip()

    def draw_ui_elements(self):
        if self.game_state == 'placing_ships':
            hovered = self.orientation_button.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR if hovered else BUTTON_COLOR, self.orientation_button, border_radius=8)
            text = self.font.render(f"Rotate (R): {'Horizontal' if self.current_orientation_h else 'Vertical'}", True, WHITE)
            self.screen.blit(text, text.get_rect(center=self.orientation_button.center))

        if self.game_state == 'game_over':
            play_hover = self.play_again_button.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR if play_hover else BUTTON_COLOR, self.play_again_button, border_radius=8)
            play_text = self.font.render("Play Again", True, WHITE)
            self.screen.blit(play_text, play_text.get_rect(center=self.play_again_button.center))
            exit_hover = self.exit_button.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR if exit_hover else BUTTON_COLOR, self.exit_button, border_radius=8)
            exit_text = self.font.render("Exit", True, WHITE)
            self.screen.blit(exit_text, exit_text.get_rect(center=self.exit_button.center))

    def draw_notification(self):
        display_text, color = "", WHITE
        # Timed notifications (HIT, SINK, etc.) have priority
        if self.notification_text and pygame.time.get_ticks() < self.notification_end_time:
            display_text, color = self.notification_text, self.notification_color
        else: # Otherwise, show the default status for the current game state
            if self.game_state == 'game_over':
                display_text = "YOU WON!" if self.winner else "YOU LOSE!"
                color = VALID_PREVIEW_COLOR if self.winner else HIT_COLOR
            elif self.game_state == 'playing':
                display_text = "Your Turn to Attack!" if self.my_turn else "Opponent's Turn"
            elif self.game_state == 'waiting_for_opponent':
                display_text = "Waiting for opponent..."
            elif self.game_state == 'placing_ships' and self.current_ship_len:
                display_text = f"Placing {self.ships_to_place[self.current_ship_len]}"
        
        if display_text:
            text_surface = self.notification_font.render(display_text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, 40))
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (30,40,60), bg_rect, border_radius=10)
            self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(BG_COLOR)
        if self.game_state != 'title_screen':
            self.my_board.draw(self.screen, "Your Board", self.font)
            self.enemy_board.draw(self.screen, "Enemy Board", self.font, show_ships=False)
        if self.game_state == 'placing_ships':
            if self.current_ship_len:
                cell = self.my_board.get_cell(pygame.mouse.get_pos())
                if cell:
                    is_valid = self.my_board.is_valid_placement(cell, self.current_ship_len, self.current_orientation_h)
                    color = VALID_PREVIEW_COLOR if is_valid else INVALID_PREVIEW_COLOR
                    r, c = cell
                    w = CELL_SIZE * self.current_ship_len if self.current_orientation_h else CELL_SIZE
                    h = CELL_SIZE if self.current_orientation_h else CELL_SIZE * self.current_ship_len
                    preview_rect = pygame.Rect(self.my_board.x_offset + c * CELL_SIZE, self.my_board.y_offset + r * CELL_SIZE, w, h)
                    pygame.draw.rect(self.screen, color, preview_rect, 3)

        self.draw_ui_elements()
        self.draw_notification()
        pygame.display.flip()

    def handle_click(self, pos):
        if self.game_state == "title_screen":
            self.reset_game()
            self.game_state = "placing_ships"
            return

        if self.game_state == 'game_over':
            if self.play_again_button.collidepoint(pos):
                self.send({'type': 'reset'})
                self.reset_game()
                self.game_state = 'placing_ships'
            elif self.exit_button.collidepoint(pos):
                self.running = False
            return

        if self.game_state == 'placing_ships' and self.current_ship_len:
            if self.orientation_button.collidepoint(pos):
                self.current_orientation_h = not self.current_orientation_h
                return
            cell = self.my_board.get_cell(pos)
            if cell and self.my_board.is_valid_placement(cell, self.current_ship_len, self.current_orientation_h):
                self.my_board.place_ship(cell, self.current_ship_len, self.current_orientation_h)
                lengths = sorted(self.ships_to_place.keys(), reverse=True)
                current_index = lengths.index(self.current_ship_len)
                if current_index + 1 < len(lengths):
                    self.current_ship_len = lengths[current_index + 1]
                else: # All ships placed
                    self.current_ship_len = None
                    self.placed = True
                    self.send({'type': 'ready'})
                    if self.enemy_placed: self.game_state = 'playing'
                    else: self.game_state = 'waiting_for_opponent'
        
        elif self.game_state == 'playing' and self.my_turn:
            cell = self.enemy_board.get_cell(pos)
            if cell and self.enemy_board.grid[cell[0]][cell[1]] == '~':
                self.send({'type': 'attack', 'cell': cell})

    def send(self, data):
        try: self.conn.sendall(pickle.dumps(data))
        except Exception as e: print(f"[SEND ERROR] {e}")

    def receive(self):
        while self.running:
            try:
                data = self.conn.recv(4096)
                if not data: break
                msg = pickle.loads(data)

                if msg['type'] == 'attack':
                    r, c = msg['cell']
                    is_hit = isinstance(self.my_board.grid[r][c], tuple)
                    response = {'type': 'result', 'cell': (r, c), 'hit': is_hit}
                    if is_hit:
                        ship_id, ship_len = self.my_board.grid[r][c]
                        self.my_board.grid[r][c] = 'X'
                        if self.check_sunk(ship_id): response['sunk'] = self.ships_to_place[ship_len]
                        if self.check_game_over():
                            self.game_state, self.game_over, self.winner = 'game_over', True, False
                            response['game_over'] = True
                    self.send(response)

                elif msg['type'] == 'result':
                    r, c = msg['cell']
                    if msg['hit']:
                        self.enemy_board.grid[r][c] = 'X'
                        if msg.get('sunk'): self.set_notification(f"You sunk their {msg['sunk']}!", 3000, SUNK_COLOR)
                        else: self.set_notification("It's a HIT! Go again.", 2000, HIT_COLOR)
                        if msg.get('game_over'):
                            self.game_state, self.game_over, self.winner = 'game_over', True, True
                    else:
                        self.enemy_board.grid[r][c] = 'O'
                        self.my_turn = False
                        self.set_notification("It's a MISS. Opponent's turn.", 2000, WHITE)
                        self.send({'type': 'turn_change'})

                elif msg['type'] == 'turn_change':
                    self.my_turn = True
                
                elif msg['type'] == 'ready':
                    self.enemy_placed = True
                    if self.placed: self.game_state = 'playing'
                
                elif msg['type'] == 'reset':
                    self.reset_game()
                    self.game_state = 'placing_ships'

            except (EOFError, ConnectionResetError):
                self.game_state, self.winner = 'game_over', True
                break
            except Exception as e:
                print(f"[RECEIVE ERROR] {e}")
                break

    def run(self):
        threading.Thread(target=self.receive, daemon=True).start()
        while self.running:
            self.clock.tick(FPS)
            
            if self.game_state == "title_screen":
                self.draw_title_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN: self.handle_click(None)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.handle_click(event.pos)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_state == 'placing_ships':
                        self.current_orientation_h = not self.current_orientation_h
                self.draw()
                
        self.conn.close()
        try: pygame.quit()
        except: pass