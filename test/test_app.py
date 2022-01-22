# import unittest
# import pickle
# import json
# from unittest import mock
# from unittest.mock import patch
#
# import helpers.logging as logging
# from helpers.cooloff import CoolOff
# from helpers.mongohandler import MongoHandler
# from helpers.datahandling import DataHandler
# from helpers.configuration import app_config
# import app
#
# logger = logging.get_logger()
# app_config.load("test_config.yaml")
#
# class TestConfig(unittest.TestCase):
#
#     @patch('app.sleep', CoolOff())
#     def test_process_request(self):
#         # load test processing request
#         app_config.load("test_config.yaml")
#
#         mongo_handler = MongoHandler()
#         data_handler = DataHandler(mongo_handler)
#         with open("../data/failed/failed_1642692193.1254342.pickle", 'rb') as f:
#             cian_response = pickle.load(f)
#
#         with mock.patch('app.pickle') as mocked_pickle:
#             app.process_request(cian_response, data_handler)
#             mocked_pickle.dump.assert_called_once()
#
#
#
#         # with patch('pickle.dump') as mock_requests:
#         #     mock_requests.get.side_effect = Timeout
#         #     with self.assertRaises(Timeout):
#         #         learn_unittest_mock.learn_mock.get_holidays()
#         #
#             # mock_requests.get.asser_called_once()
#             # with open("../data/failed/failed_1642692193.1254342.pickle", 'rb') as f:
#             #     cian_response = pickle.load(f)
#         #
#         #     data_handler = MongoHandler()
#         #
#         #     app.process_request(cian_response, data_handler)
#         #
#         #     pass
