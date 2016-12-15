import pygame
import pygame.gfxdraw


class SetGameStyle:
    def __init__(self, blank_card, sym_shape, sym_texture, sym_color):
        self.blank_card = blank_card
        self.sym_shape = sym_shape
        self.sym_texture = sym_texture
        self.sym_color = sym_color

    def card_image(self, size, number, color, texture, shape, selected=False):
        card_image = self.blank_card(size, selected)
        rect = card_image.get_rect()

        number += 1

        sym_w = int(rect.w * 0.75)
        sym_h = int(rect.h * 0.2)

        sym_x = (rect.w - sym_w) // 2

        y_gap = int(rect.h / 4 - sym_h)
        total_h = number * (sym_h + y_gap) - y_gap

        sym_y = (rect.h - total_h)//2

        for _ in range(number):
            card_image.blit(self.sym_image((sym_w, sym_h), color, texture, shape), (sym_x, sym_y))
            sym_y += sym_h + y_gap

        return card_image

    def sym_image(self, size, color, texture, shape):
        black = (0, 0, 0)

        sym_color = pygame.Surface(size, pygame.SRCALPHA)
        sym_color.fill(self.sym_color(color))
        sym_texture = self.sym_texture(size, texture)
        sym_outline, sym_mask = self.sym_shape(size, shape)

        surf = pygame.Surface(size, pygame.SRCALPHA)

        sym_outline.blit(sym_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(sym_outline, (0, 0))

        sym_mask.blit(sym_texture, (0, 0), None, pygame.BLEND_MULT)
        sym_mask.set_colorkey(black)
        sym_mask.blit(sym_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(sym_mask, (0, 0))

        return surf

    def bg_deck_image(self, size):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, 15))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, *size), 1)
        pygame.draw.rect(surf, (0, 0, 0, 60), (2, 2, size[0]-4, size[1]-4), 3)
        return surf


def def_blank_card(size, selected=False):
    card_image = pygame.Surface(size)

    card_image.fill((245, 245, 245))
    pygame.draw.rect(card_image, (1, 1, 1), card_image.get_rect(), 1)

    if selected:
        shade = pygame.Surface(size, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 40))
        card_image.blit(shade, (0, 0))

    return card_image


def def_sym_color(color):
    return [(240, 0, 0), (0, 180, 0), (100, 0, 160)][color]


def def_sym_texture(size, texture):
    white = (255, 255, 255)

    mask = pygame.Surface(size)
    rect = mask.get_rect()

    def blank_texture():
        pass

    def stripe_texture():
        n = rect.w // 4
        for i in range(1, n+1):
            pygame.draw.line(mask, white, (i * 4 - 1, 0), (i * 4 - 1, rect.h), 1)

    def solid_texture():
        mask.fill(white)

    [blank_texture, stripe_texture, solid_texture][texture]()

    return mask


def def_sym_shape(size, shape):
    white = (255, 255, 255)

    mask = pygame.Surface(size)
    outline = pygame.Surface(size, pygame.SRCALPHA)
    rect = mask.get_rect()

    def oval_outline():
        pygame.gfxdraw.aaellipse(outline, *rect.center, rect.w//2 - 1, rect.h//2 - 1, white)

    def diamond_outline():
        pointlist = rect.midleft, (rect.w//2, rect.h - 1), rect.midright, rect.midtop
        pygame.gfxdraw.aapolygon(outline, pointlist, white)

    def tilde_outline():
        pygame.gfxdraw.rectangle(outline, rect, white)

    [oval_outline, diamond_outline, tilde_outline][shape]()

    def oval_mask():
        pygame.gfxdraw.filled_ellipse(mask, *rect.center, *rect.center, white)

    def diamond_mask():
        pointlist = rect.midleft, rect.midbottom, rect.midright, rect.midtop
        pygame.gfxdraw.filled_polygon(mask, pointlist, white)

    def tilde_mask():
        mask.fill(white)

    [oval_mask, diamond_mask, tilde_mask][shape]()

    return outline, mask


default = SetGameStyle(def_blank_card, def_sym_shape, def_sym_texture, def_sym_color)
