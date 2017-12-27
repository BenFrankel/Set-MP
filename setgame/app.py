from .game import GameHandler
from .login import LoginScreen
from . import style

import hgf


class SetgameApp(hgf.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_seq = None
        self.main_hub = None
        self.main_menu = None
        self.login_screen = None
        self.sp_game = None

    def on_load(self):
        self.login_screen = LoginScreen()

        self.main_menu = hgf.Menu(title='Set Game', opacity=0)
        self.main_menu.add_button('Single Player', 'sp')
        self.main_menu.add_button('Multiplayer', 'mp')
        self.main_menu.add_button('Quit', 'exit')

        self.sp_game = GameHandler()

        self.main_hub = hgf.Hub()
        self.main_hub.register_center(self.main_menu)
        self.main_hub.register_node('sp', self.sp_game)

        self.main_seq = hgf.Sequence()
        self.main_seq.register_tail(self.login_screen)
        self.main_seq.register_tail(self.main_hub)

        self.register_load(self.main_seq)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.main_seq.size = self.size

    def refresh_layout(self):
        self.main_seq.pos = self.pos


launcher = hgf.AppManager('setgame', SetgameApp)
launcher.style_packs = style.style_packs
launcher.compose_style = style.compose
