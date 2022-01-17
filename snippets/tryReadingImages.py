import pickle

with open("../data/img/offers_images.pickle", 'rb') as r:
    data_modified = pickle.load(r)

print(data_modified)

test = data_modified[1210879568]

print(test.content)