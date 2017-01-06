import pygame

import const
from setgame.layout import GameHandler
from ui import *

pygame.init()
text.load_fonts()
image.load_images()

main_window = layout.Window((const.window_w, const.window_h))
main_window.background.fill(const.window_bgcolor)
main_window.style_add(default_style.default)

main_hub = layout.Hub(*main_window.size)
main_window.register(main_hub)

main_menu = menu.Menu(*main_hub.size)
main_hub.register_center(main_menu)
main_menu.add_button('Single Player', 'setgame sp')
main_menu.add_button('Multiplayer', 'setgame mp')
main_menu.add_button('Quit', 'exit')

game = GameHandler(*main_hub.size)
main_hub.register_node('setgame sp', game)

fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()

        main_window.handle_event(event)

    main_window.tick()

    fps_clock.tick()

    # print(fps_clock.get_fps())
