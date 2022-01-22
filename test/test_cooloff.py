from unittest import TestCase
from helpers.cooloff import CoolOff
from helpers.cooloff import _sleep
from helpers.configuration import app_config
import time


class TestCoolOff(TestCase):

    def test_defaults(self):
        app_config.load('test_config.yaml')
        cooloff = CoolOff()
        settings = cooloff.stats()
        expected_settings = {'images_min': 1,
                             'images_max': 6,
                             'images_avg': 3.5,
                             'offers_query_avg': 165.0,
                             'offers_query_min': 30,
                             'offers_query_max': 300}
        self.assertEqual(settings, expected_settings)

    def test_images(self):
        cooloff = CoolOff(images_min=1, images_max=3)
        start = time.time()
        cooloff.images()
        end = time.time()
        duration = round(end - start)
        self.assertTrue(duration < 3)
        self.assertTrue(duration >= 1)

    def test_offer_queries(self):
        cooloff = CoolOff(offers_query_min=1, offers_query_max=3)
        start = time.time()
        cooloff.offer_queries()
        end = time.time()
        duration = round(end - start)
        self.assertTrue(duration < 3)
        self.assertTrue(duration >= 1)

    def test_sleep(self):
        expected_sleep = 2
        start = time.time()
        _sleep(expected_sleep)
        end = time.time()
        duration = round(end - start)
        self.assertEqual(expected_sleep, duration)

    def test_disable_progress_bar(self):
        cooloff = CoolOff(offers_query_min=1, offers_query_max=3, progress_bar=False)
        start = time.time()
        cooloff.offer_queries()
        end = time.time()
        duration = round(end - start)
        self.assertTrue(duration < 3)
        self.assertTrue(duration >= 1)
