from setgame.model import Game

import hgf


class CardEntity(hgf.SimpleWidget):
    def __init__(self, card_model, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.type = 'card'

        self.card_model = card_model
        self._bg_factory = None

    def load_hook(self):
        self.card_model.add_observer(self)

    def load_style_hook(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size,
                                           *self.card_model.values,
                                           face_up=self.card_model.face_up,
                                           selected=self.card_model.selected)

    def notify(self, subject, diff):
        if subject == self.card_model and (diff.selected or diff.face_up):
            self.refresh()

    def mouse_state_change_hook(self, before, after):
        if before == hgf.SimpleWidget.HOVER and after == hgf.SimpleWidget.PRESS and self.card_model.face_up:
            self.card_model.toggle_select()


class PlayDeckEntity(hgf.StructuralComponent):
    def __init__(self, deck_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'play-deck'

        self.deck_model = deck_model
        self.cards = []

        self._bg_factory = None

    def load_hook(self):
        self.deck_model.add_observer(self)
        for card in self.deck_model.cards:
            card.add_observer(self)

        card_w = self.w // 5
        card_h = int(self.h / 3.5)
        self.cards = [CardEntity(card, card_w, card_h) for card in self.deck_model.cards]
        self.register_all(self.cards)

        for card in self.cards:
            card._load()

    def load_style_hook(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size)

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
                        card.y -= half_gap_h
                    if not card.is_visible:
                        card.activate()
                elif card.is_visible:
                    card.deactivate()


class DrawDeckEntity(hgf.StructuralComponent):
    def __init__(self, deck_model, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.type = 'draw-deck'

        self.deck_model = deck_model

        self._bg_factory = None

    def load_hook(self):
        self.deck_model.add_observer(self)

    def load_style_hook(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size, self.num_cards)

    @property
    def num_cards(self):
        return len(self.deck_model.draw_deck)

    def notify(self, subject, diff):
        if subject == self.deck_model and diff.draw_deck:
            self.refresh()


class DiscardDeckEntity(hgf.StructuralComponent):
    def __init__(self, deck_model, *args, **kwargs):
        super().__init__(opacity=2, *args, **kwargs)
        self.type = 'discard-deck'

        self.deck_model = deck_model
        self._top_card = None

        self._bg_factory = None

    def load_hook(self):
        self.deck_model.add_observer(self)

    def load_style_hook(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size, self.num_cards, self.top_card)

    @property
    def top_card(self):
        if self.deck_model.discard_deck:
            return self.deck_model.discard_deck[-1]
        return None

    @property
    def num_cards(self):
        return len(self.deck_model.discard_deck)

    def notify(self, subject, diff):
        if subject == self.deck_model and diff.discard_deck:
            self.refresh()


class ClockEntity(hgf.StructuralComponent):
    def __init__(self, game_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'clock'

        self.game_model = game_model
        self.clock = game_model.clock

        self.e_text = None

        self._bg_factory = None

    def load_hook(self):
        self.game_model.add_observer(self)

        text_h = int(self.h * 0.9)
        self.e_text = hgf.Text(fontsize=text_h)
        self.register(self.e_text)
        self.e_text._load()

    def load_style_hook(self):
        self._bg_factory = self.style_get('background')
        self.e_text.font = self.style_get('font')

    def refresh(self):
        self.background = self._bg_factory(self.size)

    def pause_hook(self):
        self.clock.pause()

    def unpause_hook(self):
        self.clock.unpause()

    def notify(self, subject, diff):
        if subject == self.game_model and diff.time:
            self.e_text.text = '{:d}:{:02d}'.format(self.clock.time.m, self.clock.time.s)
            if self.clock.time.h >= 1:
                self.e_text.font = self.style_get('font')  # TODO: Use default font
                self.e_text.text = 'Zzz..'
            self.e_text.center = self.rel_rect().center


class SPGameEntity(hgf.StructuralComponent):
    def __init__(self, w, h, **kwargs):
        super().__init__(w, h, **kwargs)
        self.model = Game()
        self.play_deck = None
        self.draw_deck = None
        self.discard_deck = None
        self.clock = None

    def load_hook(self):
        self.model.add_observer(self)
        self.model.load()

        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.play_deck = PlayDeckEntity(self.model.deck, deck_w, deck_h)
        self.play_deck.x = (self.w - deck_w) // 2
        self.play_deck.y = (self.h - deck_h) // 3
        self.register(self.play_deck)
        self.play_deck._load()

        card_w = self.play_deck.w // 5
        card_h = self.play_deck.h // 3.5
        card_deck_w = int(card_w * 1.3)
        card_deck_h = int(card_h * 1.3)
        self.draw_deck = DrawDeckEntity(self.model.deck, card_deck_w, card_deck_h)
        self.draw_deck.x = (self.w + self.play_deck.right - card_deck_w) // 2
        self.draw_deck.y = self.play_deck.midy
        self.register(self.draw_deck)
        self.draw_deck._load()

        self.discard_deck = DiscardDeckEntity(self.model.deck, card_deck_w, card_deck_h)
        self.discard_deck.x = (self.play_deck.left - card_deck_w) // 2
        self.discard_deck.y = self.play_deck.midy
        self.register(self.discard_deck)
        self.discard_deck._load()

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.play_deck.y * 0.8)
        self.clock = ClockEntity(self.model, clock_w, clock_h)
        self.clock.x = (self.w - clock_w) // 2
        self.clock.y = (self.play_deck.y - clock_h) // 2
        self.register(self.clock)
        self.clock._load()

    def notify(self, subject, diff):
        if subject == self.model and diff.completed:
            pass  # TODO: Handle win conditions here

    def pause_hook(self):
        if not self.model.completed:
            self.model.clock.pause()

    def unpause_hook(self):
        if not self.model.completed:
            self.model.clock.unpause()

    def tick_hook(self):
        self.model.update()


class GameHandler(hgf.StructuralComponent):
    def __init__(self, w, h, **kwargs):
        super().__init__(w, h, opacity=0, **kwargs)
        self.context = 'setgame'
        self.game = None
        self.exit_button = None
        self.pause_button = None
        self.restart_button = None
        self.completed_games = []

    def load_hook(self):
        self.game = SPGameEntity(*self.size)
        self.register(self.game)
        self.game._load()

        button_w = 100
        button_h = 50
        button_gap = 3 * button_w // 2
        button_x = self.w // 2 - 2 * button_w
        button_y = (self.game.play_deck.bottom + self.h - button_h) // 2
        self.exit_button = hgf.Button('Exit', 'exit', button_w, button_h)
        self.exit_button.pos = (button_x, button_y)
        self.register(self.exit_button)
        self.exit_button._load()

        button_x += button_gap
        self.pause_button = hgf.Button('Pause', 'toggle-pause', button_w, button_h)
        self.pause_button.pos = (button_x, button_y)
        self.register(self.pause_button)
        self.pause_button._load()

        button_x += button_gap
        self.restart_button = hgf.Button('Restart', 'restart', button_w, button_h)
        self.restart_button.pos = (button_x, button_y)
        self.register(self.restart_button)
        self.restart_button._load()

    def activate_hook(self):
        if not self.game.model.started:
            self.game.model.start()

    def handle_message(self, sender, message, **params):
        if message == 'exit':
            self.handle_message(sender, 'pause')
        if message == 'restart':
            self.handle_message(sender, 'unpause')
            self.game.model.restart()
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
            self.send_message(message, **params)
