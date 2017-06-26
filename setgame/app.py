from .layout import GameHandler
from .login import LoginScreen
from . import style

import hgf


class SetgameApp(hgf.App):
    def load_hook(self):
        main_seq = hgf.Sequence(*self.size)
        login_screen = LoginScreen(*main_seq.size)

        main_seq.register_head(login_screen)

        main_hub = hgf.Hub(*main_seq.size)

        main_menu = hgf.Menu(*main_hub.size)
        main_menu.add_button('Single Player', 'sp')
        main_menu.add_button('Multiplayer', 'mp')
        main_menu.add_button('Quit', 'exit')
        main_hub.register_center(main_menu)

        sp_game = GameHandler(*main_hub.size)
        main_hub.register_node('sp', sp_game)

        main_seq.register_tail(main_hub)
        self.register(main_seq)
        main_seq._load()


launcher = hgf.AppManager('setgame', SetgameApp)
launcher.style_packs = style.style_packs
launcher.compose_style = style.compose
