import time


# TODO: Count down from X, stopping at 0
# TODO: Count up from X
# TODO: Pause/continue timer
# TODO:
class Timer:
    def __init__(self, period=None, mode='pulse'):
        self.temp_period = None
        self.period = period
        self.mode = mode
        self.last_time = time.time()
        self.curr_time = time.time()
        self.active = False



    def check(self):
        pass

    def reset(self, period=None):
        pass
