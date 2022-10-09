from functools import wraps
from threading import Lock


def cach(fun):

    val_cached = [None]
    locker = Lock()

    @wraps(fun)
    def get_value(*args, **kwarg):
        # Si el valor ya se ha calculado lo devuelvo
        if val_cached[0] is not None:
            return val_cached[0]

        with locker:
            if val_cached[0] is None:
                #print(f"Calling {fun.__name__}")
                val_cached[0] = fun(*args, **kwarg)
        return val_cached[0]
    return get_value

