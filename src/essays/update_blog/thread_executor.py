from functools import wraps
from queue import Queue
from threading import Thread


class ThreadExecutor:
    def __init__(self, threads: list[Thread], max_executors: int = 3) -> None:
        self.done_threads = Queue()

        self.threads = [self.decorate_thread(thread)
                        for thread in threads]

        self.max_executors = max_executors

    def decorate_thread(self, ori_thread: Thread) -> Thread:
        target = ori_thread._target
        ori_thread._target = self.queue_when_done(target)

        return ori_thread

    def execute(self):
        max_executors = min(len(self.threads), self.max_executors)
        threads = self.threads

        # Inicializo todos los hilos
        for _ in range(max_executors):
            threads.pop().start()

        while self.done_threads.get() is not None:
            if not threads:
                continue
            # No inicializo otro hilo hasta que se haya terminado otro
            threads.pop().start()
            # Si he acabado los hilos, añado un indicativo de que la Queue se ha acabado
            if not threads:
                self.done_threads.put(None)

        # Espero a que estén todos acabados
        for thread in self.threads:
            thread.join()


    def queue_when_done(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ans = fn(*args, **kwargs)
            self.done_threads.put(True)
            return ans
        return wrapper