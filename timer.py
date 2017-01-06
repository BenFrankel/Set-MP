import time
import functools


# TODO: Does this handle negatives properly?
@functools.total_ordering
class Time:
    def __init__(self, d=0, h=0, m=0, s=0, ms=0):
        self._d = 0
        self._h = 0
        self._m = 0
        self._s = 0
        self._ms = 0
        self.d += d
        self.h += h
        self.m += m
        self.s += s
        self.ms += ms

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self, days):
        self._d = int(days)
        h = (days % 1) * 24
        if h != 0:
            self.h += h

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, hours):
        self._h = int(hours % 24)
        m = (hours % 1) * 60
        if m != 0:
            self.m += m
        d = hours // 24
        if d != 0:
            self.d += d

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self, minutes):
        self._m = int(minutes % 60)
        s = (minutes % 1) * 60
        if s != 0:
            self.s += s
        h = minutes // 60
        if h != 0:
            self.h += h

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, seconds):
        self._s = int(seconds % 60)
        ms = (seconds % 1) * 1000
        if ms != 0:
            self.ms += ms
        m = seconds // 60
        if m != 0:
            self.m += m

    @property
    def ms(self):
        return self._ms

    @ms.setter
    def ms(self, milliseconds):
        self._ms = int(milliseconds % 1000)
        s = milliseconds // 1000
        if s != 0:
            self.s += s

    def in_d(self):
        return self.in_h() / 24

    def in_h(self):
        return self.in_m() / 60

    def in_m(self):
        return self.in_s() / 60

    def in_s(self):
        return self.in_ms() / 1000

    def in_ms(self):
        return self.ms + 1000 * (self.s + 60 * (self.m + 60 * (self.h + 24 * self.d)))

    def __add__(self, other):
        return Time(self.d + other.d, self.h + other.h, self.m + other.m, self.s + other.s, self.ms + other.ms)

    def __sub__(self, other):
        return Time(self.d - other.d, self.h - other.h, self.m - other.m, self.s - other.s, self.ms - other.ms)

    def __lt__(self, other):
        return (self.d, self.h, self.m, self.s, self.ms) < (other.d, other.h, other.m, other.s, other.ms)

    def __gt__(self, other):
        return (self.d, self.h, self.m, self.s, self.ms) > (other.d, other.h, other.m, other.s, other.ms)

    def __str__(self):
        d = ''
        h = ''
        m = ''
        if self >= Time(m=1):
            s = '{:02d}'.format(self.s)
        else:
            s = '{:d}'.format(self.s)
        if self.ms >= 1:
            s += '.{:03d}'.format(self.ms)
        if self >= Time(d=1):
            d = '{:d} '.format(self.d)
            d += 'day'
            if self.d != 1:
                d += 's'
            d += ', '
            h += '{:02d}:'.format(self.h)
            m += '{:02d}:'.format(self.m)
        elif self >= Time(h=1):
            h += '{:d}:'.format(self.h)
            m += '{:02d}:'.format(self.m)
        elif self >= Time(m=1):
            m += '{:d}:'.format(self.m)
        return d + h + m + s


class Timer:
    def __init__(self):
        self.last_time = None
        self._time = Time()
        self.running = False

    @property
    def time(self):
        if not self.running:
            return self._time
        self.update()
        return self._time

    @time.setter
    def time(self, other):
        self._time = other

    def start(self, start_time=Time()):
        self.time = start_time
        self.last_time = Time(s=time.monotonic())
        self.running = True

    def update(self):
        if self.running:
            current_time = Time(s=time.monotonic())
            self._time += current_time - self.last_time
            self.last_time = current_time

    def pause(self):
        self.update()
        self.running = False

    def unpause(self):
        self.last_time = Time(s=time.monotonic())
        self.running = True

    def reset(self):
        self.last_time = None
        self.time = Time()
        self.running = False

    def restart(self):
        self.reset()
        self.start()

    def __eq__(self, other):
        return self.time == other.time and self.running == other.running


class CountdownTimer(Timer):
    def __init__(self):
        super().__init__()

    def update(self):
        if self.running:
            current_time = Time(s=time.monotonic())
            self._time -= current_time - self.last_time
            self.last_time = current_time
            if self._time < Time():
                self.reset()
