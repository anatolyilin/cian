# import sqlalchemy
# from testcontainers.mysql import MySqlContainer
#
# with MySqlContainer('mysql:5.7.17') as mysql:
#     engine = sqlalchemy.create_engine(mysql.get_connection_url())
#     version, = engine.execute("select version()").fetchone()
#     print(version)  # 5.7.17
#     print(mysql.get_connection_url())


from pymongo import MongoClient
import time
from testcontainers.mongodb import MongoDbContainer

with MongoDbContainer('mongo:latest') as mongoDB:
    client = MongoClient(mongoDB.get_connection_url())
    client['testDB']

    # CONNECTION_STRING = "mongodb://testuser:testpwd@127.0.0.1:27017/testDB"
    # client = MongoClient(CONNECTION_STRING)
    # print(client)
    # engine = sqlalchemy.create_engine(mysql.get_connection_url())
    # version, = engine.execute("select version()").fetchone()
    # print(version)  # 5.7.17
    # print(mysql.get_connection_url())