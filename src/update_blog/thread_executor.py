from functools import wraps
from queue import Queue
from threading import Thread


class ThreadExecutor:
    def __init__(self, threads: list[Thread], max_executors: int = 3) -> None:
        self.q = Queue()

        self.threads = [self.decorate_thread(thread)
                        for thread in threads]

        self.max_executors = max_executors

    def decorate_thread(self, ori_thread: Thread) -> Thread:
        target = ori_thread._target
        target_decorated = self.queue_when_done(target)
        args = ori_thread._args
        kwargs = ori_thread._kwargs
        name = ori_thread._name

        return Thread(name=name,
                      args=args,
                      kwargs=kwargs,
                      target=target_decorated)

    def execute(self):
        max_executors = min(len(self.threads), self.max_executors)
        threads = self.threads

        # Inicializo todos los hilos
        for _ in range(max_executors):
            threads.pop().start()

        while self.q.get() is not None:
            if not threads:
                continue
            # No inicializo otro hilo hasta que se haya terminado otro
            threads.pop().start()
            # Si he acabado los hilos, añado un indicativo de que la Queue se ha acabado
            if not threads:
                self.q.put(None)

        # Espero a que estén todos acabados
        for thread in self.threads:
            thread.join()


    def queue_when_done(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ans = fn(*args, **kwargs)
            self.q.put(True)
            return ans
        return wrapper
