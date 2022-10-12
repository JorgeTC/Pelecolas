
from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from multiprocessing import Lock
from threading import current_thread, main_thread




class Priority(int, Enum):
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class ConsoleEvent:
    __metaclass__ = ABCMeta

    def __init__(self, priority: Priority = Priority.LOW) -> None:
        self.priority = priority

        # Bloqueo el locker hasta haber completado la tarea
        self.locker = Lock()
        self.locker.acquire()

    @abstractmethod
    def execute(self):
        pass

    def execute_if_main_thread(self):
        # Si estoy en el hilo principal, lo ejecuto
        if current_thread() is main_thread():
            self.execute()
        else:
            from src.gui.gui import GUI
            GUI.add_event(current_thread(), self)
