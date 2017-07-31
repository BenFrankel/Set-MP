import hgf


class LoginScreen(hgf.GraphicalComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.select_button = None
        self.field = None
        self.drag_test = None

    def load_hook(self):
        self.select_button = hgf.Button('Log in', 'select', w=100, h=50)
        self.select_button.center = self.rel_rect().center
        self.register_load(self.select_button)

        self.field = hgf.TextField(w=200, h=50)
        self.field.midbottom = self.select_button.midtop
        self.field.y -= 10
        self.register_load(self.field)

        self.drag_test = hgf.DragWidget(box=self, w=100, h=100)

    def handle_message(self, sender, message, **params):
        if message == 'select':
            self.send_message('next')
        elif message == 'text-entry':
            print('got message\nsender:', sender, '\nmessage:', message, '\nparams:', params)
        else:
            super().handle_message(sender, message, **params)
