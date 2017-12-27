import hgf


class LoginScreen(hgf.LayeredComponent):
    def __init__(self, **kwargs):
        super().__init__(opacity=0, **kwargs)
        self.select_button = None
        self.field = None

    def on_load(self):
        self.select_button = hgf.LabeledButton('Log in', 'select')
        self.register_load(self.select_button)

        self.field = hgf.TextField()
        self.register_load(self.field)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.select_button.size = 100, 50
        self.field.size = 200, 50

    def refresh_layout(self):
        super().refresh_layout()
        self.select_button.center = self.relcenter

        self.field.midbottom = self.select_button.midtop
        self.field.y -= 10

    def handle_message(self, sender, message, **params):
        if message == 'select':
            self.send_message('next')
        elif message == 'text-entry':
            print('got message\nsender:', sender, '\nmessage:', message, '\nparams:', params)
        else:
            super().handle_message(sender, message, **params)
