import os.path

import pygame.freetype

import const
from . import base


pygame.freetype.init()


font_dict = dict()


def load_font(filename):
    return pygame.freetype.Font(os.path.join(const.dir_font, filename))


def load_fonts():
    for font_inf in const.fonts:
        try:
            font = load_font(font_inf[1])
        except FileNotFoundError:
            print('Unable to load font:', font_inf)
            exit()
        else:
            font_dict[font_inf[0]] = font


def get_font(name):
    return font_dict[name]


class Text(base.Entity):
    def __init__(self, text='', fontsize=1, fgcolor=None, font=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._text = text
        self._font = font
        self._fontsize = fontsize
        if font is None:
            self._font = get_font(const.font_default)
        self.fgcolor = fgcolor
        if fgcolor is None:
            self.fgcolor = (0, 0, 0)
        self.update_background()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, other):
        if self._text != other:
            self._text = other
            self.update_background()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, other):
        if self._font != other:
            self._font = other
            self.update_background()

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, other):
        if self._fontsize != other:
            self._fontsize = other
            self.update_background()

    def update_background(self):
        self.background = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]
