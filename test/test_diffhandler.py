from unittest import TestCase
import deepdiff
from helpers.diffhandler import _process_diff_set, _process_diff_list, _process_diff_dict, get_diff, \
    _process_type_changes


class TestDiffHandler(TestCase):
    def test_process_diff_list(self):
        list = ["root['a']['b']", "root['a']['d']"]
        expsected_list = ['a:b', 'a:d']
        process_list = _process_diff_list(list)
        self.assertEqual(process_list, expsected_list)

        list = ["root['a']['b']"]
        expsected_list = ['a:b']
        process_list = _process_diff_list(list)
        self.assertEqual(process_list, expsected_list)

        list = ["root['a']['root']"]
        expsected_list = ['a:root']
        process_list = _process_diff_list(list)
        self.assertEqual(process_list, expsected_list)

        list = ["root['a']['ro][ot']"]
        expsected_list = ['a:ro][ot']
        process_list = _process_diff_list(list)
        self.assertEqual(process_list, expsected_list)

    def test_process_diff_dict(self):
        data_dict = {"root['a']['b']": 34}
        expected_dict = {'a:b': 34}
        processed_dict = _process_diff_dict(data_dict)
        self.assertEqual(expected_dict, processed_dict)

        data_dict = {"root['a']['b']": 34, "root['c']['asd']": 34}
        expected_dict = {'a:b': 34, 'c:asd': 34}
        processed_dict = _process_diff_dict(data_dict)
        self.assertEqual(expected_dict, processed_dict)

    def test_process_diff_set(self):
        list = ["root['a'][b]", "root['a']['d']"]
        expsected_list = ['a:b', 'a:d']
        process_list = _process_diff_set(list)
        self.assertEqual(process_list, expsected_list)

        list = ["root[a][b]"]
        expsected_list = ['a:b']
        process_list = _process_diff_set(list)
        self.assertEqual(process_list, expsected_list)

        list = ["root[a]['root']"]
        expsected_list = ['a:root']
        process_list = _process_diff_set(list)
        self.assertEqual(process_list, expsected_list)

    def test_process_dictonary(self):
        a = {'a': {'b': 12, 'c': 34, 'd': 56}}
        b = {'a': {'c': 34}}
        expected_result = {'dictionary_item_removed': ['a:b', 'a:d']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {'c': 34}}
        b = {'a': {'b': 12, 'c': 34, 'd': 56}}
        expected_result = {'dictionary_item_added': ['a:b', 'a:d']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 23, 'b': 34}
        b = {'a': 23}
        expected_result = {'dictionary_item_removed': ['b']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 23, 'b': {'d': 123}}
        b = {'a': 23}
        expected_result = {'dictionary_item_removed': ['b']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 23}
        b = {'a': 23, 'b': 34}
        expected_result = {'dictionary_item_added': ['b']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {'b': 12, 'c': 34, 'd': 56}}
        b = {'a': {'b': 12, 'c': 34}}
        expected_result = {'dictionary_item_removed': ['a:d']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {'b': 12, 'c': 34}}
        b = {'a': {'b': 12, 'c': 34, 'd': 56}}
        expected_result = {'dictionary_item_added': ['a:d']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

    def test_value_change(self):
        a = {'a': {'b': 12, 'c': 34, 'd': 56}}
        b = {'a': {'b': 12, 'c': 34, 'd': 5}}
        expected_result = {'values_changed': {'a:d': {'new_value': 5, 'old_value': 56}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 23}
        b = {'a': 34}
        expected_result = {'values_changed': {'a': {'new_value': 34, 'old_value': 23}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {'b': 12, 'c': 34, 'd': 56}}
        b = {'a': {'b': 12, 'c': 3, 'd': 5}}
        expected_result = {
            'values_changed': {'a:d': {'new_value': 5, 'old_value': 56}, 'a:c': {'new_value': 3, 'old_value': 34}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

    def test_sets(self):
        a = {'a': {1, 2, 3, 4}}
        b = {'a': {1, 2, 3}}
        expected_result = {'set_item_removed': ['a:4']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {1, 2, 3, 4}}
        b = {'a': {1, 2, 3, 4, 5}}
        expected_result = {'set_item_added': ['a:5']}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

    def test_value_type_changed(self):
        a = {'a': {1, 2, 3, 4}}
        b = {'a': None}
        expected_result = {'values_changed': {"root['a']": {'old_value': {1, 2, 3, 4}, 'new_value': None}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 34}
        b = {'a': None}
        expected_result = {'values_changed': {"root['a']": {'old_value': 34, 'new_value': None}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': None}
        b = {'a': 34}
        expected_result = {'values_changed': {"root['a']": {'old_value': None, 'new_value': 34}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 'some string'}
        b = {'a': 34}
        expected_result = {'values_changed': {"root['a']": {'old_value': 'some string', 'new_value': 34}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': {'b': 56}}
        b = {'a': 34}
        expected_result = {'values_changed': {"root['a']": {'old_value': {'b': 56}, 'new_value': 34}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 34}
        b = {'a': {'b': 56}}
        expected_result = {'values_changed': {"root['a']": {'old_value': 34, 'new_value': {'b': 56}}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

        a = {'a': 34, 'c': 99}
        b = {'a': {'b': 56}, 'c': 87}
        expected_result = {'values_changed': {'c': {'new_value': 87, 'old_value': 99},
                                              "root['a']": {'old_value': 34, 'new_value': {'b': 56}}}}
        processed_diff = get_diff(a, b)
        self.assertEqual(processed_diff, expected_result)

    def test__process_type_changes_edge_case(self):
        # It should not be possible to have the same key in the type change AND value change fields of the diff.
        # However, if this happens, the value change field has precedence

        diff = {
            'type_changes':
                {
                    "root['a']": {
                        'old_type': "<class 'int'>",
                        'new_type': "<class 'dict'>",
                        'old_value': 34,
                        'new_value': {'b': 56}
                    }
                },
            'values_changed':
                {
                    "root['c']": {'new_value': 87, 'old_value': 99},
                    "root['a']": {'new_value': 1, 'old_value': 2}
                }
        }

        diff_expected = \
            {'values_changed':
                 {"root['c']":
                      {'new_value': 87, 'old_value': 99},
                  "root['a']": {'new_value': 1, 'old_value': 2}
                  }
             }

        print(_process_type_changes(diff))
