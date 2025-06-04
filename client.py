import socket
import pygame
from game import BattleshipGame

SERVER = '127.0.0.1'
PORT = 5555

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

if __name__ == '__main__':
    main()
