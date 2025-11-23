import random


def coin() -> bool:
    """
    Performs a coin flip: `True` for *heads*, and `False` for *tails*.
    The obligation to indicate and display the result of the flip is on the caller.
    """
    return bool(random.getrandbits(1))
