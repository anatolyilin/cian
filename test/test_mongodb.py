import unittest
import pickle

from helpers.configuration import app_config
from helpers.logging import get_logger
import helpers.mongodb as mng
import pymongo.errors as errors
from unittest.mock import patch


class TestMongoDBConnection(unittest.TestCase):

    def test_connection_string(self):
        app_config.load("test_config.yaml")
        expected_connection_string = "mongodb://testuser:testpwd@127.0.0.1:27017/testDB"
        self.assertEqual(mng._get_connection_string(), expected_connection_string)

    @patch('helpers.mongodb._get_connection_string', return_value="mongodb://testuser:testpwd@127.0.1.5:27017/testDB")
    def test_incorrect_connection(self, _get_connection_string):
        # change timeout to something reasonable
        mng._serverSelectionTimeoutMS = 10

        # test missing collection
        with self.assertRaises(errors.ConnectionFailure):
            mng.getCollection()
        # test connection issue
        with self.assertRaises(errors.ConnectionFailure):
            mng._connect()

    def test_changing_collection(self):
        app_config.load("test_config.yaml")
        self.assertEqual(mng.getCollection('testMetadata').name, 'testMetadata')
        self.assertEqual(mng.getCollection('nonExistingCollection').name, 'nonExistingCollection')
        self.assertNotEqual(mng.getCollection('nonExistingCollection').name, 'testMetadata')

    def test_write_read(self):
        app_config.load("test_config.yaml")
        records = mng.getCollection('testMetadata')
        records.delete_many({})

        with open("data/metadata.pickle", 'rb') as f:
            data = pickle.load(f)

        records.insert_one(data)
        cursor = records.find({'searchUuid': "97b010fa-7549-11ec-985c-8a30644c8079"})

        print(data, cursor[0])
        self.assertEqual(1, len(list(cursor)))
        records.delete_many({})


if __name__ == '__main__':
    unittest.main()
