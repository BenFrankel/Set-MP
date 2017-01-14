import os.path

import pygame

import const
from . import base


image_dict = dict()


def load_image(filename):
    return pygame.image.load(os.path.join(const.dir_font, filename))


def load_images():
    for image_inf in const.images:
        try:
            image = load_image(image_inf[1])
        except FileNotFoundError:
            print('Unable to load font:', image_inf)
            exit()
        else:
            image_dict[image_inf[0]] = image


def get_font(name):
    return image_dict[name]


class Image(base.Entity):
    def __init__(self, filename=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._image = None
        if filename is not None:
            self.load(filename)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, other):
        self.image = other
        self.background = self.image

    def load(self, filename):
        try:
            self.image = pygame.image.load(filename).convert_alpha()
        except FileNotFoundError:
            print('Unable to load image:', filename)
            exit()
