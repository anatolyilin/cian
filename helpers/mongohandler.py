import uuid

import helpers.mongodb as database
from helpers.IPersistence import IPersistence
from helpers.diffhandler import get_diff
from helpers.configuration import app_config
import helpers.logging as logging

logger = logging.get_logger()


class MongoHandler(IPersistence):

    def exists(self, path):
        try:
            return path in list(database.getConnection().list_collection_names())
        except Exception as e:
            logger.debug(f"DB collection existence check failed for {path}. Assuming the collection does not exist. ")
        return False

    def _get_ids(self, location: str) -> list:
        cursor = database.getCollection(location)
        return list(cursor.find().distinct('_id'))

    def _append_id(self, doc_id, document: dict) -> dict:
        document['_id'] = doc_id
        return document

    def _id_exists_in(self, doc_id, collection: str) -> bool:
        # return doc_id in self._get_ids(collection)
        cursor = database.getCollection(collection)
        return cursor.count_documents({'_id': doc_id}) == 1

    def store_metadata(self, new_metadata: dict, location: str = None):
        if not location:
            location = app_config.get_nested("locations.meta_collection")
        metadata_cursor = database.getCollection(location)
        metadata_id = new_metadata.get('searchRequestId')
        metadata_doc = self._append_id(metadata_id, new_metadata)

        if not self._id_exists_in(metadata_id, location):
            try:
                metadata_cursor.insert_one(metadata_doc)
            except Exception as e:
                logger.warning(f"Failed to persist data to database due to {e}")
        else:
            logger.error(f"searchRequestId {metadata_id} already present in the metadata table, overwriting.")
            try:
                metadata_cursor.replace_one({"_id": metadata_id}, metadata_doc)
            except Exception as e:
                logger.warning(f"Failed to persist data to database due to {e}")

    def get_known_image_ids(self, location: str = None) -> list:
        if not location:
            location = app_config.get_nested("locations.images_collection")
        return self._get_ids(location)

    def store_images(self, images: dict, offer_id=None, location: str = None):
        if not location:
            location = app_config.get_nested("locations.images_collection")
        metadata_cursor = database.getCollection(location)

        for image_id in images:
            try:
                metadata_cursor.replace_one({'_id': image_id},
                                            {'image': images.get(image_id), 'offer_id': offer_id},
                                            upsert=True)
            except Exception as e:
                logger.warning(f"Failed to persist image {image_id} to database due to {e}")

    def store_offers(self, new_offers: list, search_request_id: str, location: str = None):
        if not location:
            location = app_config.get_nested("locations.offers_collection")

        if type(new_offers) != list:
            raise AttributeError(f'{self.__class__.__name__}.{type(new_offers)} is invalid for persisting offers, '
                                 f'expected {list}')
        logger.debug(f"Storing offers to {location} collection")
        cursor = database.getCollection(location)
        # we can write in bulk with upsert and a custom collision handler, or do a simple iteration
        for offer in new_offers:
            try:
                offer_to_add = self._append_id(offer.get("cianId", offer.get("id", uuid.uuid4())), offer)
                logger.debug(f"Attempting to process offer {offer_to_add['_id']}")
                offer_to_add['searchRequestId'] = search_request_id
                if not offer_to_add.get('previous_searchRequestId'):
                    offer_to_add['previous_searchRequestId'] = []
                if not offer_to_add.get('previous_diff'):
                    offer_to_add['previous_diff'] = []

                if not self._id_exists_in(offer_to_add['_id'], location):
                    logger.debug(f"Attempting to persist new offer {offer_to_add['_id']} to {location} collection")
                    cursor.insert_one(offer_to_add)
                else:
                    logger.debug(f"Offer id found {offer_to_add['_id']} in the {location} collection"
                                 f", attempting to merge.")
                    historic_offer = cursor.find_one({'_id': offer_to_add['_id']})

                    offer_to_add['previous_searchRequestId'] = historic_offer.get(
                        'previous_searchRequestId')
                    offer_to_add['previous_searchRequestId'].append(historic_offer.get('searchRequestId'))

                    difference = get_diff(historic_offer,
                                          offer_to_add,
                                          exclude_paths=[
                                              "root['searchRequestId']",
                                              "root['previous_searchRequestId']",
                                              "root['previous_diff']"])

                    if difference:
                        logger.debug(f"Difference of historic and new offers is {difference}")
                        diff_to_append = dict(difference)

                        diff_to_append['searchRequestId'] = \
                            {'new_value': offer_to_add.get('searchRequestId'),
                             'old_value': historic_offer.get('searchRequestId')}
                        offer_to_add['previous_diff'].append(dict(diff_to_append))

                    logger.debug(f"Persisting {offer_to_add}")
                    cursor.replace_one({"_id": offer_to_add['_id']}, dict(offer_to_add))

            except Exception as e:
                logger.warning(f"Exception {e} - Failed to persist offer {offer}")
