import tqdm
import time
from random import randrange


def _sleep(min_seconds: int, max_seconds: int = None):
    if max_seconds:
        sleep_time = randrange(min_seconds, max_seconds)
    else:
        sleep_time = min_seconds
    print(f'sleeping for {sleep_time} seconds')
    pbar = tqdm.tqdm(total=sleep_time*2)
    for i in range(sleep_time*2):
        pbar.update(n=1)
        time.sleep(0.5)


_sleep(5)