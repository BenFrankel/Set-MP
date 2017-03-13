"""
Preset style manager for the setgame app.
"""


from . import default as _default
from ._build import compose


__all__ = ['default']


default_style_pack = {
    'button': {
        'default': {
            'button': _default.button
        }
    },

    'clock': {
        'setgame': {
            'bg': _default.clock_bg
        }
    },

    'card': {
        'setgame': {
            'front': _default.card_front,
            'back': _default.card_back,
            'symbol shape': _default.symbol_shape,
            'symbol texture': _default.symbol_texture,
            'symbol color': _default.symbol_color
        }
    },

    'play-deck': {
        'setgame': {
            'bg': _default.play_deck_bg
        }
    }
}

style_packs = {
    'default': default_style_pack
}
