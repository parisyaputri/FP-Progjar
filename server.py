import socket
import pygame
from game import BattleshipGame

HOST = '0.0.0.0'
PORT = 5555

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Battleship Server")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print("Waiting for connection...")

    conn, addr = s.accept()
    print("Client connected from", addr)

    game = BattleshipGame(screen, is_host=True, conn=conn)
    game.run()

    pygame.quit()

if __name__ == '__main__':
    main()
