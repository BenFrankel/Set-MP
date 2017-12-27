import hgf


class Card(hgf.SimpleWidget):
    MSG_TOGGLE_SELECTED = 'card-toggle-selected'

    IN_DRAW = 0
    IN_PLAY = 1
    IN_DISCARD = 2

    def __init__(self, values, **kwargs):
        super().__init__(opacity=2, **kwargs)
        self.type = 'card'
        self._bg_factory = None

        self.values = values

        self.location = Card.IN_DRAW
        self.index = -1
        self.is_selected = False
        self.is_face_up = True

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size,
                                           *self.values,
                                           face_up=self.is_face_up,
                                           selected=self.is_selected)

    @hgf.double_buffer
    class is_face_up:
        def on_transition(self):
            self.refresh_background_flag = True

    @hgf.double_buffer
    class is_selected:
        def on_transition(self):
            self.refresh_background_flag = True

        def on_change(self, before, after):
            self.send_message(Card.MSG_TOGGLE_SELECTED, selected=after)

    def flip(self):
        self.is_face_up = not self.is_face_up

    def toggle_select(self):
        self.is_selected = not self.is_selected

    def on_mouse_state_change(self, before, after):
        super().on_mouse_state_change(before, after)
        if after == hgf.SimpleWidget.PRESS and self.is_face_up:
            self.toggle_select()

    def draw_card(self, index, face_up=True):
        self.activate()
        self.location = Card.IN_PLAY
        self.index = index
        self.is_face_up = face_up

    def discard(self):
        self.deactivate()
        self.location = Card.IN_DISCARD
        self.index = -1
        self.is_selected = False

    def shuffle(self):
        self.discard()
        self.location = Card.IN_DRAW

    def __eq__(self, other):
        try:
            return self.values == other.values
        except AttributeError:
            return False

    def __repr__(self):
        return 'Card({}, {}, {}, {}, pos={})'.format(*self.values, self.pos)

    __str__ = __repr__
