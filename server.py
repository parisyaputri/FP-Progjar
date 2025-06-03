import socket
import pygame
from game import BattleshipGame

HOST = '0.0.0.0'
PORT = 5555

def main():
    pygame.init()       # Initialize Pygame
    screen = pygame.display.set_mode((1000, 600))  # Create game window
    pygame.display.set_caption("Battleship Server")  # Set window title

    # Create TCP socket and bind to specified host and port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)          # Listen for a single connection
    print("Waiting for connection...")

    # Accept an incoming client connection
    conn, addr = s.accept()
    print("Client connected from", addr)

    # Start the Battleship game (this instance is the host)
    game = BattleshipGame(screen, is_host=True, conn=conn)
    game.run()           # Run the game loop
    pygame.quit()        # Quit Pygame on exit

# Only run main() if this file is executed directly
if __name__ == '__main__':
    main()
