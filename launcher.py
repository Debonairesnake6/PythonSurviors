import pygame
from game_loop import Game
from scripts.pygame_utils import configure_icecream


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    configure_icecream()

    while True:
        game = Game()
        game.run()
