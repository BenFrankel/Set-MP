import pygame
import pygame.gfxdraw


def play_deck_bg(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, 15))

    pygame.draw.rect(surf, (0, 0, 0), (0, 0, *size), 1)
    pygame.draw.rect(surf, (0, 0, 0, 60), (2, 2, size[0]-4, size[1]-4), 3)

    return surf


def clock_bg(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((150, 150, 150, 150))

    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 1)

    return surf


def card_front(size, border=True, selected=False):
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


def card_back(size, border=True):
    surf = pygame.Surface(size)
    rect = surf.get_rect()

    surf.fill((120, 20, 120))
    if border:
        border = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(border, (0, 0, 0, 100), rect, 1)
        surf.blit(border, (0, 0))

    return surf


def symbol_color(color):
    return [(240, 0, 0), (0, 180, 0), (100, 0, 160)][color]


def symbol_texture(size, texture):
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


def symbol_shape(size, shape):
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


def button_bg(size, state):
    surf = pygame.Surface(size)

    shade = [0, 40, 40, 60, 60][state]

    surf.fill((shade, shade, shade))
    surf.set_alpha(100)

    return surf


def text_box_bg(size, margin):
    surf = pygame.Surface(size)

    surf.fill((205, 205, 205))
    pygame.draw.rect(surf, (160, 160, 160), surf.get_bounding_rect(), margin + 1)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_bounding_rect(), 1)
    surf.set_alpha(100)

    return surf


def text_box_cursor_bg(size):
    surf = pygame.Surface(size)
    surf.fill((0, 0, 0))
    return surf


def unknown_bg(size):
    surf = pygame.Surface(size)
    surf.fill((255, 0, 0))
    return surf
