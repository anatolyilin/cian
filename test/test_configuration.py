import unittest
import tempfile
import os

from helpers.configuration import app_config


class TestConfig(unittest.TestCase):

    def test_an_empty_load(self):
        self.assertEqual({}, app_config.load('doesnotexists.yaml'))
        self.assertEqual({}, app_config.load(path=None))

    def test_config(self):
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write("""
                    property: true
                    nested:
                        item: "foo"
                    other:
                        something: [1,2,3]
                    """)

            app_config.load(path)

            self.assertTrue(app_config.get("property"), "Config property not found")

            value = app_config.get_nested("nested.item")
            self.assertEqual(value, "foo", "Nested config item not found.")

            self.assertEqual([1, 2, 3], app_config.get_nested("other.something"))
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
