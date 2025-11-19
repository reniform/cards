import random

def coin() -> bool:
    return bool(random.getrandbits(1))