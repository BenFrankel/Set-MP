import pygame

import font_loader
import const
import time


# TODO: Logical Entity, Concrete Entity.
# TODO: Maybe move Image and Text into a different file. Let this be the structural layout file.
class Rect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def size(self):
        return self._w, self._h

    @size.setter
    def size(self, other):
        self._w, self._h = other

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

    def area(self):
        return self.w * self.h

    def collide_point(self, point):
        return self.left <= point[0] < self.right and self.top <= point[1] < self.bottom

    def collide_rect(self, rect):
        return self.left < rect.right and rect.left < self.right and self.top < rect.bottom and rect.top < self.bottom

    def intersect(self, rect):
        result = Rect(max(self.x, rect.x), max(self.y, rect.y))
        result.w = min(self.right, rect.right) - result.x
        result.h = min(self.bottom, rect.bottom) - result.y
        if result.w < 0 or result.h < 0:
            return None
        return result

    def as_pygame_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

    def __str__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.x, self.y, self.w, self.h)

    __repr__ = __str__


# ? Entity proxy that creates itself when show() and deletes itself when hide()
class Entity(Rect):
    def __init__(self, w, h, x=0, y=0, visible=True, hoverable=True, clickable=True):
        super().__init__(x, y, w, h)

        self.z = 0

        self._visible = visible
        self.hoverable = hoverable
        self.clickable = clickable
        self.paused = False

        self.hovered = False

        self._dirty = True
        self.dirty_rects = []

        self.parent = None
        self.children = []
        self.key_listener = None

        self.current_state = None
        self._background = pygame.Surface(self.size, pygame.SRCALPHA)
        self.display = pygame.Surface(self.size, pygame.SRCALPHA)

        self.hitbox = None

        self.style = dict()

        self.old_rect = self.copy_rect()  # None?

    @property
    def background(self):
        return self._background

    @background.setter  # Perhaps find a better solution than this to resizing?
    def background(self, other):
        if self.size != other.get_size():
            self.display = pygame.Surface(other.get_size(), pygame.SRCALPHA)
        self._background = other
        self.size = other.get_size()
        self.dirty = True

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, other):
        if self._visible != other:
            self.dirty = True
        self._visible = other

    @property
    def dirty(self):
        return self._dirty or self.old_rect != self

    @dirty.setter
    def dirty(self, other):
        if other and not self._dirty:
            self.clean_dirty_rects()
        self._dirty = other

    def resize(self, size):
        before = self.size
        self.size = size
        if before != size:
            self.update_background()

    def copy_rect(self):
        return Rect(self.x, self.y, self.w, self.h)

    def rel_rect(self):
        return Rect(0, 0, self.w, self.h)

    def abs_rect(self):
        if self.parent is None:
            return self.copy_rect()
        return Rect(*(x1 + x2 for x1, x2 in zip(self.parent.abs_rect().pos, self.pos)), self.w, self.h)

    def show(self):
        if not self.visible:
            self.old_rect = self.copy_rect()
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
        child.style_add()  # Hack-ish ...

    def register_all(self, children):
        for child in children:
            self.register(child)

    def unregister(self, child):
        self.children.remove(child)
        child.parent = None
        self.add_dirty_rect(child.copy_rect())  # TODO: What if it moved? Should be old rect.

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
            if child.hoverable and not child.paused and child.collide_point(end):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_enter(rel_start, rel_end, buttons)

    def mouse_exit(self, start, end, buttons):
        for child in self.children:
            if child.hoverable and not child.paused and child.collide_point(start):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_exit(rel_start, rel_end, buttons)

    def mouse_motion(self, start, end, buttons):
        for child in self.children:
            if child.hoverable and not child.paused and child.collide_point(start) and child.collide_point(end):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_motion(rel_start, rel_end, buttons)

    def mouse_down(self, pos, button):
        for child in self.children:
            if child.clickable and not child.paused and child.collide_point(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_down(rel_pos, button)

    def mouse_up(self, pos, button):
        for child in self.children:
            if child.clickable and not child.paused and child.collide_point(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_up(rel_pos, button)

    def handle_message(self, sender, message):
        self.send_message(message)

    def send_message(self, message):
        if self.parent is not None:
            self.parent.handle_message(self, message)

    def collide_point(self, point):
        if self.hitbox is not None:
            return self.hitbox.collide_point(point)
        return super().collide_point(point)

    def style_add(self, style=None, **kwargs):
        self.style.update(**kwargs)
        if style is not None:
            self.style.update(style)
        self.update_background()
        for child in self.children:
            child.style_add()  # Hack-ish ...

    def style_get(self, name, *args, **kwargs):
        if name not in self.style:
            if self.parent is None:
                raise KeyError('Cannot find style to handle request: \'' + name + '\'')
            return self.parent.style_get(name, *args, **kwargs)
        return self.style[name](*args, **kwargs)

    def add_dirty_rect(self, rect):
        if not self.dirty and rect not in self.dirty_rects:
            if rect.area() + sum(r.area() for r in self.dirty_rects) > self.area():
                self.dirty = True
            else:
                self.dirty_rects.append(rect)
                if self.parent is not None:
                    self.parent.add_dirty_rect(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def clean_dirty_rect(self, rect):
        self.dirty_rects.remove(rect)
        if self.parent is not None:
            self.parent.clean_dirty_rect(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def clean_dirty_rects(self):
        if self.parent is not None:
            for rect in self.dirty_rects:
                self.parent.clean_dirty_rect(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))
        self.dirty_rects.clear()

    def refresh(self, rect):
        # print(self, 'refresh', rect)
        self.display.fill((0, 0, 0, 0), rect.as_pygame_rect(), pygame.BLEND_RGBA_MIN)
        self.display.blit(self.background, rect.pos, rect.as_pygame_rect())
        for child in self.children:
            if child.visible:
                area = rect.intersect(child)
                if area is not None:
                    area.x -= child.x
                    area.y -= child.y
                    self.display.blit(child.display, (child.x + area.x, child.y + area.y), area.as_pygame_rect())

    def draw(self):
        for child in self.children:
            if child.dirty and not self.dirty:
                old = child.old_rect
                comb = Rect(min(child.x, old.x), min(child.y, old.y))
                comb.w = max(child.right, old.right) - comb.x
                comb.h = max(child.bottom, old.bottom) - comb.y
                if child.area() + old.area() > comb.area():
                    self.add_dirty_rect(comb)
                else:
                    self.add_dirty_rect(child.copy_rect())
                    self.add_dirty_rect(old)
            child.draw()
        for rect in self.dirty_rects:
            self.refresh(rect)
        if self.dirty:
            self.refresh(self.rel_rect())
        changed = self.dirty or bool(self.dirty_rects)
        self.dirty = False
        self.dirty_rects.clear()
        self.old_rect = self.copy_rect()
        return changed

    def update_background(self):
        pass

    def track(self):  # Necessary because important mouse events may be lost due to quick movement.
        pos = pygame.mouse.get_pos()
        if self.parent is not None:
            pos = tuple(x1 - x2 for x1, x2 in zip(pos, self.parent.abs_rect().pos))
        if self.hovered != self.collide_point(pos):
            rel = pygame.mouse.get_rel()
            self.hovered = not self.hovered
            if self.hovered:
                self.mouse_enter((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
            else:
                self.mouse_exit((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
        for child in self.children:
            child.track()

    def update(self):
        for child in self.children:
            if not child.paused:
                child.update()
        if not all(self.children[i].z <= self.children[i+1].z for i in range(len(self.children) - 1)):
            self.children.sort(key=lambda x: x.z)
            self.dirty = True

    def tick(self):
        self.track()
        self.update()
        self.draw()


class Screen(Entity):
    def __init__(self, *args, **kwargs):
        self.screen = pygame.display.set_mode(*args, **kwargs)
        super().__init__(*self.screen.get_size(), **kwargs)

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

    def draw(self):
        if super().draw():
            self.screen.blit(self.display, (0, 0))
            pygame.display.update()


class Text(Entity):
    def __init__(self, text='', fontsize=1, fgcolor=None, font=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._text = text
        self._font = font
        self._fontsize = fontsize
        if font is None:
            self._font = font_loader.get(const.font_default)
        self.fgcolor = fgcolor
        if fgcolor is None:
            self.fgcolor = (0, 0, 0)
        self.update_background()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, other):
        before = self.text
        self._text = other
        if before != other:
            self.update_background()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, other):
        before = self.font
        self._font = other
        if before != other:
            self.update_background()

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, other):
        before = self.fontsize
        self._fontsize = other
        if before != other:
            self.update_background()

    def update_background(self):
        self.background = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]


class Image(Entity):
    def __init__(self, filename=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._image = None
        if filename is not None:
            self.load(filename)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, other):
        self.image = other
        self.background = self.image

    def load(self, filename):
        try:
            self.image = pygame.image.load(filename).convert_alpha()
        except FileNotFoundError:
            print('Unable to load image:', filename)
            exit()


class Hub(Entity):
    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, **kwargs)
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
