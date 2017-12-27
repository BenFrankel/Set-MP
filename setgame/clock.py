import hgf


class Clock(hgf.Pulse, hgf.LayeredComponent):
    MSG_CLOCK_TICK = 'clock-tick'

    def __init__(self, **kwargs):
        super().__init__(Clock.MSG_CLOCK_TICK,
                         frequency=hgf.Time(s=1),
                         opacity=1,
                         **kwargs)
        self.type = 'clock'
        self._bg_factory = None
        self.label = None

    def on_load(self):
        self.label = hgf.Text('0:00', parent_style=True)
        self.register_load(self.label)

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.label.fontsize = int(self.h * 0.9)

    def refresh_layout(self):
        self.label.center = self.relcenter

    def reset(self):
        super().reset()
        self.label.text = '0:00'

    def trigger(self):
        self.label.text = '{:d}:{:02d}'.format(self.time.m, self.time.s)
        if self.time.h >= 1:
            self.label.font = self.style_get('font')  # TODO: Use default font
            self.label.text = 'Zzz..'
