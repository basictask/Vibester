"""
Decorators implementation used across the software
"""
from functools import wraps
from typing import Any, Callable


def robust(f: Callable) -> Callable:
    """
    Robust wrapper function that tries to execute a function and if there is an exception
    it will print it, then continue executing.
    """
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error in {f.__name__}(args={args}, kwargs={kwargs})\n{e}")
            return None
    return wrapper
