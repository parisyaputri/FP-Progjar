import socket
import pygame
from game import BattleshipGame

# Server settings
HOST = '0.0.0.0'   # Listen on all available network interfaces
PORT = 5555        # Port to listen on

def main():
    # Initialize Pygame window
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Battleship Server")

    # Create TCP socket and listen for connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)  # Allow only 1 client
    print("Waiting for connection...")

    # Accept connection from client
    conn, addr = s.accept()
    print("Client connected from", addr)

    # Start the Battleship game (server is the host)
    game = BattleshipGame(screen, is_host=True, conn=conn)
    game.run()

    # Clean up on exit
    pygame.quit()

if __name__ == '__main__':
    main()
