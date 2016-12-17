import pygame

import setgame_gui
import gui
import const
import font_loader


pygame.init()
font_loader.load()

screen = gui.Screen((const.screen_width, const.screen_height))
screen.bg_color = const.screen_bg_color
screen.register(setgame_gui.GameEntity(screen))

fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        screen.handle(event)

    screen.tick()

    fps_clock.tick(60)

