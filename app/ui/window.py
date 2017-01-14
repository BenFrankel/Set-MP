import pygame

from . import base


class Window(base.Entity):
    def __init__(self, *args, **kwargs):
        self.surf = pygame.display.set_mode(*args, **kwargs)
        super().__init__(*self.surf.get_size(), typable=True, **kwargs)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event.unicode, event.key, event.mod)
        elif event.type == pygame.KEYUP:
            self.key_up(event.key, event.mod)
        elif event.type == pygame.MOUSEMOTION:
            start = (event.pos[0] - event.rel[0], event.pos[1] - event.rel[1])
            self.mouse_motion(start, event.pos, event.buttons)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_up(event.pos, event.button)

    def handle_message(self, sender, message):
        if message == 'exit':
            exit()
        else:
            super().handle_message(sender, message)

    def _draw(self):
        if super()._draw():
            self.surf.blit(self._display, (0, 0))
            pygame.display.update()
