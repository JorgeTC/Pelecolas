from functools import update_wrapper
from threading import Lock
from typing import Any, Callable, TypeVar


class thread_safe_cache:
    RT = TypeVar('RT')

    def __init__(self, fun: Callable[[Any], RT]):
        self.val_cached = None
        self.locker = Lock()
        self.fun = fun
        update_wrapper(self, fun)

    def __call__(self, *args, **kwarg) -> RT:

        # Si el valor ya se ha calculado lo devuelvo
        if self.val_cached is not None:
            return self.val_cached

        with self.locker:
            if self.val_cached is None:
                self.val_cached = self.fun(*args, **kwarg)
        return self.val_cached
