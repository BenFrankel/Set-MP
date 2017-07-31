import hgf


class Clock(hgf.GraphicalComponent):
    MSG_CLOCK_TICK = 'clock-tick'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'clock'

        self.clock_ticker = None
        self.text = None

        self._bg_factory = None

    def resize_hook(self, before, after):
        self.text.fontsize = int(self.h * 0.9)

    def prepare_hook(self):
        self.text = hgf.Text(parent_style=True)
        self.register_prepare(self.text)

        self.clock_ticker = hgf.Pulse(Clock.MSG_CLOCK_TICK, frequency=hgf.Time(s=1))
        self.register_prepare(self.clock_ticker)

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size)

    def freeze_hook(self):
        self.clock_ticker.pause()

    def unfreeze_hook(self):
        self.clock_ticker.unpause()

    def handle_message(self, sender, message, **params):
        if message == 'clock-second':
            self.text.text = '{:d}:{:02d}'.format(self.clock_ticker.time.m, self.clock_ticker.time.s)
            if self.clock_ticker.time.h >= 1:
                self.text.font = self.style_get('font')  # TODO: Use default font
                self.text.text = 'Zzz..'
            self.text.center = self.rel_rect().center
        else:
            super().handle_message(sender, message, **params)