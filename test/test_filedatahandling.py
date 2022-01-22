import unittest
import tempfile
import os
import pickle
import deepdiff
import helpers.logging as logging
from helpers.filehander import FileHandler
from helpers.datahandling import DataHandler

logger = logging.get_logger()


class TestFileDataHandling(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.fh = FileHandler()
        self.dh = DataHandler(self.fh)
    
    def test_metadata_new_file(self):
        with open("data/metadata.pickle", 'rb') as f:
            data = pickle.load(f)

        fd, path = tempfile.mkstemp()
        try:
            self.dh.store_metadata(data, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(data.get('searchRequestId'), list(data_modified.keys())[0])
        self.assertEqual(data, data_modified.get(data.get('searchRequestId')))

    def test_metadata_append(self):
        with open("data/metadata.pickle", 'rb') as f:
            data = pickle.load(f)

        historic_metadata = {"123-ad": {'a': 21, 'b': 34, 'bar': 'foo'}}

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(historic_metadata, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            self.dh.store_metadata(data, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(len(list(data_modified.keys())), 2)
        self.assertEqual(data_modified.get("123-ad"), historic_metadata.get("123-ad"))
        self.assertEqual(data, data_modified.get(data.get('searchRequestId')))

    def test_offers_new_file(self):
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        with open("data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        fd, path = tempfile.mkstemp()
        try:
            self.dh.store_offers(data, search_request_id, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(len(data), len(list(data_modified.keys())))

        with open("data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        for original_offer in data:
            id = original_offer.get('cianId')
            processed_offer = data_modified.get(id)

            difference = deepdiff.DeepDiff(original_offer, processed_offer,
                                           exclude_paths=["root['searchRequestId']", "root['previous_searchRequestId']",
                                                          "root['previous_diff']"])

            self.assertEqual(search_request_id, processed_offer['searchRequestId'])
            self.assertEqual([], processed_offer['previous_searchRequestId'], "New data, should not have previous "
                                                                              "meta data mapping")
            self.assertEqual([], processed_offer['previous_diff'], "Historic changes field should be empty, "
                                                                   "no historic data")
            self.assertEqual(id, processed_offer['cianId'], "Id of the offer did not match")
            self.assertEqual({}, difference, f"Difference in original and processed: {difference}")

    def test_offers_existing_file_append_only(self):
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        with open("data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        historic_offers = {123: {'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
                                 'cianId': 123, 'b': 34, 'bar': 'foo'}}

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(historic_offers, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            self.dh.store_offers(data, search_request_id, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(data_modified.get(123), historic_offers.get(123))
        self.assertEqual(len(data) + 1, len(list(data_modified.keys())))

        with open("data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        for original_offer in data:
            id = original_offer.get('cianId')
            processed_offer = data_modified.get(id)

            difference = deepdiff.DeepDiff(original_offer, processed_offer,
                                           exclude_paths=["root['searchRequestId']", "root['previous_searchRequestId']",
                                                          "root['previous_diff']"])

            self.assertEqual(search_request_id, processed_offer['searchRequestId'])
            self.assertEqual([], processed_offer['previous_searchRequestId'], "New data, should not have previous "
                                                                              "meta data mapping")
            self.assertEqual([], processed_offer['previous_diff'], "Historic changes field should be empty, "
                                                                   "no historic data")
            self.assertEqual(id, processed_offer['cianId'], "Id of the offer did not match")
            self.assertEqual({}, difference, f"Difference in original and processed: {difference}")

    def test_offers_existing_file_same_offer_existed_handling(self):
        historic_offers = {123: {'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
                                 'cianId': 123, 'b': 34, 'bar': 'foo'}}
        data = [{'cianId': 123, 'b': 34, 'bar': 'foo'},
                {'cianId': 456, 'b': 34, 'bar': 'foo'}]
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(historic_offers, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            self.dh.store_offers(data.copy(), search_request_id, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(2, len(list(data_modified.keys())))

        expected = {
            123: {'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6", "previous_searchRequestId": ["123-adf"],
                  "previous_diff": [], 'cianId': 123, 'b': 34, 'bar': 'foo'},
            456: {'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6", "previous_searchRequestId": [],
                  "previous_diff": [], 'cianId': 456, 'b': 34, 'bar': 'foo'}
        }

        self.assertEqual(data_modified, expected)

    def test_offers_existing_file_one_offer_modified(self):
        historic_offers = {123: {
            'searchRequestId': "123-adf", "previous_searchRequestId": [], "previous_diff": [],
            'cianId': 123, 'b': 34, 'bar': 'foo'}}

        data = [{'cianId': 123, 'b': 34, 'bar': 'foobar'},
                {'cianId': 456, 'b': 34, 'bar': 'foo'}]
        search_request_id = "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6"

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(historic_offers, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            self.dh.store_offers(data, search_request_id, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(2, len(list(data_modified.keys())))

        expected = {
            123: {'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6", "previous_searchRequestId": ["123-adf"],
                  'cianId': 123, 'b': 34, 'bar': 'foobar',
                  'previous_diff': [{'searchRequestId': {'new_value': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6',
                                                         'old_value': '123-adf'},
                                     'values_changed': {"root['bar']": {'new_value': 'foobar',
                                                                        'old_value': 'foo'}}}]},
            456: {'searchRequestId': "4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6", "previous_searchRequestId": [],
                  "previous_diff": [], 'cianId': 456, 'b': 34, 'bar': 'foo'}
        }

        self.assertEqual(data_modified, expected)

    def test_extract_image_information_from_offer(self):
        with open("data/offers.pickle", 'rb') as f:
            data = pickle.load(f)

        offer = data[:1][0]
        images = self.dh.extract_image_information_from_offer(offer)
        images_field = offer.get('photos')
        self.assertEqual(len(offer.get('photos')), len(list(images.keys())))

        for el in images_field:
            self.assertEqual(el.get('fullUrl'), images.get(el.get('id')))

        malformed_data = {'foo': 'bar'}
        self.assertEqual({}, self.dh.extract_image_information_from_offer(malformed_data))

        exclude = [1211755686, 1211755906]
        expected = {1211755740: 'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt'
                                '-1211755740-1.jpg',
                    1211755738:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755738-1.jpg',
                    1211755735: 'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt'
                                '-1211755735-1.jpg', 1211755737:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755737-1.jpg'
                        '', 1211755744: 'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755744-1.jpg', 1211755689:
                        'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt-1211755689-1.jpg'
                        '', 1211755687: 'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755687-1.jpg', 1211755736:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755736-1.jpg'
                        '', 1211755904: 'https://cdn-p.cian.site/images/95/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755904-1.jpg', 1211755745:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755745-1.jpg'
                        '', 1211755690: 'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755690-1.jpg', 1211755810:
                        'https://cdn-p.cian.site/images/85/571/121/kvartira-sochi-kurortnyy-prospekt-1211755810-1.jpg'
                        '', 1211755905: 'https://cdn-p.cian.site/images/95/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755905-1.jpg', 1211755688:
                        'https://cdn-p.cian.site/images/65/571/121/kvartira-sochi-kurortnyy-prospekt-1211755688-1.jpg'
                        '', 1211755741:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755741-1.jpg'
                        '', 1211755809: 'https://cdn-p.cian.site/images/85/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755809-1.jpg', 1211755742:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755742-1.jpg'
                        '', 1211755811: 'https://cdn-p.cian.site/images/85/571/121/kvartira-sochi-kurortnyy-prospekt'
                                        '-1211755811-1.jpg', 1211755739:
                        'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755739-1.jpg'
                        '', 1211755813:
                        'https://cdn-p.cian.site/images/85/571/121/kvartira-sochi-kurortnyy-prospekt-1211755813-1.jpg'}

        self.assertEqual(expected, self.dh.extract_image_information_from_offer(offer, exclude))

    def test_actual_photo(self):
        from helpers.request import _get
        url = "https://i.imgur.com/ExdKOOz.png"
        response = _get(url, headers={})
        data = {1227: response.content}

        fd, path = tempfile.mkstemp()
        try:
            self.dh.store_images(images=data, location=path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(data_modified, data)

    def test_store_images_new_file(self):
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

        fd, path = tempfile.mkstemp()
        try:
            self.dh.store_images(images=data, location=path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(len(data), len(data_modified))
        self.assertEqual(list(data.keys()), list(data_modified.keys()))
        self.assertEqual(data, data_modified)

    def test_store_images(self):
        data = {
            1211755740: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755740-1.jpg',
            1211755738: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755738-1.jpg',
            1211755735: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755735-1.jpg',
            1211755737: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755737-1.jpg',
            1211755744: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755744-1.jpg',
        }

        to_be_added = {
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

        data_expected = {
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

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            self.dh.store_images(images=to_be_added, location=path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)

        self.assertEqual(data_expected, data_modified)

    def test_getting_known_image_ids(self):
        data = {
            1211755740: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755740-1.jpg',
            1211755738: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755738-1.jpg',
            1211755735: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755735-1.jpg',
            1211755737: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755737-1.jpg',
            1211755744: b'https://cdn-p.cian.site/images/75/571/121/kvartira-sochi-kurortnyy-prospekt-1211755744-1.jpg',
        }

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            image_ids = self.dh.get_known_image_ids(path)
        finally:
            os.remove(path)

        self.assertEqual(image_ids, list(data.keys()))

        image_ids = self.dh.get_known_image_ids('do_not_exist.pickle')
        self.assertEqual([], image_ids)


if __name__ == '__main__':
    unittest.main()
