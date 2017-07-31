from .deck import PlayDeck, DiscardPile, DrawPile
from .clock import Clock
from .model import FoundSet, GameSummary, is_set, has_set

import hgf

import random


class SPGame(hgf.GraphicalComponent):
    STATE_UNSTARTED = 0
    STATE_STARTED = 1
    STATE_COMPLETE = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.play_deck = None
        self.draw_deck = None
        self.discard_deck = None
        self.clock = None
        self.user = None
        self.players = None
        self.game_state = SPGame.STATE_UNSTARTED
        self.found_sets = []

    def prepare_hook(self):
        self.play_deck = PlayDeck()
        self.register_prepare(self.play_deck)

        self.draw_deck = DrawPile(len(self.play_deck.draw_deck))
        self.register_prepare(self.draw_deck)

        self.discard_deck = DiscardPile(len(self.play_deck.discard_deck))
        self.register_prepare(self.discard_deck)

        self.clock = Clock()
        self.register_prepare(self.clock)

    def resize_hook(self, before, after):
        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)

        self.play_deck.size = deck_w, deck_h
        self.play_deck.x = (self.w - deck_w) // 2
        self.play_deck.y = (self.h - deck_h) // 3

        card_deck_w = int(self.play_deck.w // 5 * 1.3)
        card_deck_h = int(self.play_deck.h // 3.5 * 1.3)
        self.draw_deck.size = self.discard_deck = card_deck_w, card_deck_h

        self.draw_deck.x = (self.w + self.play_deck.right - card_deck_w) // 2
        self.draw_deck.y = self.play_deck.midy

        self.discard_deck.x = (self.play_deck.left - card_deck_w) // 2
        self.discard_deck.y = self.play_deck.midy

        clock_w = int((self.w - deck_w) * 0.4)
        clock_h = int(self.play_deck.y * 0.8)
        self.clock.size = clock_w, clock_h
        self.clock.x = (self.w - clock_w) // 2
        self.clock.y = (self.play_deck.y - clock_h) // 2

    def completed_change_hook(self, before, after):
        pass  # TODO: Handle win conditions here

    def find_set(self, player, cards):
        for card in sorted(cards, key=lambda x: x.index):
            index = card.index
            self.deck.discard(index)
            if len(self.deck.play_deck) < 12 and len(self.deck.draw_deck) > 0:
                self.deck.draw_card(index)
        self.found_sets.append(FoundSet(player, cards))

    def start(self):
        # DEBUG ENDGAME
        # for i in range(69):
        #     self.deck.draw_card()
        #     self.deck.discard(0)
        self.game_state = SPGame.STATE_STARTED
        for _ in range(12):
            self.play_deck.draw_card()
        self.clock.start()

    def pause(self):
        super().pause()
        if not self.is_completed:
            for card in self.deck.cards:
                card.flip()

    def unpause(self):
        super().unpause()
        if not self.is_completed:
            for card in self.deck.cards:
                card.flip()

    def end(self):
        self.game_state = SPGame.STATE_COMPLETE
        self.clock.pause()
        summary = GameSummary(self)
        for card in self.deck.play_deck:
            card.discard()
        for player in self.players:
            player.end_game(summary)

    def reset(self):
        self.game_state = SPGame.STATE_UNSTARTED
        self.found_sets = []
        self.play_deck.shuffle()
        self.clock.reset()

    def restart(self):
        self.reset()
        self.start()

    def add_player(self, player):
        self.players.append(player)

    def draw_card(self):
        self.play_deck.draw_card()
        self.draw_deck.num_cards -= 1
        self.discard_deck.num_cards += 1

    def handle_message(self, sender, message, **params):
        if message == PlayDeck.MSG_SET_SELECTED:
            selected = params['cards']
            if is_set(selected):
                self.find_set(self.user, selected)
            else:
                for card in selected:
                    card.toggle_select()
            while not has_set(self.deck.play_deck):
                if len(self.deck.draw_deck) < 3:
                    self.end()
                    return
                for _ in range(3):
                    self.draw_card()
        else:
            super().handle_message(sender, message, **params)


class GameHandler(hgf.GraphicalComponent):
    MSG_PAUSE = 'pause'
    MSG_UNPAUSE = 'unpause'
    MSG_TOGGLE_PAUSE = 'toggle-pause'
    MSG_RESTART = 'restart'

    def __init__(self, **kwargs):
        super().__init__(opacity=0, **kwargs)
        self.context = 'setgame'
        self.game = None
        self.exit_button = None
        self.pause_button = None
        self.restart_button = None
        self.completed_games = []

    def resize_hook(self, before, after):
        self.game.size = after

        button_w = 100
        button_h = 50
        self.exit_button.size = self.pause_button.size = self.restart_button.size = button_w, button_h

        button_gap = 3 * button_w // 2
        button_x = self.w // 2 - 2 * button_w
        button_y = (self.game.play_deck.bottom + self.h - button_h) // 2

        self.exit_button.pos = button_x, button_y

        button_x += button_gap
        self.pause_button.pos = button_x, button_y

        button_x += button_gap
        self.restart_button.pos = button_x, button_y

    def prepare_hook(self):
        self.game = SPGame()
        self.register_prepare(self.game)

        self.exit_button = hgf.Button('Exit', hgf.Hub.MSG_RETURN_TO_CENTER)
        self.register_prepare(self.exit_button)

        self.pause_button = hgf.Button('Pause', GameHandler.MSG_PAUSE)
        self.register_prepare(self.pause_button)

        self.restart_button = hgf.Button('Restart', GameHandler.MSG_RESTART)
        self.register_prepare(self.restart_button)

    def activate_hook(self):
        self.game.start()

    def handle_message(self, sender, message, **params):
        if message == hgf.Hub.MSG_RETURN_TO_CENTER:
            self.handle_message(sender, GameHandler.MSG_PAUSE)
        elif message == GameHandler.MSG_RESTART:
            self.handle_message(sender, GameHandler.MSG_UNPAUSE)
            self.game.restart()
        elif message == GameHandler.MSG_TOGGLE_PAUSE:
            if self.game.is_paused:
                self.handle_message(sender, GameHandler.MSG_UNPAUSE)
            else:
                self.handle_message(sender, GameHandler.MSG_PAUSE)
        elif message == GameHandler.MSG_PAUSE:
            self.game.pause()
            self.pause_button.label_name = 'Unpause'
        elif message == GameHandler.MSG_UNPAUSE:
            self.game.unpause()
            self.pause_button.label_name = 'Pause'
        else:
            super().handle_message(sender, message, **params)
