import deepdiff
import helpers.logging as logging

logger = logging.get_logger()


def _process_type_changes(diff)-> dict:
    """
    Removes the type changes key and refactor the changes to the value changes field.
    :param diff: deepdiff dict
    :return: dict with key 'type_changed' removed and values added to the 'values_changes' field
    """
    type_changed = diff.get('type_changes', {})

    for key in type_changed:
        type_changed[key].pop('old_type', None)
        type_changed[key].pop('new_type', None)

        if diff.get('values_changed', None) is not None:
            # handle possible but improbable collisions between value_changes and type_changes
            if key in list(diff.get('values_changed').keys()):
                # some keys overlap, this indicates change in value and type. Should not be possible, but alright.
                if diff.get('values_changed').get(key).get('new_value') != type_changed.get(key).get('new_value') or \
                        diff.get('values_changed').get(key).get('old_value') != type_changed.get(key).get('old_value'):
                    logger.error(f"Diff library error. It should not be possible to have value and type change for "
                                 f"the same key. Type changes, modified {type_changed}. modified Diff {diff}")
                    type_changed.pop(key)

    diff.pop('type_changes', None)
    if diff.get('values_changed', None) is None:
        diff['values_changed'] = type_changed
    else:
        diff['values_changed'].update(type_changed)

    return diff


def _process_diff_set(items: list, delimiter: str = ":") -> list:
    """
    modify list of root['foo'][bar] to list of 'foo<delimiter>bar'. Note missing quotes in the original list.
    :param items: list of elements of string type, e.g. [root[foo]['bar']]
    :param delimiter: delimiter of the values, see description.
    :return: list of elements of string type, e.g. ['foo<delimiter>bar']
    """
    root = "root["
    diff_delimiter = "]["

    set_item_processed = []
    for element in items:
        # remove '
        element = element.replace("'", "")
        # cut the first part containing root[' off
        if element[0:5] == root:
            element = element[5:]
        # cut the trailing part containing '] off
        if element[-1:] == "]":
            element = element[:-1]
        # split by '][', and merge back together with provided delimiter
        set_item_processed.append(delimiter.join(element.split(diff_delimiter)))

    return set_item_processed


def _process_diff_list(items: list, delimiter: str = ":") -> list:
    """
    modify list of root['foo']['bar'] to list of 'foo<delimiter>bar'
    :param items: list of elements of string type, e.g. [root['foo']['bar']]
    :param delimiter: delimiter of the values, see description.
    :return: list of elements of string type, e.g. ['foo<delimiter>bar']
    """
    root = "root['"
    diff_delimiter = "']['"

    dictionary_item_processed = []
    for element in items:
        # cut the first part containing root[' off
        if element[0:6] == root:
            element = element[6:]
        # cut the trailing part containing '] off
        if element[-2:] == "']":
            element = element[:-2]
        # split by '][', and merge back together with provided delimiter
        dictionary_item_processed.append(delimiter.join(element.split(diff_delimiter)))

    return dictionary_item_processed


def _process_diff_dict(items: dict, delimiter: str = ":") -> dict:
    """
    map a dict {root['foo']['bar']: value} to dict of {'foo<delimiter>bar': value}
    :param items: dict, {root['foo']['bar']: value}
    :param delimiter: delimiter of the values, see description.
    :return: dict, {'foo<delimiter>bar': value}
    """
    root = "root['"
    diff_delimiter = "']['"

    dictionary_item_processed = {}
    # for element in items:
    for key, value in items.items():
        # cut the first part containing root[' off
        if key[0:6] == root:
            key = key[6:]
        # cut the trailing part containing '] off
        if key[-2:] == "']":
            key = key[:-2]
        # split by '][', and merge back together with provided delimiter
        dictionary_item_processed[delimiter.join(key.split(diff_delimiter))] = value

    return dictionary_item_processed


def _process_diff(diff: dict) -> dict:
    """
    Helper function to process dict containing diff to acceptable format
    :param diff: diff dict produced by deepdiff library
    :return: diff in acceptable format
    """
    if diff.get('values_changed', None) is not None:
        diff['values_changed'] = _process_diff_dict(diff.get('values_changed'))

    if diff.get('dictionary_item_removed', None) is not None:
        diff['dictionary_item_removed'] = _process_diff_list(diff.get('dictionary_item_removed'))

    if diff.get('dictionary_item_added', None) is not None:
        diff['dictionary_item_added'] = _process_diff_list(diff.get('dictionary_item_added'))

    if diff.get('type_changes', None) is not None:
        diff = _process_type_changes(diff)

    if diff.get('set_item_added', None) is not None:
        diff['set_item_added'] = _process_diff_set(diff.get('set_item_added'))

    if diff.get('set_item_removed', None) is not None:
        diff['set_item_removed'] = _process_diff_set(diff.get('set_item_removed'))

    return diff


def get_diff(first: dict, second: dict, exclude_paths: list = None) -> dict:
    """
    Compute diff between two dicts
    :param first: first dict
    :param second: second dict
    :param exclude_paths: elements to exclude from the diff
    :return: diff of two elements that complies with the following requirements:
        - change in value type (null -> int, null -> str) is moved to value_changes key
        -
        -
    """
    diff = deepdiff.DeepDiff(first, second, exclude_paths=exclude_paths)
    return _process_diff(diff)
