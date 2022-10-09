from functools import wraps
from threading import Lock


def cach(fun):

    val_cached = None
    locker = Lock()

    @wraps(fun)
    def get_value(*args, **kwarg):
        nonlocal val_cached
        # Si el valor ya se ha calculado lo devuelvo
        if val_cached is not None:
            return val_cached

        with locker:
            if val_cached is None:
                val_cached = fun(*args, **kwarg)
        return val_cached
    return get_value
