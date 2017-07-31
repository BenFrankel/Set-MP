from .game import GameHandler
from .login import LoginScreen
from . import style

import hgf


class SetgameApp(hgf.App):
    def load_hook(self):
        main_seq = hgf.Sequence(w=self.w, h=self.h)
        login_screen = LoginScreen(w=main_seq.w, h=main_seq.h)

        main_seq.register_head(login_screen)

        main_hub = hgf.Hub(w=main_seq.w, h=main_seq.h)

        main_menu = hgf.Menu(w=main_hub.w, h=main_hub.h, title='Set Game')
        main_menu.add_button('Single Player', 'sp')
        main_menu.add_button('Multiplayer', 'mp')
        main_menu.add_button('Quit', 'exit')
        main_hub.register_center(main_menu)

        sp_game = GameHandler(w=main_hub.w, h=main_hub.h)
        main_hub.register_node('sp', sp_game)

        main_seq.register_tail(main_hub)
        self.register_load(main_seq)


launcher = hgf.AppManager('setgame', SetgameApp)
launcher.style_packs = style.style_packs
launcher.compose_style = style.compose
