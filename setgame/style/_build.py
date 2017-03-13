import pygame


def compose(config):
    def symbol(size, color, texture, shape):
        black = (0, 0, 0)

        s_color = pygame.Surface(size, pygame.SRCALPHA)
        s_color.fill(config.style_get('symbol-color', 'card', 'setgame')(color))
        s_texture = config.style_get('symbol-texture', 'card', 'setgame')(size, texture)
        s_outline, s_mask = config.style_get('symbol-shape', 'card', 'setgame')(size, shape)

        surf = pygame.Surface(size, pygame.SRCALPHA)

        s_outline.blit(s_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(s_outline, (0, 0))

        s_mask.blit(s_texture, (0, 0), None, pygame.BLEND_MULT)
        s_mask.set_colorkey(black)
        s_mask.blit(s_color, (0, 0), None, pygame.BLEND_MULT)
        surf.blit(s_mask, (0, 0))

        return surf

    def card(size, number, color, texture, shape, border=True, face_up=True, selected=False):
        if not face_up:
            return config.style_get('back', 'card', 'setgame')(size, border)

        card_image = config.style_get('front', 'card', 'setgame')(size, border, selected)
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
        back_img = config.style_get('back', 'card', 'setgame')((card_w, card_h))
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
        front_img = config.style_get('front', 'card', 'setgame')((card_w, card_h))
        for _ in range(layers):
            surf.blit(front_img, (card_x, card_y))
            card_x -= 2
            card_y -= 2
        if top_card is not None:
            surf.blit(card((card_w, card_h), *top_card.values), (card_x + 2, card_y + 2))

        return surf

    config.style_add('card', 'card', 'setgame', card)
    config.style_add('discard-deck', 'discard-deck', 'setgame', discard_deck)
    config.style_add('draw-deck', 'draw-deck', 'setgame', draw_deck)
