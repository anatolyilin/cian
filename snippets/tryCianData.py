import pickle

with open('../data/raw/cian_dump.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)

data_json = data.json()
house_data = data_json['data']

offers = house_data['offersSerialized']

two_offers = offers[:2]
assert len(two_offers) == 2

house_data.pop('offersSerialized')

with open('../test/data/metadata.pickle', 'wb') as f:
    pickle.dump(house_data, f, pickle.HIGHEST_PROTOCOL)

with open('../test/data/offers.pickle', 'wb') as f:
    pickle.dump(two_offers, f, pickle.HIGHEST_PROTOCOL)

# with open('metadata.pickle', 'rb') as f:
#     # The protocol version used is detected automatically, so we do not
#     # have to specify it.
#     data = pickle.load(f)
#
# print(data)