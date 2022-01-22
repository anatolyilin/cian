import time
from random import randrange
import tqdm

import helpers.logging as logging
from helpers.configuration import app_config

logger = logging.get_logger()
'''cooloff:
  image:
    min: 1
    max: 6
  offer_query:
    min: 30
    max: 300
    '''


def _sleep(min_seconds: int, max_seconds: int = None, animate: bool = True):
    """
    Function to provide a delay in execution
    :param min_seconds: minimum delay [seconds]
    :param max_seconds: maximum delay, when provided a random delay between min and max will be used [seconds]
    :param animate: if True a progress bar will be shown [seconds]
    :return: delay between min_seconds and max_seconds, or min_seconds if max_seconds is not provided
    """
    if max_seconds:
        sleep_time = randrange(min_seconds, max_seconds)
    else:
        sleep_time = min_seconds
    logger.info(f'sleeping for {sleep_time} seconds')
    if animate:
        pbar = tqdm.tqdm(total=sleep_time*2)
        for i in range(sleep_time*2):
            pbar.update(n=1)
            time.sleep(0.5)
    else:
        time.sleep(sleep_time)


class CoolOff:
    """
    Class used to add delay points in the execution of the app.
    """
    def __init__(self, images_min: int = None, images_max: int = None, offers_query_min: int = None,
                 offers_query_max: int = None, progress_bar: bool = True):
        """
        Constructor for the CoolOff class
        :param images_min: minimum delay between image downloading [seconds]
        :param images_max: maximum delay between image downloading [seconds]
        :param offers_query_min: minimum delay between running queries [seconds]
        :param offers_query_max: maximum delay between running queries [seconds]
        :param progress_bar: if True a progress bar will be shown (default: True)
        """
        if not images_max:
            images_max = app_config.get_nested("cooloff.image.max")
        if not images_min:
            images_min = app_config.get_nested("cooloff.image.min")
        if not offers_query_max:
            offers_query_max = app_config.get_nested("cooloff.offer_query.max")
        if not offers_query_min:
            offers_query_min = app_config.get_nested("cooloff.offer_query.min")

        self.time_images_min = images_min
        self.time_images_max = images_max

        self.time_offer_query_min = offers_query_min
        self.time_offer_query_max = offers_query_max

        self.animate = progress_bar

    def stats(self) -> dict:
        return {
            'images_min': self.time_images_min,
            'images_max': self.time_images_max,
            'images_avg': (self.time_images_min + self.time_images_max) / 2,
            'offers_query_min': self.time_offer_query_min,
            'offers_query_max': self.time_offer_query_max,
            'offers_query_avg': (self.time_offer_query_max + self.time_offer_query_min) / 2,
            'progress_bar': self.animate
        }

    def images(self):
        _sleep(self.time_images_min, self.time_images_max, self.animate)

    def offer_queries(self):
        _sleep(self.time_offer_query_min, self.time_offer_query_max, self.animate)