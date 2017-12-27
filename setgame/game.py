from .deck import PlayDeck
from .pile import DiscardPile, DrawPile
from .clock import Clock
from .model import FoundSet, GameSummary, is_set, has_set

import hgf


class SPGame(hgf.LayeredComponent):
    STATE_UNSTARTED = 0
    STATE_STARTED = 1
    STATE_COMPLETE = 2

    def __init__(self, *args, opacity=0, **kwargs):
        super().__init__(opacity=opacity, *args, **kwargs)
        self.play_deck = None
        self.draw_pile = None
        self.discard_pile = None
        self.clock = None
        self.user = None
        self.players = None
        self.game_state = SPGame.STATE_UNSTARTED
        self.found_sets = []

    def on_load(self):
        self.play_deck = PlayDeck()
        self.register_load(self.play_deck)

        self.draw_pile = DrawPile(len(self.play_deck.draw_deck))
        self.draw_pile.num_cards = 81
        self.register_load(self.draw_pile)

        self.discard_pile = DiscardPile(len(self.play_deck.discard_deck))
        self.register_load(self.discard_pile)

        self.clock = Clock()
        self.register_load(self.clock)

        self.start()

    def refresh_proportions(self):
        super().refresh_proportions()
        self.play_deck.size = (int(self.w * 0.6),
                               int(self.h * 0.7))

        self.draw_pile.size = self.discard_pile.size = (int(self.play_deck.w // 5 * 1.3),
                                                        int(self.play_deck.h // 3.5 * 1.3))

        self.play_deck.y = (self.h - self.play_deck.h) // 3
        self.clock.size = (int((self.w - self.play_deck.w) * 0.4),
                           int(self.play_deck.y * 0.8))

    def refresh_layout(self):
        self.play_deck.x = (self.w - self.play_deck.w) // 2
        self.play_deck.y = (self.h - self.play_deck.h) // 3

        self.draw_pile.x = (self.w + self.play_deck.right - self.draw_pile.w) // 2
        self.discard_pile.x = (self.play_deck.left - self.discard_pile.w) // 2
        self.draw_pile.y = self.discard_pile.y = self.play_deck.midy

        self.clock.x = (self.w - self.clock.w) // 2
        self.clock.y = (self.play_deck.y - self.clock.h) // 2

    @hgf.double_buffer
    class completed: pass  # TODO: Handle win conditions here

    def find_set(self, player, cards):
        for card in sorted(cards, key=lambda x: x.index):
            # Card's index will change when we discard it, so remember the index first
            index = card.index
            self.discard(index)
            if len(self.play_deck._play_deck) < 12 and len(self.play_deck._draw_deck) > 0:
                self.draw_card(index)
        self.found_sets.append(FoundSet(player, cards))

    def start(self):
        # DEBUG ENDGAME
        # for i in range(69):
        #     self.deck.draw_card()
        #     self.deck.discard(0)
        self.game_state = SPGame.STATE_STARTED
        for _ in range(12):
            self.draw_card()
        self.clock.start()
        self.populate_play_deck()

    def populate_play_deck(self):
        while not has_set(self.play_deck._play_deck) or len(self.play_deck._play_deck) < 12:
            if len(self.play_deck._draw_deck) < 3:
                self.end()
                return
            for _ in range(3):
                self.draw_card()
        self.play_deck.refresh_proportions_flag = True

    def on_pause(self):
        super().on_pause()
        if self.game_state != SPGame.STATE_COMPLETE:
            for card in self.play_deck._play_deck:
                card.is_face_up = False

    def on_unpause(self):
        super().on_unpause()
        if self.game_state != SPGame.STATE_COMPLETE:
            for card in self.play_deck._play_deck:
                card.is_face_up = True

    def end(self):
        self.game_state = SPGame.STATE_COMPLETE
        self.clock.pause()
        summary = GameSummary(self)
        for card in self.play_deck._play_deck:
            card.discard()
        for player in self.players:
            player.end_game(summary)

    def reset(self):
        self.game_state = SPGame.STATE_UNSTARTED
        self.found_sets = []
        self.play_deck.shuffle()
        self.draw_pile.num_cards = 81
        self.discard_pile.num_cards = 0
        self.discard_pile.top_card = None
        self.clock.reset()

    def restart(self):
        self.reset()
        self.start()

    def add_player(self, player):
        self.players.append(player)

    def draw_card(self, index=None):
        self.draw_pile.num_cards -= 1
        self.play_deck.draw_card(index)

    def discard(self, index):
        self.discard_pile.num_cards += 1
        self.discard_pile.top_card = self.play_deck.discard(index)

    def handle_message(self, sender, message, **params):
        if message == PlayDeck.MSG_SET_SELECTED:
            selected = params['cards']
            if is_set(selected):
                self.find_set(self.user, selected)
                self.populate_play_deck()
            else:
                for card in selected:
                    card.toggle_select()
        else:
            super().handle_message(sender, message, **params)


class GameHandler(hgf.LayeredComponent):
    MSG_PAUSE = 'pause'
    MSG_UNPAUSE = 'unpause'
    MSG_TOGGLE_PAUSE = 'toggle-pause'
    MSG_RESTART = 'restart'

    def __init__(self, opacity=0, **kwargs):
        super().__init__(opacity=opacity, **kwargs)
        self.context = 'setgame'
        self.game = None
        self.exit_button = None
        self.pause_button = None
        self.restart_button = None
        self.completed_games = []

    def on_load(self):
        self.game = SPGame(z=-1)
        self.register_load(self.game)

        self.exit_button = hgf.LabeledButton('Exit', hgf.Hub.MSG_RETURN_TO_CENTER)
        self.register_load(self.exit_button)

        self.pause_button = hgf.LabeledButton('Pause', GameHandler.MSG_PAUSE)
        self.register_load(self.pause_button)

        self.restart_button = hgf.LabeledButton('Restart', GameHandler.MSG_RESTART)
        self.register_load(self.restart_button)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.game.size = self.size
        self.exit_button.size = self.pause_button.size = self.restart_button.size = 100, 50

    def refresh_layout(self):
        button_gap = 3 * self.exit_button.w // 2
        button_x = self.w // 2 - 2 * self.exit_button.w
        button_y = (self.game.play_deck.bottom + self.h - self.exit_button.h) // 2

        self.exit_button.pos = button_x, button_y

        button_x += button_gap
        self.pause_button.pos = button_x, button_y

        button_x += button_gap
        self.restart_button.pos = button_x, button_y

    def handle_message(self, sender, message, **params):
        if message == hgf.Hub.MSG_RETURN_TO_CENTER:
            self.handle_message(sender, GameHandler.MSG_PAUSE)
        if message == GameHandler.MSG_RESTART:
            self.handle_message(sender, GameHandler.MSG_UNPAUSE)
            self.game.restart()
        elif message == GameHandler.MSG_TOGGLE_PAUSE:
            if self.game.is_paused:
                self.handle_message(sender, GameHandler.MSG_UNPAUSE)
            else:
                self.handle_message(sender, GameHandler.MSG_PAUSE)
        elif message == GameHandler.MSG_PAUSE:
            self.game.pause()
            self.pause_button.label.text = 'Unpause'
            self.pause_button.message = GameHandler.MSG_UNPAUSE
        elif message == GameHandler.MSG_UNPAUSE:
            self.game.unpause()
            self.pause_button.label.text = 'Pause'
            self.pause_button.message = GameHandler.MSG_PAUSE
        else:
            super().handle_message(sender, message, **params)
