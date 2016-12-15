import pygame


# TODO: Z-value for children.
# TODO: Hitbox and custom contains().
class Entity(pygame.Rect):
    def __init__(self, *args, visible=True, hoverable=True, clickable=True, active=True):
        super().__init__(*args)
        self.parent = None
        self.children = []
        self.active_child = None
        self._surf = pygame.Surface(self.size, pygame.SRCALPHA)
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

    def key_down(self, event):
        if self.active_child is not None:
            self.active_child.key_down(event)

    def key_up(self, event):
        if self.active_child is not None:
            self.active_child.key_down(event)

    def hover(self, event):
        for child in self.children:
            if child.hoverable and child.active and child.collidepoint(event.pos):
                child.hover(event)

    def mouse_down(self, event):
        for child in self.children:
            if child.clickable and child.active and child.collidepoint(event.pos):
                rel_pos = (event.pos[0] - child.x, event.pos[1] - child.y)
                rel_event = pygame.event.Event(event.type, pos=rel_pos, button=event.button)
                child.mouse_down(rel_event)

    def mouse_up(self, event):
        for child in self.children:
            if child.clickable and child.active and child.collidepoint(event.pos):
                rel_pos = (event.pos[0] - child.x, event.pos[1] - child.y)
                rel_event = pygame.event.Event(event.type, pos=rel_pos, button=event.button)
                child.mouse_up(rel_event)

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
        self.style = None

    def set_style(self, style):
        self.style = style
        for child in self.children:
            child.set_style(style)

    def register(self, child):
        child.set_style(self.style)
        super().register(child)

    def unregister(self, child):
        child.set_style(None)
        super().unregister(child)


class Image(Entity):
    def __init__(self):
        super().__init__(0, 0, 0, 0, visible=False, hoverable=False, clickable=False, active=False)
        self.loaded = False
        self.image = None

    def load(self, filename):
        try:
            self.surf = self.image = pygame.image.load(filename).convert_alpha()
        except:
            print('Unable to load image:', filename)
            exit()
        self.loaded = True
        return self

    def pre_draw(self):
        self.surf = self.image

    def show(self):
        if self.loaded:
            super().show()


class Screen(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(0, 0, 0, 0)
        self.surf = pygame.display.set_mode(*args, **kwargs)
        self.bg_color = (0, 0, 0)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event)
        elif event.type == pygame.KEYUP:
            self.key_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self.hover(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_up(event)

    def pre_draw(self):
        self.surf.fill(self.bg_color)

    def draw(self):
        super().draw()
        pygame.display.update()


# TODO: class Button
# TODO: class Menu

