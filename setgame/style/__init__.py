"""
Preset style manager for the setgame app.
"""


from . import default as _default
from ._build import compose


__all__ = ['default']


default_style_pack = {
    'button': {
        'default': {
            'background': _default.button_bg
        }
    },

    'text-box': {
        'default': {
            'background': _default.text_box_bg,
            'cursor-bg': _default.text_box_cursor_bg
        }
    },

    'clock': {
        'setgame': {
            'background': _default.clock_bg
        }
    },

    'card': {
        'setgame': {
            'front': _default.card_front,
            'back': _default.card_back,
            'symbol-shape': _default.symbol_shape,
            'symbol-texture': _default.symbol_texture,
            'symbol-color': _default.symbol_color
        }
    },

    'play-deck': {
        'setgame': {
            'background': _default.play_deck_bg
        }
    }
}

style_packs = {
    'default': default_style_pack
}
