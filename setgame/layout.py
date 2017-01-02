import const
import font_loader
from setgame import default_style
from setgame.model import Game
from ui import layout
from ui.menu import WidgetState, Widget, Button


# TODO: Card cannot detect
class CardEntity(Widget):
    def __init__(self, card, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = card
        self.card.add_observer(self)

    def notify(self, subject, diff):
        if subject == self.card and diff.selected:
            self.update_background()

    def widget_state_change(self, before, after):
        if before == WidgetState.HOVER and after == WidgetState.PRESS:
            self.card.toggle_select()

    def update_background(self):
        try:
            self.background = self.style_get(const.style_card, self.size, *self.card.values, self.card.selected)
        except KeyError:
            super().update_background()


class PlayDeckEntity(layout.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        deck.add_observer(self)
        for card in deck.cards:
            card.add_observer(self)

        e_card_w = self.w // 5
        e_card_h = self.h // 3.5
        self.e_cards = [CardEntity(card, e_card_w, e_card_h) for card in deck.cards]
        self.register_all(self.e_cards)

    @property
    def deck(self):
        return self.parent.game.deck

    @property
    def dim(self):
        num_in_play = len(self.deck.play_deck)
        rows = 3
        cols = max((num_in_play + 2) // rows, 1)
        if num_in_play <= 6:
            rows = max(num_in_play // 3, 1)
            cols = 3
        return rows, cols

    @property
    def card_size(self):
        rows, cols = self.dim
        card_w = min(int(self.w / (cols + 1)), int(self.w / 5))
        card_h = min(int(self.h / (rows + 0.5)), int(self.h / 3.5))
        return card_w, card_h

    def notify(self, subject, diff):
        if subject == self.deck and diff.play_deck or subject in self.deck.play_deck and diff.selected:
            rows, cols = self.dim
            card_w, card_h = self.card_size
            half_gap_w = (self.w - (self.w // cols) * (cols - 1) - card_w) // 2
            half_gap_h = (self.h - (self.h // rows) * (rows - 1) - card_h) // 2
            for e_card in self.e_cards:
                if e_card.card.in_play():
                    e_card.resize((card_w, card_h))
                    e_card.x = half_gap_w + (self.w // cols) * (e_card.card.index % cols)
                    e_card.y = half_gap_h + (self.h // rows) * (e_card.card.index // cols)
                    if e_card.card.selected:
                        e_card.y -= half_gap_h // 2
                    if not e_card.visible:
                        e_card.show()
                elif e_card.visible:
                    e_card.hide()

    def update_background(self):
        try:
            self.background = self.style_get(const.style_deck_bg, self.size)
        except KeyError:
            super().update_background()


class DrawDeckEntity(layout.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        deck.add_observer(self)

    @property
    def deck(self):
        return self.parent.game.deck

    @property
    def num_cards(self):
        return len(self.deck.draw_deck)

    def notify(self, subject, diff):
        if subject == self.deck and diff.draw_deck:
            self.update_background()

    def update_background(self):
        try:
            self.background = self.style_get(const.style_draw_deck, self.size, self.num_cards)
        except KeyError:
            super().update_background()


class DiscardDeckEntity(layout.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        deck.add_observer(self)
        self._top_card = None

    @property
    def deck(self):
        return self.parent.game.deck

    @property
    def top_card(self):
        if self.deck.discard_deck:
            return self.deck.discard_deck[-1]
        return None

    @property
    def num_cards(self):
        return len(self.deck.discard_deck)

    def notify(self, subject, diff):
        if subject == self.deck and diff.discard_deck:
            self.update_background()

    def update_background(self):
        try:
            self.background = self.style_get(const.style_discard_deck, self.size, self.num_cards, self.top_card)
        except KeyError:
            super().update_background()


class ClockEntity(layout.Entity):
    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        game.add_observer(self)

        text_h = int(self.h * 0.9)
        self.e_text = layout.Text(fontsize=text_h, font=font_loader.get(const.font_digital_clock))
        self.register(self.e_text)

    @property
    def clock(self):
        return self.parent.game.clock

    def notify(self, subject, diff):
        if subject == self.parent.game and diff.time:
            self.e_text.text = '{:d}:{:02d}'.format(self.clock.time.m, self.clock.time.s)
            if self.clock.time.h >= 1:
                self.e_text.font = font_loader.get(const.font_default)
                self.e_text.text = 'Zzz..'
            self.e_text.center = self.rel_rect().center

    def update_background(self):
        try:
            self.background = self.style_get(const.style_clock_bg, self.size)
        except KeyError:
            super().update_background()


class GameEntity(layout.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = Game()
        self.game.add_observer(self)

        self.style_add(default_style.default)

        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.e_play_deck = PlayDeckEntity(self.game.deck, deck_w, deck_h)
        self.e_play_deck.x = (self.w - deck_w) // 2
        self.e_play_deck.y = (self.h - deck_h) // 3
        self.register(self.e_play_deck)

        card_w = self.e_play_deck.w // 5
        card_h = self.e_play_deck.h // 3.5
        card_deck_w = int(card_w * 1.3)
        card_deck_h = int(card_h * 1.3)
        self.e_draw_deck = DrawDeckEntity(self.game.deck, card_deck_w, card_deck_h)
        self.e_draw_deck.x = (self.w + self.e_play_deck.right - card_deck_w) // 2
        self.e_draw_deck.y = self.e_play_deck.midy
        self.register(self.e_draw_deck)

        self.e_discard_deck = DiscardDeckEntity(self.game.deck, card_deck_w, card_deck_h)
        self.e_discard_deck.x = (self.e_play_deck.left - card_deck_w) // 2
        self.e_discard_deck.y = self.e_play_deck.midy
        self.register(self.e_discard_deck)

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.e_play_deck.y * 0.8)
        self.e_clock = ClockEntity(self.game, clock_w, clock_h)
        self.e_clock.x = (self.w - clock_w)//2
        self.e_clock.y = (self.e_play_deck.y - clock_h) // 2
        self.register(self.e_clock)

        button_w = 100
        button_h = 50
        button_y = (self.e_play_deck.bottom + self.h - button_h) // 2
        self.restart_button = Button('Restart', 'restart', button_w, button_h)
        self.restart_button.x = (self.w + 2*button_w) // 2
        self.restart_button.y = button_y
        self.register(self.restart_button)

        self.exit_button = Button('Exit', 'exit', button_w, button_h)
        self.exit_button.x = (self.w - 4*button_w)//2
        self.exit_button.y = button_y
        self.register(self.exit_button)

        self.game.start_game()

    def notify(self, subject, diff):
        if subject == self.game and diff.completed:
            pass  # TODO: Can handle win conditions here.

    def pause(self):
        if not self.game.completed:
            self.game.clock.pause()
        super().pause()

    def unpause(self):
        if not self.game.completed:
            self.game.clock.unpause()
        super().unpause()

    def update(self):
        self.game.update()
        super().update()

    def handle_message(self, sender, message):
        if message == 'restart':
            self.game.reset_game()
            self.game.start_game()
        else:
            super().handle_message(sender, message)
