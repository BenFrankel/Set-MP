import pygame

from setgame import launcher


pygame.init()
pygame.mixer.quit()

launcher.load()
launcher.spawn_app().launch(fps=60, debug=True)
