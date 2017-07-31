from .card import Card

import hgf

import random
import itertools


class PlayDeck(hgf.GraphicalComponent):
    MSG_SET_SELECTED = 'set-selected'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'play-deck'

        self.cards = None
        self._draw_deck = []
        self._play_deck = []
        self._discard_deck = []
        self._selected = []

        self._bg_factory = None

        self.dimensions = 0, 0

    def prepare_hook(self):
        self.cards = [Card(values) for values in itertools.product((0, 1, 2), repeat=4)]
        random.shuffle(self.cards)
        self.register_prepare(*self.cards)

        self._draw_deck = self.cards[:]

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size)

    @hgf.visualattr
    def dimensions(self): pass

    def dimensions_change_hook(self, before, after):
        rows, cols = self.dimensions
        card_w = min(int(self.w / (cols + 1)), int(self.w / 5))
        card_h = min(int(self.h / (rows + 0.5)), int(self.h / 3.5))
        for card in self.cards:
            card.size = card_w, card_h

    def resize_hook(self, before, after):
        card_size = self.card_size
        for card in self.cards:
            card.size = card_size

    def _dim_from_num(self, num):
        num_in_play = len(self.play_deck)
        rows = 3
        cols = max((num_in_play + 2) // rows, 1)
        if num_in_play <= 6:
            rows = max(num_in_play // 3, 1)
            cols = 3
        return rows, cols

    def notify(self, subject, diff):
        if subject == self.deck_model and diff.play_deck or subject in self.play_deck and diff.selected:
            rows, cols = self.dimensions
            card_w, card_h = self.card_size
            half_gap_w = (self.w - (self.w // cols) * (cols - 1) - card_w) // 2
            half_gap_h = (self.h - (self.h // rows) * (rows - 1) - card_h) // 2
            for card in self.cards:
                if card.in_play():
                    if not card.is_loaded:
                        card.prepare()
                    if card.size != (card_w, card_h):
                        card.size = card_w, card_h
                        card.is_stale = True
                    card.x = half_gap_w + (self.w // cols) * (card.index % cols)
                    card.y = half_gap_h + (self.h // rows) * (card.index // cols)
                    if card.selected:
                        card.y -= half_gap_h
                    if not card.is_visible:
                        card.activate()
                elif card.is_visible:
                    card.deactivate()

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

    def shuffle_play(self):
        random.shuffle(self._play_deck)
        for i, card in enumerate(self._play_deck):
            card.index = i

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

    def discard(self, index):
        to_discard = self._play_deck.pop(index)
        to_discard.discard()
        self._discard_deck.append(to_discard)
        for card in self._play_deck[index:]:
            card.index -= 1

    def handle_message(self, sender, message, **params):
        if message == Card.MSG_TOGGLE_SELECTED:
            if params['selected']:
                self._selected.append(sender)
                if len(self._selected) == 3:
                    self.send_message(PlayDeck.MSG_SET_SELECTED, cards=self._selected)
            else:
                self._selected.remove(sender)

    def __repr__(self):
        return '<Deck(' + str(self.cards)[1:-1] + ')>'

    __str__ = __repr__


class Pile(hgf.GraphicalComponent):
    def __init__(self, num_cards=0, **kwargs):
        super().__init__(opacity=2, **kwargs)
        self.type = 'discard-deck'
        self._bg_factory = None
        self._top_card = None
        self.num_cards = num_cards

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size, self.num_cards, self._top_card)

    @hgf.visualattr
    def num_cards(self): pass

    def num_cards_change_hook(self, before, after):
        self.is_stale = True

    def add_to_pile(self, card):
        self._top_card = card
        self.num_cards += 1


class DrawPile(Pile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'draw-pile'


class DiscardPile(Pile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'discard-pile'
