import functools

def debug(func):
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        print(func.__name__, args, kwargs)
        return func(*args, **kwargs)
    return wrapper_debug