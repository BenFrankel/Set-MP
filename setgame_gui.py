import gui
import menu
import setgame_logic
import setgame_style
import font_loader
import const


class CardEntity(menu.Widget):
    def __init__(self, card, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = card

    def state_change(self, before, after):
        if before == menu.Widget.HOVER and after == menu.Widget.PRESS:
            self.card.toggle_select()

    def get_base_state(self):
        return (self.card.selected,) + super().get_base_state()

    def update_base(self):
        try:
            self.base = self.style_get(const.style_card, self.size, *self.card.values, self.card.selected)
        except KeyError:
            pass


class DeckEntity(gui.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck = deck
        e_card_w = self.w // 5
        e_card_h = self.h // 3.5
        self.e_cards = [CardEntity(card, e_card_w, e_card_h) for card in self.deck.cards]
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

    def get_base_state(self):
        return (self.deck,) + super().get_base_state()

    def update_base(self):
        try:
            self.base = self.style_get(const.style_deck_bg, self.size)
        except KeyError:
            pass


class ClockEntity(gui.Entity):
    def __init__(self, clock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clock = clock
        text_h = int(self.h * 0.9)
        self.e_text = gui.Text(fontsize=text_h, font=font_loader.get(const.font_digital_clock))
        self.register(self.e_text)

    def update(self):
        self.e_text.text = '{:d}:{:02d}'.format(self.clock.time.m, self.clock.time.s)
        if self.clock.time.h >= 1:
            self.e_text.font = font_loader.get(const.font_default)
            self.e_text.text = 'Zzz..'
        self.e_text.x = (self.w - self.e_text.w) // 2
        self.e_text.y = (self.h - self.e_text.h) // 2
        super().update()

    def update_base(self):
        try:
            self.base = self.style_get(const.style_clock_bg, self.size)
        except KeyError:
            pass


class DrawDeckEntity(gui.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_cards = 81

    def get_base_state(self):
        return self.num_cards

    def update_base(self):
        try:
            self.base = self.style_get(const.style_draw_deck, self.size, self.num_cards)
        except KeyError:
            pass


class DiscardDeckEntity(gui.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_cards = 0
        self.top_card = None

    def get_base_state(self):
        return (self.num_cards, self.top_card) + super().get_base_state()

    def update_base(self):
        try:
            self.base = self.style_get(const.style_discard_deck, self.size, self.num_cards, self.top_card)
        except KeyError:
            pass

    def update(self):
        if self.num_cards == 0:
            self.top_card = None
        super().update()


class GameEntity(gui.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = setgame_logic.Game()
        self.style_add(setgame_style.default)

        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.e_deck = DeckEntity(self.game.deck, deck_w, deck_h)
        self.e_deck.x = (self.w - deck_w)//2
        self.e_deck.y = (self.h - deck_h)//3
        self.register(self.e_deck)

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.e_deck.y * 0.8)
        self.e_clock = ClockEntity(self.game.clock, clock_w, clock_h)
        self.e_clock.x = (self.w - clock_w)//2
        self.e_clock.y = (self.e_deck.y - clock_h)//2
        self.register(self.e_clock)

        card_w = self.e_deck.w // 5
        card_h = self.e_deck.h // 3.5
        card_deck_w = int(card_w * 1.3)
        card_deck_h = int(card_h * 1.3)
        self.e_draw_deck = DrawDeckEntity(card_deck_w, card_deck_h)
        self.e_draw_deck.x = (self.w + self.e_deck.right - card_deck_w)//2
        self.e_draw_deck.y = self.e_deck.midy
        self.register(self.e_draw_deck)

        self.e_discard_deck = DiscardDeckEntity(card_deck_w, card_deck_h)
        self.e_discard_deck.x = (self.e_deck.left - card_deck_w)//2
        self.e_discard_deck.y = self.e_deck.midy
        self.register(self.e_discard_deck)

        button_w = 100
        button_h = 50
        button_y = (self.e_deck.bottom + self.h - button_h)//2
        self.restart_button = menu.Button('Restart', 'restart', button_w, button_h)
        self.restart_button.x = (self.w + 2*button_w) // 2
        self.restart_button.y = button_y
        self.register(self.restart_button)

        self.exit_button = menu.Button('Exit', 'exit', button_w, button_h)
        self.exit_button.x = (self.w - 4*button_w)//2
        self.exit_button.y = button_y
        self.register(self.exit_button)

        self.game.start_game()

    def pause(self):
        if not self.game.completed:
            self.game.clock.pause()
        super().pause()

    def unpause(self):
        if not self.game.completed:
            self.game.clock.unpause()
        super().unpause()

    def update(self):
        if not self.game.completed:  # TODO: Can handle win conditions here as well.
            pass
        self.game.update()
        self.e_draw_deck.num_cards = len(self.game.deck.draw_deck)
        self.e_discard_deck.num_cards = len(self.game.deck.discard_deck)
        if len(self.game.deck.discard_deck) > 0:
            self.e_discard_deck.top_card = self.game.deck.discard_deck[-1]
        super().update()

    def handle_message(self, sender, message):
        if message == 'restart':
            self.game.reset_game()
            self.game.start_game()
        else:
            super().handle_message(sender, message)
