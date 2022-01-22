import unittest
import tempfile
import os
import pickle
import helpers.logging as logging

import helpers.filehander as filehandler

logger = logging.get_logger()
fh = filehandler.FileHandler()


class TestFileHandler(unittest.TestCase):

    def test_exceptions(self):
        with self.assertRaises(Exception):
            filehandler.load_data('doesntexist.txt')

        with self.assertRaises(Exception):
            filehandler.persist_data({}, 'doesntexist.txt')

        with self.assertRaises(Exception):
            filehandler.store_metadata({}, 'doesntexist.txt')

        with self.assertRaises(Exception):
            filehandler.get_known_image_ids('doesntexist.txt')

        with self.assertRaises(Exception):
            filehandler.store_images(images={}, location='doesntexist.txt')

        with self.assertRaises(Exception):
            filehandler.store_offers(new_offers={}, search_request_id="123", location='doesntexist.txt')


    def test_load_data(self):
        data = {'foo': 'bar'}
        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            f.close()
            loaded_data = fh.load_data(path)
        finally:
            os.remove(path)

        self.assertEqual(loaded_data, data)

        fd, path = tempfile.mkstemp()
        try:
            loaded_data = fh.load_data(path)
        finally:
            os.remove(path)

        self.assertEqual(loaded_data, {})

    def test_store_data(self):
        data = {'foo': 'bar'}
        fd, path = tempfile.mkstemp()
        try:
            fh.persist_data(data, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)
        self.assertEqual(data, data_modified)

        data = {'foo': 'foobarfoo'}
        data_og = {'foo': 1234}
        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                pickle.dump(data_og, f, pickle.HIGHEST_PROTOCOL)
            fh.persist_data(data, path)
            with open(path, 'rb') as r:
                data_modified = pickle.load(r)
        finally:
            os.remove(path)
        self.assertEqual(data, data_modified)
        self.assertNotEqual(data_og, data_modified)

    def test_file_paths(self):
        fd, path = tempfile.mkstemp()
        try:
            self.assertFalse(fh.exists(path), "Should fail, proposed file is empty")
            with os.fdopen(fd, "w") as tmp:
                tmp.write("""
                            key: value
                            some:
                                bar: "foo"
                            """)

            self.assertTrue(fh.exists(path), "False negative")
        finally:
            os.remove(path)

        self.assertFalse(fh.exists("non_existing_file.txt"), "False positive")


if __name__ == '__main__':
    unittest.main()