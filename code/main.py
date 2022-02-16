import pygame, sys
from settings import *
from level import Level


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        # Set window title
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()

        self.level = Level()

        # sound
        main_sound = pygame.mixer.Sound("../audio/main.ogg")
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)

    def run(self):
        while True:  # event loop: Are we closing the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        # pauses game and display menu
                        self.level.toggle_menu()
            # Fill screen
            self.screen.fill(WATER_COLOR)
            self.level.run()
            # Updating the screen
            pygame.display.update()
            # Controlling the framerate
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
