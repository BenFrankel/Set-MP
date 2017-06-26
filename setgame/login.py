import hgf


class LoginScreen(hgf.StructuralComponent):
    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, **kwargs)
        self.select_button = None
        self.field = None

    def load_hook(self):
        self.select_button = hgf.Button('Log in', 'select', 100, 50)
        self.select_button.center = self.rel_rect().center
        self.register_load(self.select_button)

        self.field = hgf.TextField(200, 50)
        self.field.midbottom = self.select_button.midtop
        self.field.y -= 10
        self.register_load(self.field)

    def handle_message(self, sender, message, **params):
        if message == 'select':
            self.send_message('next')
        elif message == 'text-entry':
            print('got message\nsender:', sender, '\nmessage:', message, '\nparams:', params)
        else:
            self.send_message(message)
