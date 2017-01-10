import pygame


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


class Entity(Rect):
    def __init__(self, w, h, x=0, y=0, visible=True, hoverable=True, clickable=True, typable=False, opacity=1):
        super().__init__(x, y, w, h)

        # Heirarchical references.
        self.parent = None
        self._children = []
        self.key_listener = None

        self.z = 0

        # General flags.
        self._visible = visible
        self._hoverable = hoverable
        self._clickable = clickable
        self._typable = typable
        self._opacity = opacity
        self._paused = False
        self._hovered = False

        # Surfaces.
        if self.is_transparent:
            self._colorkey = None
            self._background = None
            self._display = None
        elif self.is_translucent:
            self._colorkey = (0, 0, 0, 0)
            self._background = pygame.Surface(self.size, pygame.SRCALPHA)
            self._display = pygame.Surface(self.size, pygame.SRCALPHA)
        else:  # self.is_opaque
            self._colorkey = (0, 0, 0)
            self._background = pygame.Surface(self.size)
            self._display = pygame.Surface(self.size)
        if self._colorkey is not None:
            self._background.set_colorkey(self.colorkey)
            self._display.set_colorkey(self.colorkey)

        # Dirty Rectangle memory.
        self._dirty = False
        self._dirty_rects = []
        self._dirty_area = 0

        self._old_rect = None
        self._old_visible = None

        # Style.
        self._style = dict()

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_visible(self):
        return self._visible and (self.is_root or self.parent.is_visible)

    @property
    def can_hover(self):
        return self._hoverable and (self.is_root or self.parent.can_hover)

    @property
    def can_click(self):
        return self._clickable and (self.is_root or self.parent.can_click)

    @property
    def can_type(self):
        return self._typable and (self.is_root or self.parent.can_type)

    @property
    def is_paused(self):
        return self._paused or not self.is_root and self.parent.is_paused

    @property
    def is_transparent(self):
        return self._opacity == 0

    @property
    def is_translucent(self):
        return self._opacity == 1

    @property
    def is_opaque(self):
        return self._opacity == 2

    @property
    def is_alive(self):
        return self._visible and not self._paused

    @property
    def dirty(self):
        if self._old_visible is None:
            return self._visible
        return self._dirty or self._old_rect != self or self._old_visible != self._visible

    @dirty.setter
    def dirty(self, other):
        if other and not self.is_root:
            for rect in self._dirty_rects:
                self._clean_dirty_rects(rect)
        self._dirty = other

    @property
    def colorkey(self):
        return self._colorkey

    @colorkey.setter
    def colorkey(self, other):
        if self._colorkey != other:
            self._colorkey = other
            self._background.set_colorkey(other)
            self._display.set_colorkey(other)

    @property
    def background(self):
        return self._background

    @background.setter  # Perhaps find a better solution than this to resizing?
    def background(self, other):
        if self.size != other.get_size():
            if self.is_translucent:
                self._display = pygame.Surface(other.get_size(), pygame.SRCALPHA)
            elif self.is_opaque:
                self._display = pygame.Surface(other.get_size())
        if self._colorkey is not None:
            self._background.set_colorkey(self.colorkey)
            self._display.set_colorkey(self.colorkey)
        self._background = other
        self.size = other.get_size()
        self.dirty = True

    def update_background(self):
        pass

    def resize(self, size):
        if self.size != size:
            self.size = size
            self.update_background()

    def style_add(self, style=None, **kwargs):
        self._style.update(**kwargs)
        if style is not None:
            self._style.update(style)
        self.update_background()
        for child in self._children:
            child.style_add()  # Hack-ish ...

    def style_get(self, name, *args, **kwargs):
        if name not in self._style:
            if self.is_root:
                raise KeyError('Cannot find style to handle request: \'' + name + '\'')
            return self.parent.style_get(name, *args, **kwargs)
        return self._style[name](*args, **kwargs)

    def copy_rect(self):
        return Rect(self.x, self.y, self.w, self.h)

    def rel_rect(self):
        return Rect(0, 0, self.w, self.h)

    def abs_rect(self):
        if self.is_root:
            return self.copy_rect()
        abs_pos = self.parent.abs_rect().pos
        return Rect(abs_pos[0] - self.pos[0], abs_pos[1] - self.pos[1], self.w, self.h)

    def show(self):
        self._visible = True
        self.unpause()

    def hide(self):
        self._visible = False
        self.pause()

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    def register(self, child):
        if not child.is_root:
            child.parent.unregister(child)
        for rect in child._dirty_rects:
            child._clean_dirty_rects(rect)
        child.parent = self
        child.dirty = child._visible
        child.style_add()  # Hack-ish ...
        self._children.append(child)

    def register_all(self, children):
        for child in children:
            self.register(child)

    def unregister(self, child):
        self._children.remove(child)
        child.parent = None
        if child._old_visible and child._old_rect is not None:
            self._add_dirty_rect(child._old_rect)

    def unregister_all(self, children):
        for child in children:
            self.unregister(child)

    def key_down(self, unicode, key, mod):
        if self.key_listener is not None and self.key_listener.is_alive:
            self.key_listener.key_down(unicode, key, mod)

    def key_up(self, key, mod):
        if self.key_listener is not None and self.key_listener.is_alive:
            self.key_listener.key_up(key, mod)

    def mouse_enter(self, start, end, buttons):
        for child in self._children:
            if child._hoverable and child.is_alive and child.collide_point(end):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_enter(rel_start, rel_end, buttons)

    def mouse_exit(self, start, end, buttons):
        for child in self._children:
            if child._hoverable and child.is_alive and child.collide_point(start):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_exit(rel_start, rel_end, buttons)

    def mouse_motion(self, start, end, buttons):
        for child in self._children:
            if child._hoverable and child.is_alive and child.collide_point(start) and child.collide_point(end):
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child.mouse_motion(rel_start, rel_end, buttons)

    def mouse_down(self, pos, button):
        for child in self._children[::-1]:
            if child._clickable and child.is_alive and child.collide_point(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                if child._typable:
                    self.key_listener = child
                child.mouse_down(rel_pos, button)

    def mouse_up(self, pos, button):
        for child in self._children:
            if child._clickable and child.is_alive and child.collide_point(pos):
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child.mouse_up(rel_pos, button)

    def handle_message(self, sender, message):
        self.send_message(message)

    def send_message(self, message):
        if not self.is_root:
            self.parent.handle_message(self, message)

    def _add_dirty_rect(self, rect):
        if not self.dirty and rect not in self._dirty_rects:
            area = rect.area()
            if area + self._dirty_area > self.area():
                self.dirty = True
                self._dirty_area += area
            else:
                self._dirty_rects.append(rect)
                if not self.is_root:
                    self.parent._add_dirty_rect(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def _clean_dirty_rects(self, rect):
        self._dirty_rects.remove(rect)
        self._dirty_area -= rect.area()
        if not self.is_root:
            self.parent._clean_dirty_rects(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def _transition_rects(self):
        if self._old_visible and self._visible:
            old = self._old_rect
            comb = Rect(min(self.x, old.x), min(self.y, old.y))
            comb.w = max(self.right, old.right) - comb.x
            comb.h = max(self.bottom, old.bottom) - comb.y
            if self.area() + old.area() > comb.area():
                return [comb]
            else:
                return [self._old_rect, self.copy_rect()]
        elif self._old_visible:
            return [self._old_rect]
        elif self._visible:
            return [self.copy_rect()]
        return []

    def _refresh(self, rect):
        children = self._children[:]
        self._display.fill(self.colorkey, rect.as_pygame_rect())
        self._display.blit(self._background, rect.pos, rect.as_pygame_rect())
        for child in children:
            if child._visible:
                if child.is_transparent:
                    children.extend(child._children)
                else:
                    area = rect.intersect(child)
                    if area is not None:
                        area.x -= child.x
                        area.y -= child.y
                        self._display.blit(child._display, (child.x + area.x, child.y + area.y), area.as_pygame_rect())

    def _draw(self):
        if self._visible:
            for child in self._children:
                if not child.is_transparent and child.dirty and not self.dirty:
                    for rect in child._transition_rects():
                        self._add_dirty_rect(rect)
                if child._visible or child._old_visible:
                    child._draw()
            if not self.is_transparent:
                if self.dirty:
                    self._refresh(self.rel_rect())
                else:
                    for rect in self._dirty_rects:
                        self._refresh(rect)
        changed = self.dirty or bool(self._dirty_rects)
        self.dirty = False
        self._dirty_rects = []
        self._old_rect = self.copy_rect()
        self._old_visible = self._visible
        return changed

    def track(self):
        pass

    def _track(self):  # Necessary because important mouse events may be lost due to quick movement.
        self.track()
        pos = pygame.mouse.get_pos()
        if not self.is_root:
            pos = tuple(x1 - x2 for x1, x2 in zip(pos, self.parent.abs_rect().pos))
        if self._hovered != self.collide_point(pos):
            rel = pygame.mouse.get_rel()
            self._hovered = not self._hovered
            if self._hovered:
                self.mouse_enter((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
            else:
                self.mouse_exit((pos[0] - rel[0], pos[1] - rel[1]), pos, pygame.mouse.get_pressed())
        for child in self._children:
            if child.is_alive:
                child._track()

    def update(self):
        pass

    def _update(self):
        self.update()
        for child in self._children:
            if child.is_alive:
                child._update()
        if not all(self._children[i].z <= self._children[i+1].z for i in range(len(self._children) - 1)):
            self._children.sort(key=lambda x: x.z)
            self.dirty = True

    def tick(self):
        self._track()
        self._update()
        self._draw()


class Window(Entity):
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


class Hub(Entity):
    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, typable=True, opacity=0, **kwargs)
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
        if self.location is not child:
            if self.location is not None:
                self.location.hide()
            self.location = child
            child.show()
            if child._typable:
                self.key_listener = child
            else:
                self.key_listener = None

    def handle_message(self, sender, message):
        if message == 'exit' and self.location is not self.loc_center:
            self.enter_node(self.loc_center)
        elif message in self.nodes:
            self.enter_node(self.nodes[message])
        else:
            super().handle_message(sender, message)
