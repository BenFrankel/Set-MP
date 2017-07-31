import hgf


class Card(hgf.SimpleWidget):
    MSG_TOGGLE_SELECTED = 'card-toggle-selected'

    def __init__(self, values, **kwargs):
        super().__init__(opacity=2, **kwargs)
        self.type = 'card'
        self._bg_factory = None

        self.values = values

        self.location = 0  # 0=draw, 1=play, 2=discard
        self.index = -1
        self.selected = False
        self.face_up = True

    @hgf.visualattr
    def face_up(self): pass

    @hgf.visualattr
    def selected(self): pass

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size,
                                           *self.values,
                                           face_up=self.face_up,
                                           selected=self.selected)

    def mouse_state_change_hook(self, before, after):
        if after == hgf.SimpleWidget.PRESS and self.face_up:
            self.selected = not self.selected

    def selected_change_hook(self, before, after):
        self.is_stale = True
        self.send_message(Card.MSG_TOGGLE_SELECTED, selected=after)

    def face_up_change_hook(self, before, after):
        self.is_stale = True

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

    def __eq__(self, other):
        try:
            return self.values == other.values
        except AttributeError:
            return False

    def __repr__(self):
        return '<Card({}, {}, {}, {})>'.format(*self.values)

    __str__ = __repr__
