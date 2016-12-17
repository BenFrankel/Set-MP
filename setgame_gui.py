import gui
import setgame_logic
import setgame_style
import font_loader
import const


class CardEntity(gui.StyledEntity):
    def __init__(self, card, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = card
        self.current_state = None

    def mouse_up(self, pos, button):
        self.card.toggle_select()
        super().mouse_up(pos, button)

    def pre_draw(self):
        if self.current_state != (self.size, self.card.selected):
            self.current_state = self.size, self.card.selected
            self.surf = self.style_draw(const.style_card, self.size, *self.card.values, self.card.selected)


class DeckEntity(gui.StyledEntity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck = deck
        e_card_w = int(self.w / 5)
        e_card_h = int(self.h / 3.5)
        self.e_cards = [CardEntity(card, (0, 0, e_card_w, e_card_h)) for card in self.deck.cards]
        self.register_all(self.e_cards)

    def update(self):
        num_in_play = len(self.deck.play_deck)
        rows = 3
        cols = max((num_in_play + 2) // rows, 1)
        if num_in_play <= 6:
            rows = max(num_in_play // 3, 1)
            cols = 3
        e_card_w = min(int(self.w / (cols + 1)), int(self.w / 5))
        e_card_h = min(int(self.h / (rows + 0.5)), int(self.h / 3.5))
        half_gap_w = (self.w - (self.w // cols) * (cols - 1) - e_card_w)//2
        half_gap_h = (self.h - (self.h // rows) * (rows - 1) - e_card_h)//2
        for e_card in self.e_cards:
            if e_card.card.in_play():
                e_card.size = (e_card_w, e_card_h)
                e_card.x = half_gap_w + (self.w // cols) * (e_card.card.index % cols)
                e_card.y = half_gap_h + (self.h // rows) * (e_card.card.index // cols)
                if e_card.card.selected:
                    e_card.y -= half_gap_h//2
                e_card.show()
            else:
                e_card.hide()
        super().update()

    def pre_draw(self):
        self.surf = self.style_draw(const.style_deck_bg, self.size)


class ClockEntity(gui.StyledEntity):
    def __init__(self, clock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clock = clock
        text_h = int(self.h * 0.9)
        self.e_text = gui.Text(text_h, font=font_loader.get(const.font_digital_clock))
        self.register(self.e_text)

    def update(self):
        self.e_text.text = '{:d}:{:02d}'.format(self.clock.time.m, self.clock.time.s)
        if self.clock.time.h >= 1:
            self.e_text.font = font_loader.get(const.font_default)
            self.e_text.text = 'Zzz..'
        self.e_text.x = (self.w - self.e_text.w) // 2
        self.e_text.y = (self.h - self.e_text.h) // 2

    def pre_draw(self):
        self.surf = self.style_draw(const.style_clock_bg, self.size)


class DrawDeckEntity(gui.StyledEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_cards = 81

    def pre_draw(self):
        self.surf = self.style_draw(const.style_draw_deck, self.size, self.num_cards)


class DiscardDeckEntity(gui.StyledEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_cards = 0
        self.top_card = None

    def pre_draw(self):
        self.surf = self.style_draw(const.style_discard_deck, self.size, self.num_cards, self.top_card)


class GameEntity(gui.StyledEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = setgame_logic.Game()
        self.add_style(setgame_style.default)

        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.e_deck = DeckEntity(self.game.deck, (self.w - deck_w)//2, (self.h - deck_h)//3, deck_w, deck_h)
        self.register(self.e_deck)

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.e_deck.y * 0.8)
        self.e_clock = ClockEntity(self.game.clock, (self.w - clock_w)//2, (self.e_deck.y - clock_h)//2, clock_w, clock_h)
        self.register(self.e_clock)

        card_w = int(self.e_deck.w / 5)
        card_h = int(self.e_deck.h / 3.5)
        card_deck_w = int(card_w * 1.3)
        card_deck_h = int(card_h * 1.3)
        draw_deck_x = (self.w + self.e_deck.right - card_deck_w)//2
        draw_deck_y = self.e_deck.centery
        self.e_draw_deck = DrawDeckEntity(draw_deck_x, draw_deck_y, card_deck_w, card_deck_h)
        self.register(self.e_draw_deck)

        disc_deck_x = (self.e_deck.left - card_deck_w)//2
        disc_deck_y = self.e_deck.centery
        self.e_discard_deck = DiscardDeckEntity(disc_deck_x, disc_deck_y, card_deck_w, card_deck_h)
        self.register(self.e_discard_deck)

        self.game.start_game()

    def update(self):
        if not self.game.playing:  # TODO: Can handle win conditions here as well.
            pass
        self.game.update()
        self.e_draw_deck.num_cards = len(self.game.deck.draw_deck)
        self.e_discard_deck.num_cards = len(self.game.deck.discard_deck)
        if len(self.game.deck.discard_deck) > 0:
            self.e_discard_deck.top_card = self.game.deck.discard_deck[-1]
        super().update()
