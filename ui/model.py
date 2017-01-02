class Subject:
    def __init__(self):
        self.observers = []

        self.parent = None
        self.children = []

        self.state_attrs = tuple()
        self.old_state = None

    def add_observer(self, observer):
        self.observers.append(observer)

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

    def notify_all(self, diff):
        for observer in self.observers:
            observer.notify(self, diff)

    def get_state(self):
        return State(self.state_attrs, tuple(getattr(self, attr) for attr in self.state_attrs))

    def update(self):
        for child in self.children:
            child.update()
        new_state = self.get_state()
        if self.old_state != new_state:
            self.notify_all(StateChange(self.old_state, new_state))
            self.old_state = new_state


class State:
    def __init__(self, attrs, vals):
        self.attrs = attrs
        for attr, val in zip(attrs, vals):
            setattr(self, attr, val)

    def __eq__(self, other):
        return all(attr in dir(other) and getattr(other, attr) == getattr(self, attr) for attr in self.attrs)

    def __str__(self):
        return '{' + ', '.join('{}: {}'.format(attr, getattr(self, attr)) for attr in self.attrs) + '}'


class StateChange:
    def __init__(self, before, after):
        self.before = before
        self.after = after
        for attr in after.attrs:
            setattr(self, attr, before is None or getattr(before, attr) != getattr(after, attr))
