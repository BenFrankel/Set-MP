import pygame

import font_loader
import const


class Entity(pygame.Rect):
    def __init__(self, *args, visible=True, hoverable=True, clickable=True, active=True):
        super().__init__(*args)
        self.parent = None
        self.children = []
        self.active_child = None
        self._surf = pygame.Surface(self.size, pygame.SRCALPHA)
        self.hitbox = None
        self.visible = visible
        self.hoverable = hoverable
        self.clickable = clickable
        self.active = active
        self.bg_color = (0, 0, 0, 0)
        self.z = 0

    @property
    def surf(self):
        return self._surf

    @surf.setter
    def surf(self, other):
        self._surf = other
        self.size = other.get_size()

    def show(self):
        self.visible = True
        self.active = True

    def hide(self):
        self.visible = False
        self.active = False

    def pause(self):
        self.active = False

    def unpause(self):
        self.active = True

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
        if self.active_child is not None:
            self.active_child.key_down(unicode, key, mod)

    def key_up(self, key, mod):
        if self.active_child is not None:
            self.active_child.key_down(key, mod)

    def mouse_motion(self, pos, rel, buttons):
        for child in self.children:
            if child.hoverable and child.active and child.contains(pos):
                child.mouse_motion(pos, rel, buttons)

    def mouse_down(self, pos, button):
        for child in self.children:
            if child.clickable and child.active and child.contains(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_down(rel_pos, button)

    def mouse_up(self, pos, button):
        for child in self.children:
            if child.clickable and child.active and child.contains(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_up(rel_pos, button)

    def contains(self, pos):
        if self.hitbox is not None:
            return self.hitbox.collidepoint(pos)
        return self.collidepoint(pos)

    def pre_draw(self):
        self.surf.fill((0, 0, 0, 0))

    def post_draw(self):
        pass

    def draw(self):
        self.pre_draw()
        if not all(self.children[i].z <= self.children[i+1].z for i in range(len(self.children) - 1)):
            self.children.sort(key=lambda x: x.z)
        for child in self.children:
            if child.visible:
                child.draw()
        self.post_draw()
        if self.parent is not None:
            self.parent.surf.blit(self.surf, self)

    def update(self):
        for child in self.children:
            if child.active:
                child.update()

    def tick(self):
        self.update()
        self.draw()


class StyledEntity(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = dict()

    def add_style(self, style, **kwargs):
        self.style.update(style, **kwargs)

    def style_draw(self, name, *args, **kwargs):
        if name not in self.style:
            if self.parent is None:
                raise KeyError('Cannot find style to handle drawing\'' + name + '\'.')
            return self.parent.style_draw(name, *args, **kwargs)
        return self.style[name](*args, **kwargs)


class Text(Entity):
    def __init__(self, fontsize, text='', font=None, **kwargs):
        super().__init__(0, 0, 0, fontsize, **kwargs)
        self._text = text
        self.font = font
        self.fontsize = fontsize
        if font is None:
            self.font = font_loader.get(const.font_default)
        new_rect = self.font.get_rect(self.text, size=fontsize)
        self.w = new_rect.w
        self.h = new_rect.h

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, other):
        self._text = other
        new_rect = self.font.get_rect(self.text, size=self.fontsize)
        self.w = new_rect.w
        self.h = new_rect.h

    def pre_draw(self):
        self.surf = self.font.render(self.text, size=self.fontsize)[0]


class Image(Entity):
    def __init__(self):
        super().__init__(0, 0, 0, 0, visible=True, hoverable=False, clickable=False, active=False)
        self.loaded = False
        self.image = None

    def load(self, filename):
        try:
            self.image = pygame.image.load(filename).convert_alpha()
        except FileNotFoundError:
            print('Unable to load image:', filename)
            exit()
        self.loaded = True
        return self

    def pre_draw(self):
        if self.loaded:
            self.surf = self.image


class Screen(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(0, 0, 0, 0)
        self.surf = pygame.display.set_mode(*args, **kwargs)
        self.bg_color = (0, 0, 0)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event.unicode, event.key, event.mod)
        elif event.type == pygame.KEYUP:
            self.key_up(event.key, event.mod)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_motion(event.pos, event.rel, event.buttons)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_up(event.pos, event.button)

    def pre_draw(self):
        self.surf.fill(self.bg_color)

    def draw(self):
        super().draw()
        pygame.display.update()


# TODO: class Button
# TODO: class Menu
