from unittest import TestCase
from helpers.persistance.mongohandler import MongoHandler
from helpers.diffhandler import _process_diff
import helpers.persistance.mongodb as database
import pickle
import deepdiff
import helpers.request as cian
from helpers.configuration import app_config


class TestMongoHandler(TestCase):

    @classmethod
    def setUpClass(cls):
        app_config.load("test/test_config.yaml")
        cls._handler = MongoHandler()
        cls.collectionName = 'testCollection'
        cls.collection = database.getCollection(cls.collectionName)
        cls.collection.delete_many({})

    def test_exists(self):
        self.assertTrue(self._handler.exists('testCollection'))
        self.assertFalse(self._handler.exists('nonExistingCollection'))

    def test_id_exists_in(self):
        collection = self.collection
        data = {
            1211755740: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755740-1.jpg',
            1211755738: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755738-1.jpg'
        }
        self._handler.store_images(images=data, location=self.collectionName)
        self.assertTrue(self._handler._id_exists_in(1211755740, self.collectionName))
        self.assertFalse(self._handler._id_exists_in(99, self.collectionName))

    def test_store_metadata(self):
        with open("test/data/metadata.pickle", 'rb') as f:
            data = pickle.load(f)

        collection = self.collection

        self._handler.store_metadata(data, self.collectionName)
        cursor = collection.find({'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"})

        self.assertEqual(1, len(list(cursor)))
        collection.delete_many({})

        self._handler.store_metadata(data, self.collectionName)
        self._handler.store_metadata(data, self.collectionName)

        cursor = collection.find({'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"})

        self.assertEqual(1, len(list(cursor)))
        collection.delete_many({})

        old_data = {"_id": "123", "some": "data"}
        collection.insert_one(old_data)
        self._handler.store_metadata(data, self.collectionName)

        ids = collection.find().distinct('_id')
        self.assertEqual(2, len(ids))
        self.assertEqual(["123", "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"], ids)

        collection.delete_many({})

    def test_get_known_image_ids(self):
        collection = self.collection

        old_data = [{"_id": 123, "image": "someimage"},
                    {"_id": 124, "image": "someotherimage"}]
        collection.insert_many(old_data)

        ids = self._handler.get_known_image_ids(self.collectionName)
        self.assertEqual(ids, [123, 124])

        collection.delete_many({})

    def test_store_images(self):
        collection = self.collection

        data = {
            1211755740: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755740-1.jpg',
            1211755738: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755738-1.jpg',
            1211755735: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755735-1.jpg',
            1211755737: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755737-1.jpg',
            1211755744: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755744-1.jpg',
            1211755689: b'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt-1211755689-1.jpg',
            1211755687: b'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt-1211755687-1.jpg',
            1211755736: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755736-1.jpg',
            1211755904: b'https://cdn-p.cian.site/images/95/571/121/kvartira-sochi-kurortnyy-prospekt-1211755904-1.jpg',
            1211755745: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755745-1.jpg',
            1211755690: b'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt-1211755690-1.jpg',
            1211755810: b'https://cdn-p.cian.site/images/85/571/121/kvartira-sochi-kurortnyy-prospekt-1211755810-1.jpg',
            1211755905: b'https://cdn-p.cian.site/images/95/571/121/kvartira-sochi-kurortnyy-prospekt-1211755905-1.jpg'}

        self._handler.store_images(images=data, location=self.collectionName)

        ids = collection.find().distinct('_id')
        self.assertCountEqual(ids, data.keys())

        for el in data:
            self.assertEqual(data[el], collection.find({'_id': el})[0].get('image'))
            self.assertIsNone(collection.find({'_id': el})[0].get('offer_id'))

        # add new values
        new_data = {99999: b'https://cdn-p.cian.site/images/99999999.jpg'}
        self._handler.store_images(images=new_data,location=self.collectionName)
        #
        ids = collection.find().distinct('_id')
        data.update(new_data)
        self.assertCountEqual(ids, data.keys())

        self.assertEqual(new_data[99999], collection.find({'_id': 99999})[0].get('image'))

        # test overwrite
        modified_image = {99999: b'https://cdn-p.cian.site/images/modified_image.jpg'}
        data.update(modified_image)
        self._handler.store_images(images=modified_image,location= self.collectionName)

        self.assertEqual(modified_image[99999], collection.find({'_id': 99999})[0].get('image'))

        for el in data:
            self.assertEqual(data[el], collection.find({'_id': el})[0].get('image'))
            self.assertIsNone(collection.find({'_id': el})[0].get('offer_id'))

        collection.delete_many({})

    def test_read_actual_image(self):
        collection = self.collection

        url = "https://i.imgur.com/ExdKOOz.png"
        response = cian._get(url, headers={})
        image_bytes = response.content

        data = {1234: image_bytes}

        self._handler.store_images(images=data, location=self.collectionName, offer_id=98765)

        db_bytes = collection.find({'_id': 1234})[0].get('image')

        self.assertEqual(image_bytes, db_bytes)

        # img = Image.open(io.BytesIO(image_bytes))
        # img.show()
        collection.delete_many({})

    def test_store_incorrect_offer_obj(self):
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"
        with self.assertRaises(AttributeError):
            self._handler.store_offers({'foo': 'bar'}, search_request_id, self.collectionName)

    def test_store_offers_new_entries(self):
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"
        collection = self.collection

        collection.delete_many({})

        with open("test/data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        self._handler.store_offers(data, search_request_id, self.collectionName)
        data_modified = list(collection.find({}))

        with open("test/data/offers.pickle", 'rb') as f:
            reloaded_data = pickle.load(f)

        self.assertEqual(len(reloaded_data), len(list(data_modified)))

        for original_offer in reloaded_data:
            doc_id = original_offer.get('cianId')
            processed_offer = list(collection.find({'_id': doc_id}))[0]

            difference = deepdiff.DeepDiff(processed_offer, original_offer,
                                           exclude_paths=["root['_id']", "root['searchRequestId']",
                                                          "root['previous_searchRequestId']", "root['previous_diff']"])

            self.assertEqual(search_request_id, processed_offer['searchRequestId'])
            self.assertEqual([], processed_offer['previous_searchRequestId'], "New data, should not have previous "
                                                                              "meta data mapping")
            self.assertEqual([], processed_offer['previous_diff'], "Historic changes field should be empty, "
                                                                   "no historic data")
            self.assertEqual(doc_id, processed_offer['cianId'], "Id of the offer did not match")
            self.assertEqual({}, difference, f"Difference in original and processed: {difference}")

        # append new values
        new_data = [{"previous_searchRequestId": [], "previous_diff": [],
                     'cianId': 123, 'b': 34, 'bar': 'foo'}]
        self._handler.store_offers(new_data, search_request_id, self.collectionName)

        for original_offer in reloaded_data:
            doc_id = original_offer.get('cianId')
            self.assertEqual(1, len(list(collection.find({'_id': doc_id}))))
            processed_offer = list(collection.find({'_id': doc_id}))[0]

            difference = deepdiff.DeepDiff(processed_offer, original_offer,
                                           exclude_paths=["root['_id']", "root['searchRequestId']",
                                                          "root['previous_searchRequestId']", "root['previous_diff']"])

            self.assertEqual(search_request_id, processed_offer['searchRequestId'])
            self.assertEqual([], processed_offer['previous_searchRequestId'], "New data, should not have previous "
                                                                              "meta data mapping")
            self.assertEqual([], processed_offer['previous_diff'], "Historic changes field should be empty, "
                                                                   "no historic data")
            self.assertEqual(doc_id, processed_offer['cianId'], "Id of the offer did not match")
            self.assertEqual({}, difference, f"Difference in original and processed: {difference}")

        processed_offer = list(collection.find({'_id': 123}))[0]

        difference = deepdiff.DeepDiff(processed_offer, new_data[0],
                                       exclude_paths=["root['_id']", "root['searchRequestId']",
                                                      "root['previous_searchRequestId']", "root['previous_diff']"])

        self.assertEqual(difference, {})
        collection.delete_many({})

    def test_store_new_offers_with_existing_data(self):
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"
        collection = self.collection

        collection.delete_many({})

        historic_offer = {'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
                          'cianId': 123, 'b': 34, 'bar': 'foo', '_id': 123}
        data = [{'cianId': 789, 'b': 34, 'bar': 'foo'},
                {'cianId': 456, 'b': 34, 'bar': 'foo'}]
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        collection.insert_one(historic_offer)
        self.assertEqual(1, len(list(collection.find({}))))

        self._handler.store_offers(data, search_request_id, self.collectionName)

        self.assertEqual(3, len(list(collection.find({}))))

        expected = [
            {'_id': 123, 'searchRequestId': '123-adf', 'previous_searchRequestId': [], 'previous_diff': [],
             'cianId': 123, 'b': 34, 'bar': 'foo'},
            {'_id': 789, 'cianId': 789, 'b': 34, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': [],
             'previous_diff': []},
            {'_id': 456, 'cianId': 456, 'b': 34, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': [],
             'previous_diff': []}]

        self.assertEqual(list(collection.find({})), expected)

    def test_store_offers_with_existing_data(self):
        collection = self.collection

        collection.delete_many({})

        historic_offer = {'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
                          'cianId': 123, 'b': 34, 'bar': 'foo', '_id': 123}
        data = [{'cianId': 123, 'b': 34, 'bar': 'foo'},
                {'cianId': 456, 'b': 34, 'bar': 'foo'}]
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        collection.insert_one(historic_offer)
        self.assertEqual(1, len(list(collection.find({}))))

        self._handler.store_offers(data, search_request_id, self.collectionName)

        self.assertEqual(2, len(list(collection.find({}))))

        expected = [
            {'_id': 123, 'cianId': 123, 'b': 34, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': ['123-adf'],
             'previous_diff': []},
            {'_id': 456, 'cianId': 456, 'b': 34, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': [],
             'previous_diff': []}]

        self.assertEqual(list(collection.find({})), expected)

    def test_store_offers_with_existing_data_with_diff(self):
        collection = self.collection

        collection.delete_many({})

        historic_offer = {'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
                          'cianId': 123, 'b': 34, 'bar': 'foo', '_id': 123}
        data = [{'cianId': 123, 'b': 12345353453, 'bar': 'foo'},
                {'cianId': 456, 'b': 34, 'bar': 'foo'}]
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        collection.insert_one(historic_offer)
        self.assertEqual(1, len(list(collection.find({}))))

        self._handler.store_offers(data, search_request_id, self.collectionName)

        self.assertEqual(2, len(list(collection.find({}))))

        expected = [
            {'_id': 123, 'cianId': 123, 'b': 12345353453, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': ['123-adf'],
             'previous_diff': [{'searchRequestId': {'new_value': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6',
                                                    'old_value': '123-adf'},
                                'values_changed': {"b": {'new_value': 12345353453,
                                                                 'old_value': 34}}}]},
            {'_id': 456, 'cianId': 456, 'b': 34, 'bar': 'foo',
             'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6', 'previous_searchRequestId': [],
             'previous_diff': []}]

        self.assertEqual(list(collection.find({})), expected)

    def test_removal_types_from_diff(self):
        # diff library adds sees changes 'null -> 1234' as a type change and not a value change.
        # Secondly, the types are printed in python way, including ' which brakes the document
        with open('test/data/diff.pickle', 'rb') as f:
            data = pickle.load(f)

        diff = data.get('previous_diff')[0]
        with open('test/data/diff.pickle', 'rb') as f:
            diff_og = pickle.load(f).get('previous_diff')[0]

        diff = _process_diff(diff)
        self.assertIsNone(diff.get('type_changes'))
        self.assertEqual(diff_og.get('searchRequestId'), diff.get('searchRequestId'))

        for type_change_key in diff_og.get('type_changes'):
            self.assertIsNotNone(diff.get('values_changed').get(type_change_key))
            old_value = diff_og.get('type_changes').get(type_change_key).get('old_value')
            new_value = diff_og.get('type_changes').get(type_change_key).get('new_value')

            if not diff_og.get('values_changed').get(type_change_key):
                #  type changed items were not in the value changed list
                self.assertEqual(old_value, diff.get('values_changed').get(type_change_key).get('old_value'))
                self.assertEqual(new_value, diff.get('values_changed').get(type_change_key).get('new_value'))
            else:
                # there is a collision, it should maintain original values
                self.assertEqual(diff_og.get('values_changed').get(type_change_key).get('old_value'), diff.get('values_changed').get(type_change_key).get('old_value'))
                self.assertEqual(diff_og.get('values_changed').get(type_change_key).get('new_value'), diff.get('values_changed').get(type_change_key).get('new_value'))
