import pygame
import pygame.gfxdraw

import const


def style(play_deck_bg, clock_bg, card_front, card_back, sym_shape, sym_texture, sym_color):
    def symbol(size, color, texture, shape):
        black = (0, 0, 0)

        s_color = pygame.Surface(size, pygame.SRCALPHA)
        s_color.fill(sym_color(color))
        s_texture = sym_texture(size, texture)
        s_outline, s_mask = sym_shape(size, shape)

        surf = pygame.Surface(size, pygame.SRCALPHA)

        s_outline.blit(s_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(s_outline, (0, 0))

        s_mask.blit(s_texture, (0, 0), None, pygame.BLEND_MULT)
        s_mask.set_colorkey(black)
        s_mask.blit(s_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(s_mask, (0, 0))

        return surf

    def card(size, number, color, texture, shape, border=True, selected=False):
        card_image = card_front(size, border, selected)
        rect = card_image.get_rect()

        number += 1

        sym_w = int(rect.w * 0.75)
        sym_h = int(rect.h * 0.2)

        sym_x = (rect.w - sym_w) // 2

        y_gap = int(rect.h / 4 - sym_h)
        total_h = number * (sym_h + y_gap) - y_gap

        sym_y = (rect.h - total_h)//2

        for _ in range(number):
            card_image.blit(symbol((sym_w, sym_h), color, texture, shape), (sym_x, sym_y))
            sym_y += sym_h + y_gap

        return card_image

    def draw_deck(size, num_cards):
        card_w = size[0] // 1.3
        card_h = size[1] // 1.3
        layers = (num_cards + 3) // 6

        surf = pygame.Surface(size, pygame.SRCALPHA)
        rect = surf.get_rect()

        card_x = 0
        card_y = rect.h - card_h
        back_img = card_back((card_w, card_h))
        for _ in range(layers):
            surf.blit(back_img, (card_x, card_y))
            card_x += 2
            card_y -= 2

        return surf

    def discard_deck(size, num_cards, top_card):
        card_w = size[0] // 1.3
        card_h = size[1] // 1.3
        layers = (num_cards + 3) // 6

        surf = pygame.Surface(size, pygame.SRCALPHA)
        rect = surf.get_rect()

        card_x = rect.w - card_w - 1
        card_y = rect.h - card_h - 1
        front_img = card_front((card_w, card_h))
        for _ in range(layers):
            surf.blit(front_img, (card_x, card_y))
            card_x -= 2
            card_y -= 2
        if top_card is not None:
            surf.blit(card((card_w, card_h), *top_card.values), (card_x + 2, card_y + 2))

        return surf

    return {const.style_card: card,
            const.style_card_back: card_back,
            const.style_clock_bg: clock_bg,
            const.style_deck_bg: play_deck_bg,
            const.style_discard_deck: discard_deck,
            const.style_draw_deck: draw_deck}


def def_play_deck_bg(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 15))

    pygame.draw.rect(surf, (0, 0, 0), (0, 0, *size), 1)
    pygame.draw.rect(surf, (0, 0, 0, 60), (2, 2, size[0]-4, size[1]-4), 3)

    return surf


def def_clock_bg(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((150, 150, 150, 150))

    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 1)

    return surf


def def_card_front(size, border=True, selected=False):
    surf = pygame.Surface(size)
    rect = surf.get_rect()

    surf.fill((245, 245, 245))

    if selected:
        shade = pygame.Surface(size)
        shade.fill((0, 0, 0))
        shade.set_alpha(40)
        surf.blit(shade, (0, 0))

    if border:
        border = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(border, (0, 0, 0, 100), rect, 1)
        surf.blit(border, (0, 0))

    return surf


def def_card_back(size, border=True):
    surf = pygame.Surface(size)
    rect = surf.get_rect()

    surf.fill((120, 20, 120))
    if border:
        border = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(border, (0, 0, 0, 100), rect, 1)
        surf.blit(border, (0, 0))

    return surf


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


default = style(def_play_deck_bg,
                def_clock_bg,
                def_card_front,
                def_card_back,
                def_sym_shape,
                def_sym_texture,
                def_sym_color)
