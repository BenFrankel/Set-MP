import pygame

import const
from app import config
from app.ui import *
from setgame.layout import GameHandler


pygame.init()
text.load_fonts()
image.load_images()

main_window = window.Window((const.window_w, const.window_h))
main_window.background.fill(const.window_bgcolor)
main_window.style_add(config.default_style)
# Add default_controls.
# Add default_options.

main_hub = switch.Hub(*main_window.size)
main_window.register(main_hub)

main_menu = menu.Menu(*main_hub.size)
main_hub.register_center(main_menu)
main_menu.add_button('Single Player', 'setgame-sp')
main_menu.add_button('Multiplayer', 'setgame-mp')
main_menu.add_button('Quit', 'exit')

game = GameHandler(*main_hub.size)
main_hub.register_node('setgame-sp', game)

fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        elif event.type == pygame.KEYDOWN:  # TODO: Handle this in Window controls.
            if event.key == pygame.K_ESCAPE:
                exit()

        main_window.handle_event(event)

    main_window.tick()

    fps_clock.tick()

    # print(fps_clock.get_fps())
