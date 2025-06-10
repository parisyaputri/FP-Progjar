import socket
import pygame
from game import BattleshipGame

# Server address and port
SERVER = '127.0.0.1'
PORT = 5555

def main():
    # Initialize Pygame and create the window
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Battleship Client")

    # Create TCP socket and connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))
    print("Connected to server")

    # Create BattleshipGame instance for client player
    game = BattleshipGame(screen, is_host=False, conn=s)

    # Run the game loop
    game.run()

    # Quit Pygame when done
    pygame.quit()

# Run main() when script is executed directly
if __name__ == '__main__':
    main()
