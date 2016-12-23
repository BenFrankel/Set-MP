import pygame

import const
import gui
import setgame_gui
import font_loader
import default_style
import menu


pygame.init()
font_loader.load()

screen = gui.Screen(const.screen_width, const.screen_height)
screen.bg_color = const.screen_bg_color
screen.style_add(default_style.default)

main_hub = gui.Hub(*screen.size)

main_menu = menu.Menu(*screen.size)
main_menu.add_button('Single Player', 'setgame sp')
main_menu.add_button('Multiplayer', 'setgame mp')
main_menu.add_button('Quit', 'exit')
main_hub.register_center(main_menu)

setgame = setgame_gui.GameEntity(*screen.size)
main_hub.register_node('setgame sp', setgame)

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

