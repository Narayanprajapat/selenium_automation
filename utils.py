import time
import random


def wait_between(lower=1, upper=2):
    """
    Max Time :upper
    """
    if upper < lower:
        raise ValueError
    random_num = random.randint(lower, upper)
    time.sleep(random_num)
    return random_num
