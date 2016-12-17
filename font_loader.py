import os.path

import pygame.freetype

import const


font_dir = os.path.join('resources', 'data', 'font')
digital_clock = None
default = None


def load_font(filename):
    return pygame.freetype.Font(os.path.join(font_dir, filename))


def load():
    global digital_clock

    try:
        digital_clock = load_font(const.digital_clock)
    except:
        print('Unable to load font:', const.digital_clock)
        exit()

    global default
    default = digital_clock
