from enum import Enum

import pygame

import const
from ui.layout import Entity, Text


class WidgetState(Enum):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4


class Widget(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hoverable=True, clickable=True, **kwargs)
        self._widget_state = WidgetState.IDLE

    @property
    def widget_state(self):
        return self._widget_state

    @widget_state.setter
    def widget_state(self, other):
        before = self._widget_state
        self._widget_state = other
        if before != other:
            self.widget_state_change(before, other)
            # self.update_background()

    def widget_state_change(self, before, after):
        return False

    def pause(self):
        self.widget_state = WidgetState.IDLE
        super().pause()

    def mouse_enter(self, start, end, buttons):
        if self.widget_state == WidgetState.IDLE:
            if buttons[0]:
                self.widget_state = WidgetState.PUSH
            else:
                self.widget_state = WidgetState.HOVER
        elif self.widget_state == WidgetState.PULL:
            self.widget_state = WidgetState.PRESS
        super().mouse_enter(start, end, buttons)

    def mouse_exit(self, start, end, buttons):
        if self.widget_state == WidgetState.HOVER or self.widget_state == WidgetState.PUSH:
            self.widget_state = WidgetState.IDLE
        elif self.widget_state == WidgetState.PRESS:
            self.widget_state = WidgetState.PULL
        super().mouse_exit(start, end, buttons)

    def mouse_down(self, pos, button):
        if button == 1:
            if self.widget_state != WidgetState.HOVER:
                self.widget_state = WidgetState.HOVER
            self.widget_state = WidgetState.PRESS
        super().mouse_down(pos, button)

    def mouse_up(self, pos, button):
        if button == 1:
            if self.widget_state == WidgetState.PRESS or self.widget_state == WidgetState.PUSH:
                self.widget_state = WidgetState.HOVER
            elif self.widget_state == WidgetState.PULL:
                self.widget_state = WidgetState.IDLE
        super().mouse_up(pos, button)

    def update(self):
        if self.widget_state == WidgetState.PULL and not pygame.mouse.get_pressed()[0]:
            self.widget_state = WidgetState.IDLE
        super().update()


class Button(Widget):
    def __init__(self, name, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.message = message

        self.label = Text(name, fontsize=max(self.h//3, 14), fgcolor=(255, 255, 255))
        self.register(self.label)

    def widget_state_change(self, before, after):
        if before == WidgetState.PRESS and after == WidgetState.HOVER:
            self.send_message(self.message)
        self.update_background()

    def update_background(self):
        try:
            self.background = self.style_get(const.style_button, self.size, self.widget_state)
        except KeyError:
            super().update_background()

    def update(self):
        self.label.center = self.rel_rect().center
        if self.widget_state == WidgetState.PRESS:
            self.label.x -= 1
            self.label.y += 1
        super().update()


class Menu(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = list()

    def add_button(self, name, message):
        # TODO: Something smarter than this...
        button_w = self.w // 5
        button_h = self.h // 10
        button = Button(name, message, button_w, button_h)
        self.buttons.append(button)
        self.register(button)

    def update(self):
        # TODO: Smarter than this too..
        button_y = 10
        for button in self.buttons:
            button.x = 10
            button.y = button_y + 200
            button_y += button.h + 10
        super().update()
