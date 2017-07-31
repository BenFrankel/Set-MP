# class Game(model.Subject):
#     def __init__(self):
#         super().__init__()
#         self.state_properties = 'started', 'completed', 'time'
#
#     def load_hook(self):
#         self.deck = Deck()
#         self.register(self.deck)
#         self.deck.load()
#
#         self.clock = hgf.Timer()
#
#         self.user = Player('Username')
#         self.players = [self.user]
#
#     @property
#     def time(self):
#         return self.clock.time.s
import itertools


def is_match(values):
    return len(values) == 3 and sum(values) % 3 == 0


def is_set(cards):
    return all(is_match(comparison) for comparison in zip(*[card.values for card in cards]))


def has_set(cards):
    return any(is_set(sub) for sub in itertools.combinations(cards, 3))


def all_sets(cards):
    return list(filter(is_set, itertools.combinations(cards, 3)))


class FoundSet:
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards


class PlayerSummary:
    def __init__(self, player, found_sets):
        self.name = player.name
        self.found_sets = found_sets
        self.won = False


class GameSummary:
    def __init__(self, game):
        self.time = game.clock.time
        self.found_sets = game.found_sets
        self.players = []
        for player in game.players:
            found_sets = list(filter(lambda y: y.player is player, self.found_sets))
            self.players.append(PlayerSummary(player, found_sets))
        self.players.sort(key=lambda x: len(x.found_sets))
        self.winner = self.players[0]
        self.winner.won = True

    def __str__(self):
        return '{} wins! - {} sets in {} seconds.'.format(self.winner.name, len(self.winner.found_sets), self.time.in_s())


class Player:
    def __init__(self, name):
        self.name = name
        self.won_games = []

    def end_game(self, summary):
        if summary.winner.name == self.name:
            self.won_games.append(summary)
            print(summary)
