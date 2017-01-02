import pygame

import const
import font_loader
from setgame.layout import GameEntity
from ui import *

pygame.init()
font_loader.load()

screen = layout.Screen((const.screen_width, const.screen_height))
screen.background = pygame.Surface(screen.size)
screen.background.fill(const.screen_bg_color)
screen.style_add(default_style.default)

main_hub = layout.Hub(*screen.size)

main_menu = menu.Menu(*screen.size)
main_menu.add_button('Single Player', 'setgame sp')
main_menu.add_button('Multiplayer', 'setgame mp')
main_menu.add_button('Quit', 'exit')
main_hub.register_center(main_menu)

game = GameEntity(*screen.size)
main_hub.register_node('setgame sp', game)

screen.register(main_hub)

fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        screen.handle_event(event)

    screen.tick()

    fps_clock.tick(60)

    print(fps_clock.get_fps())

