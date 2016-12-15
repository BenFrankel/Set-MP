import gui
import setgame_logic
import setgame_style


class CardEntity(gui.StyledEntity):
    def __init__(self, card, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = card
        self.current_state = None

    def mouse_up(self, event):
        self.card.toggle_select()
        super().mouse_up(event)

    def pre_draw(self):
        if self.current_state != (self.size, self.card.selected):
            self.current_state = self.size, self.card.selected
            self.surf = self.style.card_image(self.size, *self.card.values, self.card.selected)


class DeckEntity(gui.StyledEntity):
    def __init__(self, deck, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck = deck
        e_card_w = int(self.w / 5)
        e_card_h = int(self.h / 3.5)
        self.e_cards = [CardEntity(card, (0, 0, e_card_w, e_card_h)) for card in self.deck.cards]
        self.register_all(self.e_cards)

    def update(self):
        num_in_play = len(self.deck.play_deck)
        cols = max((num_in_play + 2) // 3, 1)
        rows = 3
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

    def pre_draw(self):
        self.surf = self.style.bg_deck_image(self.size)


# TODO: Display cards remaining in draw deck.
# TODO: Display time since beginning of game.
class GameEntity(gui.StyledEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = setgame_logic.Game()
        self.set_style(setgame_style.default)
        deck_w = int(self.w * 0.6)
        deck_h = int(self.h * 0.7)
        self.e_deck = DeckEntity(self.game.deck, (self.w - deck_w)//2, (self.h - deck_h)//4, deck_w, deck_h)
        self.register(self.e_deck)

    def update(self):
        if not self.game.playing:  # TODO: Can handle win conditions here as well.
            self.game.play()
        self.game.update()
        super().update()

