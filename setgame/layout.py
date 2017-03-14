import pygame

from app import gui
from setgame.model import Game


class CardEntity(gui.Widget):
    def __init__(self, card, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.name = 'card'

        self.card_model = card
        self.card_model.add_observer(self)

    def notify(self, subject, diff):
        if subject == self.card_model and (diff.selected or diff.face_up):
            self.reload()

    def widget_state_change(self, before, after):
        if before == gui.WidgetState.HOVER and after == gui.WidgetState.PRESS and self.card_model.face_up:
            self.card_model.toggle_select()

    def reload(self):
        self.background = self.style_get('card')(self.size,
                                                 *self.card_model.values,
                                                 face_up=self.card_model.face_up,
                                                 selected=self.card_model.selected)


class PlayDeckEntity(gui.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'play-deck'

        self.deck_model = deck
        deck.add_observer(self)
        for card in deck.cards:
            card.add_observer(self)

        card_w = self.w // 5
        card_h = self.h // 3.5
        self.cards = [CardEntity(card, card_w, card_h) for card in deck.cards]
        self.register_all(self.cards)

    @property
    def dim(self):
        num_in_play = len(self.deck_model.play_deck)
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
        if subject == self.deck_model and diff.play_deck or subject in self.deck_model.play_deck and diff.selected:
            rows, cols = self.dim
            card_w, card_h = self.card_size
            half_gap_w = (self.w - (self.w // cols) * (cols - 1) - card_w) // 2
            half_gap_h = (self.h - (self.h // rows) * (rows - 1) - card_h) // 2
            for card in self.cards:
                if card.card_model.in_play():
                    card.resize((card_w, card_h))
                    card.x = half_gap_w + (self.w // cols) * (card.card_model.index % cols)
                    card.y = half_gap_h + (self.h // rows) * (card.card_model.index // cols)
                    if card.card_model.selected:
                        card.y -= half_gap_h // 2
                    if not card.is_alive:
                        card.show()
                elif card.is_alive:
                    card.hide()

    def reload(self):
        self.background = self.style_get('bg')(self.size)


class DrawDeckEntity(gui.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.name = 'draw-deck'

        self.deck = deck
        deck.add_observer(self)

    @property
    def num_cards(self):
        return len(self.deck.draw_deck)

    def notify(self, subject, diff):
        if subject == self.deck and diff.draw_deck:
            self.reload()

    def reload(self):
        self.background = self.style_get('draw-deck')(self.size, self.num_cards)


class DiscardDeckEntity(gui.Entity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.name = 'discard-deck'

        self.deck = deck
        deck.add_observer(self)

        self._top_card = None

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
            self.reload()

    def reload(self):
        self.background = self.style_get('discard-deck')(self.size, self.num_cards, self.top_card)


class ClockEntity(gui.Entity):
    def __init__(self, game_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'clock'

        self.game_model = game_model
        self.clock = game_model.clock
        game_model.add_observer(self)

        text_h = int(self.h * 0.9)
        self.e_text = gui.Text(fontsize=text_h)
        self.register(self.e_text)

    def pause(self):
        self.clock.pause()
        super().pause()

    def unpause(self):
        self.clock.unpause()
        super().unpause()

    def notify(self, subject, diff):
        if subject == self.game_model and diff.time:
            self.e_text.text = '{:d}:{:02d}'.format(self.clock.time.m, self.clock.time.s)
            if self.clock.time.h >= 1:
                self.e_text.font = self.style_get('font')  # TODO: Use default font
                self.e_text.text = 'Zzz..'
            self.e_text.center = self.rel_rect().center

    def reload(self):  # TODO: Text appears misplaced at 0:00
        self.background = self.style_get('bg')(self.size)
        self.e_text.font = self.style_get('font')


class SPGameEntity(gui.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = Game()
        self.model.add_observer(self)

        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.play_deck = PlayDeckEntity(self.model.deck, deck_w, deck_h)
        self.play_deck.x = (self.w - deck_w) // 2
        self.play_deck.y = (self.h - deck_h) // 3
        self.register(self.play_deck)

        card_w = self.play_deck.w // 5
        card_h = self.play_deck.h // 3.5
        card_deck_w = int(card_w * 1.3)
        card_deck_h = int(card_h * 1.3)
        self.draw_deck = DrawDeckEntity(self.model.deck, card_deck_w, card_deck_h)
        self.draw_deck.x = (self.w + self.play_deck.right - card_deck_w) // 2
        self.draw_deck.y = self.play_deck.midy
        self.register(self.draw_deck)

        self.discard_deck = DiscardDeckEntity(self.model.deck, card_deck_w, card_deck_h)
        self.discard_deck.x = (self.play_deck.left - card_deck_w) // 2
        self.discard_deck.y = self.play_deck.midy
        self.register(self.discard_deck)

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.play_deck.y * 0.8)
        self.clock = ClockEntity(self.model, clock_w, clock_h)
        self.clock.x = (self.w - clock_w) // 2
        self.clock.y = (self.play_deck.y - clock_h) // 2
        self.register(self.clock)

    def notify(self, subject, diff):
        if subject == self.model and diff.completed:
            pass  # TODO: Handle win conditions here

    def pause(self):
        if not self.model.completed:
            self.model.clock.pause()
        super().pause()

    def unpause(self):
        if not self.model.completed:
            self.model.clock.unpause()
        super().unpause()

    def update(self):
        self.model.tick()


class GameHandler(gui.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, typable=True, opacity=0, **kwargs)
        self.category = 'setgame'

        self.game = SPGameEntity(*args)
        self.register(self.game)

        button_w = 100
        button_h = 50
        button_gap = 3 * button_w // 2
        button_x = self.w // 2 - 2 * button_w
        button_y = (self.game.play_deck.bottom + self.h - button_h) // 2
        self.exit_button = gui.Button('Exit', 'exit', button_w, button_h)
        self.exit_button.pos = (button_x, button_y)
        self.register(self.exit_button)

        button_x += button_gap
        self.pause_button = gui.Button('Pause', 'toggle-pause', button_w, button_h)
        self.pause_button.pos = (button_x, button_y)
        self.register(self.pause_button)

        button_x += button_gap
        self.restart_button = gui.Button('Restart', 'restart', button_w, button_h)
        self.restart_button.pos = (button_x, button_y)
        self.register(self.restart_button)

        self.completed_games = []

    def handle_message(self, sender, message):
        if message == 'exit':
            self.handle_message(sender, 'pause')
        if message == 'restart':
            self.game.model.restart()
            self.handle_message(sender, 'unpause')
        elif message == 'toggle-pause':
            if self.game.model.paused:
                self.handle_message(sender, 'unpause')
            else:
                self.handle_message(sender, 'pause')
        elif message == 'pause':
            self.game.model.pause()
            self.pause_button.label_name = 'Unpause'
        elif message == 'unpause':
            self.game.model.unpause()
            self.pause_button.label_name = 'Pause'
        else:
            super().handle_message(sender, message)

    def show(self):
        if not self.game.model.started:
            self.game.model.start()
        super().show()
