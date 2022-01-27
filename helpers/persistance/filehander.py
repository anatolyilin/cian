import pickle # nosec
import os
import uuid
import deepdiff

from helpers.persistance.IPersistence import IPersistence

from pathlib import Path
import helpers.logging as logging
from helpers.configuration import app_config

logger = logging.get_logger()


class FileHandler(IPersistence):

    def exists(self, path):
        try:
            logger.debug(f"{path} - path check is {Path(path).is_file()}")
            logger.debug(f"{path} - file size is {os.path.getsize(path)}")
            return Path(path).is_file() and os.path.getsize(path) > 0
        except Exception as e:
            logger.debug(f"File existence check failed for {path} with {e}. Assuming the file does not exist. ")
            return False

    def load_data(self, path):
        try:
            if self.exists(path):
                with open(path, 'rb') as r: # nosec
                    data = pickle.load(r)
                return data
        except Exception as e:
            logger.warning(f"Failed to read file from {path} due to {e}")
        return {}

    def persist_data(self, data, path):
        try:
            with open(path, 'wb') as f: # nosec
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.warning(f"Failed to write file to {path} due to {e}")
            raise

    def store_metadata(self, new_metadata, location=None):
        if not location:
            location = app_config.get_nested("locations.meta_file")
        logger.debug(f"Will write to {location}")
        logger.info(
            f"Storing meta data. Will append if exists. Previous meta file exists:  {self.exists(location)}")

        try:
            if not self.exists(location):
                logger.debug(f"Metadata file {location} not found")
                metadata_store = {new_metadata.get("searchRequestId"): new_metadata}
                logger.debug(f"Attempting to write new file {location}")
                self.persist_data(metadata_store, location)
                logger.debug(f"Wrote new metadata file {location}")
            else:
                logger.debug("Previous metadata file found, reading")
                metadata_store = self.load_data(location)
                metadata_store.update({new_metadata.get("searchRequestId"): new_metadata})
                self.persist_data(metadata_store, location)

        except Exception as e:
            logger.warning(f"Failed to write metadata due to {e}")

    def get_known_image_ids(self, location: None) -> list:
        logger.info("Getting list of previously downloaded images")
        if not location:
            location = app_config.get_nested("locations.images_file")
        logger.debug(f"Attempting to read cache from {location}")
        try:
            if not self.exists(location):
                logger.debug(f"Images file container {location} not found")
                return []
            else:
                logger.debug("Previous images file container found, reading")
                previous_images = self.load_data(location)
                return list(previous_images.keys())
        except Exception as e:
            logger.warning(f"Failed to write metadata due to {e}")

    # by design, overwrite previous images with the same id.
    def store_images(self, images, offer_id=None, location=None):
        if not location:
            location = app_config.get_nested("locations.images_file")
        logger.debug(f"Will write to {location}")
        logger.debug(
            f"Storing images. Will append if exists. Previous images file container exists:  {self.exists(location)}")
        try:
            if not self.exists(location):
                logger.debug(f"Images file container {location} not found")
                logger.debug(f"Attempting to write new file {location}")
                self.persist_data(images, location)
                logger.debug(f"Wrote new file {location}")
            else:
                logger.debug("Previous images file container found, reading")
                previous_images = self.load_data(location)
                previous_images.update(images)
                self.persist_data(previous_images, location)
        except Exception as e:
            logger.warning(f"Failed to write metadata due to {e}")

    def store_offers(self, new_offers, search_request_id, location=None):
        if not location:
            location = app_config.get_nested("locations.offers_file")
        logger.debug(f"Will write to {location}")
        logger.info(f"Storing offers data. Will append if exists. Previous meta file exists:  {self.exists(location)}")
        try:
            offers_to_add = {}
            logger.debug("Processing offers, appending metadata")
            for offer in new_offers:
                offer['searchRequestId'] = search_request_id
                if not offer.get('previous_searchRequestId'):
                    offer['previous_searchRequestId'] = []
                if not offer.get('previous_diff'):
                    offer['previous_diff'] = []

                offers_to_add.update({offer.get("cianId", offer.get("id", uuid.uuid4())): offer})

            logger.debug("Processed offers, attempting to persist offers")
            if not self.exists(location):
                logger.debug(f"Previous offers file {location} not found, writing new.")
                self.persist_data(offers_to_add, location)
            else:
                logger.debug(f"Previous offers file {location} found, attempting to read")
                previous_offers = self.load_data(location)
                logger.debug(f"Previous offers file {location} found, read successfully")

                historic_ids = previous_offers.keys()
                new_ids = offers_to_add.keys()
                logger.debug(f"Comparing historic offers to new ones, finding duplicates")
                intersecting_ids = list(set(historic_ids) & set(new_ids))
                logger.debug(f"IDs found in both historic and the new data: {intersecting_ids}")

                if len(intersecting_ids) == 0:
                    logger.debug("No duplicates found, attempting to persist")
                    self.persist_data({**previous_offers, **offers_to_add}, location)

                else:
                    logger.debug("Some offers id found in the historic data, attempting to merge.")
                    # dict will get pretty huge, let's not delete keys, but create new dicts instead
                    unique_historic_offers = dict(
                        (k, v) for (k, v) in previous_offers.items() if k not in intersecting_ids)
                    logger.debug(f"Unique historic values found: {unique_historic_offers}")
                    new_unique_offers = dict((k, v) for (k, v) in offers_to_add.items() if k not in intersecting_ids)
                    logger.debug(f"Unique values found in new offers: {new_unique_offers}")
                    all_unique_offers = {**unique_historic_offers, **new_unique_offers}
                    logger.debug(f"Unique values to append: {new_unique_offers}")

                    for duplicate_id in intersecting_ids:
                        logger.debug(f"Processing duplicate id {duplicate_id}")
                        updated_offer = offers_to_add.get(duplicate_id)

                        logger.debug(f"Processing previous_searchRequestIds.")
                        updated_offer['previous_searchRequestId'] = previous_offers.get(duplicate_id).get(
                            'previous_searchRequestId')
                        updated_offer['previous_searchRequestId'].append(
                            previous_offers.get(duplicate_id).get('searchRequestId'))

                        logger.debug("Attempting to process the duplicate offer")
                        difference = deepdiff.DeepDiff(previous_offers.get(duplicate_id),
                                                       offers_to_add.get(duplicate_id),
                                                       exclude_paths=["root['searchRequestId']",
                                                                      "root['previous_searchRequestId']",
                                                                      "root['previous_diff']"])
                        logger.debug(f"Diff new - old offer: {difference}")
                        if difference:
                            diff_to_append = dict(difference)
                            diff_to_append['searchRequestId'] = \
                                {'new_value': updated_offer.get('searchRequestId'),
                                 'old_value': previous_offers.get(duplicate_id).get('searchRequestId')}
                            logger.debug("New offer will modify the existing one, appending the diff")
                            if not updated_offer.get('previous_diff'):
                                updated_offer['previous_diff'] = []

                            updated_offer['previous_diff'].append(diff_to_append)

                        logger.debug("Offer processed, adding the list")
                        all_unique_offers.update({duplicate_id: updated_offer})

                    logger.debug("All offers processed, writing to file")
                    self.persist_data(all_unique_offers, location)
        except Exception as e:
            logger.warning(f"Failed to write offers due to {e}")
