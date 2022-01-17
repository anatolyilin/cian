from helpers.configuration import app_config
from pymongo import MongoClient, errors
import helpers.logging as logging

_connection = None
_serverSelectionTimeoutMS = 10000
logger = logging.get_logger()


def _get_connection_string() -> str:
    connection_string = "mongodb://{username}:{password}@{host}:{port}/{db}" \
        .format(username=app_config.get_nested("database.username"),
                password=app_config.get_nested("database.password"),
                host=app_config.get_nested("database.host"),
                port=app_config.get_nested("database.port"),
                db=app_config.get_nested("database.db"))
    return connection_string


def _connect():
    logger.debug("Attempting to connect to MongoDB")
    try:
        conn = MongoClient(_get_connection_string(), serverSelectionTimeoutMS=_serverSelectionTimeoutMS)
        logger.debug(f"Connected to MongoDB: {conn.server_info()}")
    except errors.ConnectionFailure as err:
        logger.warning(f"Unable to connect to the database, no reason to proceed with the execution. {err}")
        raise
    return conn


# maybe connection and not the reference to the collection should be made global
def getConnection(collection=app_config.get_nested("database.collection")):
    logger.debug("Attempting to retrieve MongoDB connection")
    if collection is None:
        logger.warning("No collection has been selected to work with, aborting.")
        raise errors.ConnectionFailure("Collection not provided")
    global _connection
    if _connection is None:
        _connection = _connect().get_database(collection)
    return _connection


__all__ = ['getConnection']
