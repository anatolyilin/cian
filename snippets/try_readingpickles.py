import pickle
import deepdiff
from pymongo import MongoClient


# def clean(diff: dict) -> dict:
#     update_dict = diff.get('type_changes')
#     for key in update_dict:
#         update_dict[key].pop('old_type', None)
#         update_dict[key].pop('new_type', None)
#         value = update_dict[key]
#         # print(value)
#         # print(key)
#     diff.pop('type_changes')
#     print(diff.get('values_changed'))
#     diff.get('values_changed').update(update_dict)
#     print(diff.get('values_changed'))
#
#
# def get_database():
#     CONNECTION_STRING = "mongodb://testuser:testpwd@127.0.0.1:27017/testDB"
#     client = MongoClient(CONNECTION_STRING)
#     # Create the database for our example (we will use the same database throughout the tutorial
#     return client['testDB']
#
#
# with open('../.failed.pickle', 'rb') as f:
#     data = pickle.load(f)
#
# diff_og = data.get('previous_diff')
#
# diff_dict = diff_og[0]
def process_diff(diff_dict: dict) -> dict:
    if diff_dict.get('dictionary_item_removed', None) is not None:
        diff_dict = process_removed_items(diff_dict)
    return diff_dict


def process_removed_items(diff_dict: dict, delimiter: str = ":") -> dict:
    root = "root['"
    diff_delimiter = "']['"
    dictionary_item_removed = []
    print(diff_dict.get('dictionary_item_removed'))
    for element in diff_dict.get('dictionary_item_removed'):
        # cut the first part containing root[' off
        if element[0:6] == root:
            element = element[6:]
        # cut the trailing part containing '] off
        if element[-2:] == "']":
            element = element[:-2]
        # split by '][', and merge back together with provided delimiter
        dictionary_item_removed.append(delimiter.join(element.split(diff_delimiter)))

    diff_dict['dictionary_item_removed'] = dictionary_item_removed
    return diff_dict


a = {'a': {'b': 12, 'c': 34, 'd': 56}}
b = {'a': {'c': 34}}

diff = deepdiff.DeepDiff(a, b)
diff = process_diff(dict(diff))
print(diff)



#     remove root[
#     replace ][ with delimited
#     remove ]






# clean(diff_dict)
# for el in diff_dict:
#     print(f"{el} : {diff_dict.get(el)}")

# type_changes = diff_dict.get('type_changes')
# values_changed = diff_dict.get('values_changed')
# print(values_changed)
# searchRequestId = diff_dict.get('searchRequestId')
#
#
# for el in type_changes:
#     print(f"{el} : {type_changes.get(el)}")
#
# first_type_change = type_changes.get("root['geo']['jk']['webSiteUrlUtm']")
# print(first_type_change)
# print(type(first_type_change))
#
# for el in first_type_change:
#     print(f"{el} : {first_type_change.get(el)}")

# print('---------')
# for el in values_changed:
#     print(f"{el} : {values_changed.get(el)}")

# dbname = get_database()
# collection = dbname["testCollection"]
#
# diff = {'_id': 1}
# diff.update({'diff': diff_dict})
#
# collection.replace_one({'_id': 1}, diff)



# 'previous_diff': [
#     {'dictionary_item_removed':
#          [root['user']['agentAvailability']['availableFrom'],
#           root['user']['agentAvailability']['availableTo'],
#           root['user']['agentAvailability']['message'],
#           root['user']['agentAvailability']['title']
#           ],
#
#      'values_changed':
#          {
#           "root['addedTimestamp']": {'new_value': 1642753609, 'old_value': 1642666866},
#           "root['added']": {'new_value': 'сегодня, 11:26', 'old_value': 'вчера, 11:21'},
#           "root['humanizedTimedelta']": {'new_value': 'час назад', 'old_value': 'вчера'},
#           "root['user']['agentAvailability']['available']": {'new_value': True, 'old_value': False}
#          },
#      'searchRequestId': {'new_value': 'a716639a-129e-4497-8314-56181a8fa531', 'old_value': '71c359d2-9292-45f0-b1eb-7e2b90b9a6f0'}
#      }
# ]
