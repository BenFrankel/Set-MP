import pygame





# ~~ STYLE ~~

def style(button):
    return {'button': button}


def def_button(size, state):
    surf = pygame.Surface(size)

    shade = [0, 40, 40, 60, 60][state.value]

    surf.fill((shade, shade, shade))
    surf.set_alpha(100)

    return surf


default_style = style(def_button)


# ~~ OPTIONS ~~

class Options:
    def __init__(self, options=None, **kwargs):
        self._options = dict(options, **kwargs)
        for name in self._options:
            setattr(self, name, self._options[name])

    def options_add(self, options=None, **kwargs):
        self._options.update(options, **kwargs)
