import unittest
from helpers.configuration import app_config
from helpers.logging import get_logger


class TestLoggingHandler(unittest.TestCase):

    def test_get_logger(self):
        app_config.load("test/test_config.yaml")
        logger = get_logger()
        logger.info("test log")

        with self.assertLogs() as cm:
            logger.info('first message')
            logger.error('second message')
            self.assertEqual(cm.output, ['INFO:Cian:first message',
                                         'ERROR:Cian:second message'])


if __name__ == '__main__':
    unittest.main()