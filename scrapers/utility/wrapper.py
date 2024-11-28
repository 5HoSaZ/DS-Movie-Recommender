import threading
from typing import Callable


def data_fallback(fallback=None):
    """Wrapper for data extraction fallback."""

    def data_wrapper(func: Callable):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return fallback

        return inner

    return data_wrapper


def threaded(func: Callable):
    """Wrapper for multi-threading."""

    def inner(*args, **kwargs):
        return threading.Thread(target=func, args=args, kwargs=kwargs)

    return inner
