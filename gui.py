import pygame

import font_loader
import const


# ? Entity proxy that creates itself when show() and deletes itself when hide()
# Some events from mouse enter / exit / motion may be lost.
class Entity:
    def __init__(self, w, h, x=0, y=0, visible=True, hoverable=True, clickable=True):
        self._w = w
        self._h = h
        self._x = x
        self._y = y
        self.z = 0

        self.visible = visible
        self.hoverable = hoverable
        self.clickable = clickable
        self.paused = False

        self.hovered = False

        self.parent = None
        self.children = []
        self.key_listener = None

        self.base_state = None
        self._base = pygame.Surface((w, h), pygame.SRCALPHA)
        self.surf = pygame.Surface((w, h), pygame.SRCALPHA)

        self.hitbox = None

        self.style = dict()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, other):
        self._base = other
        self._w, self._h = other.get_size()

    @property
    def size(self):
        self.refresh()
        return self._w, self._h

    @size.setter
    def size(self, other):
        self._w, self._h = other
        self.refresh()

    @property
    def w(self):
        return self.size[0]

    @w.setter
    def w(self, other):
        self.size = (other, self.size[1])

    @property
    def h(self):
        return self.size[1]

    @h.setter
    def h(self, other):
        self.size = (self.size[0], other)

    @property
    def width(self):
        return self.w

    @width.setter
    def width(self, other):
        self.w = other

    @property
    def height(self):
        return self.h

    @height.setter
    def height(self, other):
        self.h = other

    @property
    def pos(self):
        return self._x, self._y

    @pos.setter
    def pos(self, other):
        self._x, self._y = other

    topleft = pos

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, other):
        self.pos = (other, self.pos[1])

    left = x

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, other):
        self.pos = (self.pos[0], other)

    top = y

    @property
    def midx(self):
        return self.x + self.w // 2

    @midx.setter
    def midx(self, other):
        self.x = other - self.w // 2

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, other):
        self.x = other - self.w

    @property
    def midy(self):
        return self.y + self.h // 2

    @midy.setter
    def midy(self, other):
        self.y = other - self.h // 2

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, other):
        self.y = other - self.h

    @property
    def midtop(self):
        return self.midx, self.top

    @midtop.setter
    def midtop(self, other):
        self.midx, self.top = other

    @property
    def topright(self):
        return self.right, self.top

    @topright.setter
    def topright(self, other):
        self.right, self.top = other

    @property
    def midleft(self):
        return self.x, self.y + self.h // 2

    @midleft.setter
    def midleft(self, other):
        self.left, self.midy = other

    @property
    def center(self):
        return self.midx, self.midy

    @center.setter
    def center(self, other):
        self.midx, self.midy = other

    @property
    def midright(self):
        return self.right, self.midy

    @midright.setter
    def midright(self, other):
        self.right, self.midy = other

    @property
    def bottomleft(self):
        return self.left, self.bottom

    @bottomleft.setter
    def bottomleft(self, other):
        self.left, self.bottom = other

    @property
    def midbottom(self):
        return self.midx, self.bottom

    @midbottom.setter
    def midbottom(self, other):
        self.midx, self.bottom = other

    @property
    def bottomright(self):
        return self.right, self.bottom

    @bottomright.setter
    def bottomright(self, other):
        self.right, self.bottom = other

    def show(self):
        self.visible = True
        self.unpause()

    def hide(self):
        self.visible = False
        self.pause()

    def pause(self):
        self.paused = True
        for child in self.children:
            child.pause()

    def unpause(self):
        self.paused = False
        for child in self.children:
            child.unpause()

    def register(self, child):
        self.children.append(child)
        if child.parent is not None:
            child.parent.unregister(child)
        child.parent = self

    def register_all(self, children):
        for child in children:
            self.register(child)

    def unregister(self, child):
        self.children.remove(child)
        child.parent = None

    def unregister_all(self, children):
        for child in children:
            self.unregister(child)

    def key_down(self, unicode, key, mod):
        if self.key_listener is not None:
            self.key_listener.key_down(unicode, key, mod)

    def key_up(self, key, mod):
        if self.key_listener is not None:
            self.key_listener.key_down(key, mod)

    def mouse_enter(self, start, end, buttons):
        for child in self.children:
            if child.hoverable and not child.paused and child.contains(end):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_enter(rel_start, rel_end, buttons)

    def mouse_exit(self, start, end, buttons):
        for child in self.children:
            if child.hoverable and not child.paused and child.contains(start):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_exit(rel_start, rel_end, buttons)

    def mouse_motion(self, start, end, buttons):
        for child in self.children:
            if child.hoverable and not child.paused:
                contains_start = child.contains(start)
                contains_end = child.contains(end)
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                if contains_start and contains_end:
                    child.mouse_motion(rel_start, rel_end, buttons)
                elif contains_start:
                    child.mouse_exit(rel_start, rel_end, buttons)
                elif contains_end:
                    child.mouse_enter(rel_start, rel_end, buttons)

    def mouse_down(self, pos, button):
        for child in self.children:
            if child.clickable and not child.paused and child.contains(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_down(rel_pos, button)

    def mouse_up(self, pos, button):
        for child in self.children:
            if child.clickable and not child.paused and child.contains(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_up(rel_pos, button)

    def handle_message(self, sender, message):
        self.send_message(message)

    def send_message(self, message):
        if self.parent is not None:
            self.parent.handle_message(self, message)

    def contains(self, pos):
        if self.hitbox is not None:
            return self.hitbox.collidepoint(pos)
        return self.left <= pos[0] < self.right and self.top <= pos[1] < self.bottom

    def style_add(self, style=None, **kwargs):
        self.style.update(**kwargs)
        if style is not None:
            self.style.update(style)
        self.draw()

    def style_get(self, name, *args, **kwargs):
        if name not in self.style:
            if self.parent is None:
                raise KeyError('Cannot find style to handle request: \'' + name + '\'')
            return self.parent.style_get(name, *args, **kwargs)
        return self.style[name](*args, **kwargs)

    def get_base_state(self):
        return self._x, self._y

    def update_base(self):
        self.base = pygame.Surface(self.size, pygame.SRCALPHA)
        self.base.fill((0, 0, 0, 0))

    def refresh(self):
        current_state = self.get_base_state()
        if self.base_state != current_state:
            self.base_state = current_state
            self.update_base()

    def draw(self):
        self.refresh()
        self.surf = self.base.copy()
        if not all(self.children[i].z <= self.children[i+1].z for i in range(len(self.children) - 1)):
            self.children.sort(key=lambda x: x.z)
        for child in self.children:
            if child.visible:
                child.draw()
        if self.parent is not None:
            self.parent.surf.blit(self.surf, self.pos)

    def update(self):
        pos = pygame.mouse.get_pos()
        if not self.hovered and self.contains(pos):
            rel = pygame.mouse.get_rel()
            self.mouse_enter((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
        elif self.hovered and not self.contains(pos):
            rel = pygame.mouse.get_rel()
            self.mouse_exit((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
        for child in self.children:
            if not child.paused:
                child.update()

    def tick(self):
        self.update()
        self.draw()


class Screen(Entity):
    def __init__(self, *size, **kwargs):
        super().__init__(*size)
        self.screen = pygame.display.set_mode(size, **kwargs)
        self.bg_color = (0, 0, 0)

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

    def get_base_state(self):
        return (self.bg_color, self.screen.get_size()) + super().get_base_state()

    def update_base(self):
        self.base = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.base.fill(self.bg_color)

    def draw(self):
        super().draw()
        self.screen.blit(self.surf, (0, 0))
        pygame.display.update()


class Text(Entity):
    def __init__(self, text='', fontsize=1, fgcolor=None, font=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self.text = text
        self.font = font
        self.fontsize = fontsize
        if font is None:
            self.font = font_loader.get(const.font_default)
        self.fgcolor = fgcolor
        if fgcolor is None:
            self.fgcolor = (0, 0, 0)

    def get_base_state(self):
        return (self.text, self.fontsize, self.font, self.fgcolor) + super().get_base_state()

    def update_base(self):
        self.base = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]


class Image(Entity):
    def __init__(self, filename=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self.image = None
        if filename is not None:
            self.load(filename)

    def load(self, filename):
        try:
            self.image = pygame.image.load(filename).convert_alpha()
        except FileNotFoundError:
            print('Unable to load image:', filename)
            exit()

    def get_base_state(self):
        return (self.image,) + super().get_base_state()

    def update_base(self):
        self.base = self.image


class Hub(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loc_center = None
        self.nodes = dict()
        self.location = None

    def register_node(self, name, child):
        if name in self.nodes:
            raise KeyError('A node with the name ' + name + ' is already registered.')
        self.nodes[name] = child
        child.hide()
        self.register(child)

    def register_center(self, child):
        self.loc_center = child
        if self.location is None:
            self.enter_node(child)
        self.register(child)

    def enter_node(self, child):
        if self.location is not None:
            self.location.hide()
        self.location = child
        self.location.show()

    def handle_message(self, sender, message):
        if message == 'exit' and self.location is not self.loc_center:
            self.enter_node(self.loc_center)
        elif message in self.nodes:
            self.enter_node(self.nodes[message])
        else:
            super().handle_message(sender, message)
