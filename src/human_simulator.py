import threading

class HumanSimulator():

    def __init__(self, title) -> None:
        self.curr_title = title

        threading.Event()
        pass

    def ans_title(self, event):

