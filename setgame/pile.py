import hgf


class Pile(hgf.LayeredComponent):
    def __init__(self, num_cards=0, **kwargs):
        super().__init__(opacity=1, **kwargs)
        self._bg_factory = None
        self.top_card = None
        self.num_cards = num_cards

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size, self.num_cards, self.top_card)

    @hgf.double_buffer
    class num_cards:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class top_card:
        def on_transition(self):
            self.refresh_background_flag = True


class DrawPile(Pile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'draw-pile'


class DiscardPile(Pile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'discard-pile'
