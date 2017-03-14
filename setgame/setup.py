from app import gui, AppManager
from .layout import GameHandler
from . import style


def setup(app):
    main_seq = gui.switch.Sequence(*app.size)
    main_hub = gui.switch.Hub(*main_seq.size)

    main_menu = gui.menu.Menu(*main_hub.size)
    main_menu.add_button('Single Player', 'sp')
    main_menu.add_button('Multiplayer', 'mp')
    main_menu.add_button('Quit', 'exit')
    main_hub.register_center(main_menu)

    sp_game = GameHandler(*main_hub.size)
    main_hub.register_node('sp', sp_game)

    main_seq.register_tail(main_hub)
    app.register(main_seq)


manager = AppManager('setgame')
manager.style_packs = style.style_packs
manager.compose_style = style.compose
manager.setup = setup
