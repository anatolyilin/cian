import pickle

metadata_loc = '../data/metadata/metadata.pickle'
offers_loc = '../data/raw/offers.pickle'


def load_data(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data


metadata = load_data(metadata_loc)
offers = load_data(offers_loc)


# print(offers[list(offers.keys())[0]].keys())

print(offers[list(offers.keys())[0]])

photos = offers[list(offers.keys())[0]]['photos']

pics_keys = ['thumbnailUrl', 'fullUrl']
# 1204642334
for photo in photos:
    print(photo)
# #
# for id in list(offers.keys()):
#     # print(offers[id]['bargainTerms']['price']) -> price
#     print(offers[id]['bargainTerms']['price'])

# print(metadata[list(metadata.keys())[0]])
#
# curl 'https://cdn-p.cian.site/images/51/866/811/kvartira-centralnyy-gorkogo-pereulok-1186681538-2.jpg' \
# -X 'GET' \
# -H 'Accept: image/webp,image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5' \
# -H 'Accept-Encoding: gzip, deflate, br' \
# -H 'Host: cdn-p.cian.site' \
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15' \
# -H 'Accept-Language: en-GB,en;q=0.9' \
# -H 'Referer: https://sochi.cian.ru/' \
# -H 'Connection: keep-alive'


