import datetime
import sys

from src.aux_console import clear_current_line


class Timer():
    def __init__(self):
        self.start = datetime.datetime.now()

    def remains(self, done: float) -> str:
        if done != 0:
            now = datetime.datetime.now()
            left = (1 - done) * (now - self.start) / done
            sec = int(left.total_seconds())
            if sec < 60:
                return "{} seconds".format(sec)
            else:
                return "{} minutes".format(int(sec / 60))

    def reset(self) -> None:
        self.start = datetime.datetime.now()


class ProgressBar():
    def __init__(self):
        self.__timer = Timer()
        self.barLength = 20
        self.progress = 0.0

    def update(self, done):
        self.progress = float(done)
        block = int(round(self.barLength * self.progress))
        clear_current_line()
        text = "[{0}] {1:.2f}% {2}".format( "="*block + " "*(self. barLength-block), self. progress*100, self.__timer.remains(self.progress))
        sys.stdout.write(text)
        sys.stdout.flush()

    def reset_timer(self):
        self.__timer.reset()
