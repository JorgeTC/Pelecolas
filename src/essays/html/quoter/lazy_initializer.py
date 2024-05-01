from threading import Thread, Lock
from typing import Callable, Any, TypeVar


StoredValue = TypeVar('StoredValue')
class LazyInitializer:

    def __init__(self, initializer: Callable[[Any], StoredValue]):
        self.initializing_lock = Lock()
        self.initializing_lock.acquire()

        self.value: StoredValue = None

        self.initializer: Callable[[Any], StoredValue] = initializer

        Thread(target=self.initialize,
               name=self.initializer.__name__).start()

    def initialize(self):
        self.value = self.initializer()
        self.initializing_lock.release()

    def get(self) -> StoredValue:
        with self.initializing_lock:
            return self.value
