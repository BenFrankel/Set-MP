import itertools
import random

import timer
from ui import model


def is_match(values):
    if len(values) != 3:
        return False
    return all(values[i] == values[i+1] for i in range(len(values) - 1)) or len(set(values)) == len(values)


def is_set(cards):
    return all(is_match(comparison) for comparison in zip(*[card.values for card in cards]))


def has_set(cards):  # Not important, but is there an O(N) algorithm?
    return any(is_set(sub) for sub in itertools.combinations(cards, 3))


def all_sets(cards):
    return list(filter(is_set, itertools.combinations(cards, 3)))


class Card(model.Subject):
    def __init__(self, values):
        super().__init__()
        self.values = values
        self.location = 0  # 0=draw, 1=play, 2=discard
        self.index = -1
        self.selected = False
        self.state_attributes = 'selected', 'location', 'index'

    def toggle_select(self):
        self.selected = not self.selected

    def draw_card(self, index):
        self.location = 1
        self.index = index

    def discard(self):
        self.selected = False
        self.location = 2
        self.index = -1

    def shuffle(self):
        self.discard()
        self.location = 0

    def in_draw(self):
        return self.location == 0

    def in_play(self):
        return self.location == 1

    def in_discard(self):
        return self.location == 2

    def __eq__(self, other):
        try:
            return self.values == other.values
        except AttributeError:
            return False

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<Card(' + str(self.values)[1:-1] + ')>'


class Deck(model.Subject):
    def __init__(self):
        super().__init__()
        self.cards = [Card(values) for values in itertools.product((0, 1, 2), repeat=4)]
        self.register_all(self.cards)
        random.shuffle(self.cards)
        self.draw_deck = self.cards[:]
        self.play_deck = []
        self.discard_deck = []
        self.state_attrs = 'draw_deck', 'play_deck', 'discard_deck'

    def shuffle(self):
        for card in self.cards:
            card.shuffle()
        random.shuffle(self.cards)
        self.draw_deck = self.cards[:]
        self.play_deck = []
        self.discard_deck = []

    def play_shuffle(self):
        random.shuffle(self.play_deck)
        for i, card in enumerate(self.play_deck):
            card.index = i

    def get_selected(self):
        return list(filter(lambda x: x.selected, self.play_deck))

    def draw_card(self, index=None):
        if index is None:
            index = len(self.play_deck)
        for card in self.play_deck[index:]:
            card.index += 1
        next_card = self.draw_deck.pop()
        next_card.draw_card(index)
        self.play_deck.insert(index, next_card)

    def discard(self, index):
        to_discard = self.play_deck.pop(index)
        to_discard.discard()
        self.discard_deck.append(to_discard)
        for card in self.play_deck[index:]:
            card.index -= 1

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '<Deck(' + str(self.cards)[1:-1] + ')>'


class Game(model.Subject):
    def __init__(self):
        super().__init__()
        self.deck = Deck()
        self.register(self.deck)
        self.found_sets = [self.deck.cards[:3]]
        self.clock = timer.Timer()
        self.completed = False
        self.state_attributes = 'completed', 'clock', 'found_sets'

    def start_game(self):
        # TESTING ENDGAME
        # for i in range(69):
        #     self.deck.draw_card()
        #     self.deck.discard(0)
        for _ in range(12):
            self.deck.draw_card()
        self.clock.restart()
        self.completed = False

    def reset_game(self):
        self.deck.shuffle()
        self.found_sets = []
        self.clock.reset()
        self.completed = False

    def end_game(self):
        self.clock.pause()
        for card in self.deck.play_deck:
            card.discard()
        self.completed = True

    def update(self):
        if not self.completed:
            selected = self.deck.get_selected()
            if len(selected) >= 3:
                if is_set(selected):
                    for card in sorted(selected, key=lambda x: x.index):
                        index = card.index
                        self.deck.discard(index)
                        if len(self.deck.play_deck) < 12 and len(self.deck.draw_deck) > 0:
                            self.deck.draw_card(index)
                    self.found_sets.append(selected)
                else:
                    for card in selected:
                        card.toggle_select()
            while not has_set(self.deck.play_deck):
                if len(self.deck.draw_deck) < 3:
                    self.end_game()
                    return
                for _ in range(3):
                    self.deck.draw_card(random.randrange(len(self.deck.play_deck)))
        super().update()
