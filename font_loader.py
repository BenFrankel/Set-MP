import os.path

import pygame.freetype

import const


pygame.freetype.init()


font_dict = dict()


def load_font(filename):
    return pygame.freetype.Font(os.path.join(const.dir_font, filename))


def load():
    for font_inf in const.fonts:
        try:
            font = load_font(font_inf[1])
        except FileNotFoundError:
            print('Unable to load font:', font_inf)
        else:
            font_dict[font_inf[0]] = font


def get(name):
    return font_dict[name]
