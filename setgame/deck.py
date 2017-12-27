from .card import Card

import hgf

import random
import itertools


class PlayDeck(hgf.LayeredComponent):
    MSG_SET_SELECTED = 'set-selected'

    def __init__(self, **kwargs):
        super().__init__(opacity=1, **kwargs)
        self.type = 'play-deck'

        self.cards = None
        self._draw_deck = []
        self._play_deck = []
        self._discard_deck = []
        self._selected = []

        self._bg_factory = None

        self.dimensions = 0, 0

    def on_load(self):
        self.cards = [Card(values, active=False) for values in itertools.product((0, 1, 2), repeat=4)]
        random.shuffle(self.cards)
        self.register_load(*self.cards)

        self._draw_deck = self.cards[:]

    def refresh_proportions(self):
        super().refresh_proportions()
        self.dimensions = self._dim_from_num()
        old_card_size = self.cards[0].size
        card_size = self._card_size_from_dim()
        if old_card_size != card_size:
            for card in self.cards:
                card.size = card_size
                card.on_w_transition()
                card.on_h_transition()

    def refresh_layout(self):
        rows, cols = self.dimensions
        half_gap_w = (self.w - (self.w // cols) * (cols - 1) - self.cards[0].w) // 2
        half_gap_h = (self.h - (self.h // rows) * (rows - 1) - self.cards[0].h) // 2
        for card in self.cards:
            if card.location == Card.IN_PLAY:
                card.x = half_gap_w + (self.w // cols) * (card.index % cols)
                card.y = half_gap_h + (self.h // rows) * (card.index // cols)
                if card.is_selected:
                    card.y -= 10
                card.on_x_transition()
                card.on_y_transition()

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size)

    def _dim_from_num(self):
        num_in_play = len(self.play_deck)
        rows = 3
        cols = max((num_in_play + 2) // rows, 1)
        if num_in_play <= 6:
            rows = max(num_in_play // 3, 1)
            cols = 3
        return rows, cols

    def _card_size_from_dim(self):
        return min(int(self.w / (self.dimensions[1] + 1)), int(self.w / 5)),\
               min(int(self.h / (self.dimensions[0] + 0.5)), int(self.h / 3.5))

    @property
    def draw_deck(self):
        return tuple(self._draw_deck)

    @property
    def play_deck(self):
        return tuple(self._play_deck)

    @property
    def discard_deck(self):
        return tuple(self._discard_deck)

    def shuffle(self):
        for card in self.cards:
            card.shuffle()
        random.shuffle(self.cards)
        self._draw_deck = self.cards[:]
        self._play_deck = []
        self._discard_deck = []
        self.refresh_layout_flag = True

    def shuffle_play(self):
        random.shuffle(self._play_deck)
        for i, card in enumerate(self._play_deck):
            card.index = i
        self.refresh_layout_flag = True

    def get_selected(self):
        return list(filter(lambda x: x.selected, self._play_deck))

    def draw_card(self, index=None):
        if index is None:
            index = random.randrange(len(self._play_deck) + 1)
        for card in self._play_deck[index:]:
            card.index += 1
        next_card = self._draw_deck.pop()
        next_card.draw_card(index)
        self._play_deck.insert(index, next_card)
        self.refresh_layout_flag = True
        return next_card

    def discard(self, index):
        to_discard = self._play_deck.pop(index)
        to_discard.discard()
        self._discard_deck.append(to_discard)
        for card in self._play_deck[index:]:
            card.index -= 1
        self.refresh_layout_flag = True
        return to_discard

    def handle_message(self, sender, message, **params):
        if message == Card.MSG_TOGGLE_SELECTED:
            self.refresh_layout_flag = True
            if params['selected']:
                self._selected.append(sender)
                if len(self._selected) == 3:
                    self.send_message(PlayDeck.MSG_SET_SELECTED, cards=tuple(self._selected))
            else:
                self._selected.remove(sender)
        else:
            super().handle_message(sender, message, **params)
