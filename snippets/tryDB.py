from pymongo import MongoClient
import pymongo
from pandas import DataFrame

def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://testuser:testpwd@localhost/testDB"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['testDB']


dbname = get_database()
collection_name = dbname["testCollection"]

item_details = collection_name.find()
# for item in item_details:
#     # This does not give a very readable output
#     print(item)

# convert the dictionary objects to dataframe
items_df = DataFrame(item_details)

# see the magic
print(items_df)