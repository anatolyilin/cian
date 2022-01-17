import json
import deepdiff

#
# dict_1 = {
#     "a": 1,
#     "k": 34,
#     "nested": {
#         "b": 1,
#     }
# }
#
# dict_2 = {
#     "a": 2,
#     "nested": {
#         "b": 1,
#     },
# }
#
# diff = deepdiff.DeepDiff(dict_1, dict_2, exclude_paths=["root['a']", "root['k']"])
#
# print(diff)
# if not diff:
#     print("equal")
# else:
#     print("not equal")

dict_1 = {'searchRequestId': '123-adf',
          'previous_searchRequestId': ['4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6'],
          'previous_diff': [],
          'cianId': 123,
          'b': 34,
          'bar': 'foo'}
dict_2 = {'cianId': 123,
          'b': 34,
          'bar': 'foo',
          'searchRequestId': '4acb3624-67c4-4c3c-bcc8-5cc81dcd11d6',
          'previous_searchRequestId': [],
          'previous_diff': []}

diff = deepdiff.DeepDiff(dict_1, dict_2, exclude_paths=["root['searchRequestId']",
                                                        "root['previous_searchRequestId']",
                                                        "root['previous_diff]"])

print(dict(diff))
print(type(dict(diff)))
if not diff:
    print("equal")
else:
    print("not equal")