import unittest
import tempfile
import os

from helpers.configuration import app_config


class TestConfig(unittest.TestCase):

    def test_config(self):
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write("""
                    property: true
                    nested:
                        item: "foo"
                    """)

            app_config.load(path)

            self.assertTrue(app_config.get("property"), "Config property not found")

            value = app_config.get_nested("nested.item")
            self.assertEqual(value, "foo", "Nested config item not found.")
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
