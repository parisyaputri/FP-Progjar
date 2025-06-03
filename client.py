import socket            # TCP
import pygame
from game import BattleshipGame

SERVER = '127.0.0.1'
PORT = 5555

def main():
    pygame.init()        # Initialize Pygame
    screen = pygame.display.set_mode((1000, 600))  # Create game window
    pygame.display.set_caption("Battleship Client")  # Set window title

    # Set up TCP socket connection to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))  # Connect to game server
    print("Connected to server")

    # Initialize the Battleship game instance (as client)
    game = BattleshipGame(screen, is_host=False, conn=s)
    game.run()           # Start the game loop

    pygame.quit()        # Quit Pygame when done

# Start the main function if script is run directly
if __name__ == '__main__':
    main()
