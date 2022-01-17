import unittest

from helpers.configuration import app_config
from helpers.logging import get_logger
import helpers.mongodb as mng
import pymongo.errors as errors
from unittest.mock import patch


class TestMongoDBConnection(unittest.TestCase):

    def test_connection_string(self):
        app_config.load("test/test_config.yaml")
        expected_connection_string = "mongodb://testuser:testpwd@127.0.0.1:27017/testDB"
        self.assertEqual(mng._get_connection_string(), expected_connection_string)

    @patch('helpers.mongodb._get_connection_string', return_value="mongodb://testuser:testpwd@127.0.1.5:27017/testDB")
    def test_incorrect_connection(self, _get_connection_string):
        # change timeout to something reasonable
        mng._serverSelectionTimeoutMS = 10

        # test missing collection
        with self.assertRaises(errors.ConnectionFailure):
            mng.getConnection()
        # test connection issue
        with self.assertRaises(errors.ConnectionFailure):
            mng._connect()


if __name__ == '__main__':
    unittest.main()
