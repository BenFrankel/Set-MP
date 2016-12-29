import pygame

import const


def style(button):
    return {const.style_button: button}


def def_button(size, state):
    surf = pygame.Surface(size)

    shade = [0, 40, 40, 60, 60][state.value]

    surf.fill((shade, shade, shade))
    surf.set_alpha(100)

    return surf


default = style(def_button)
