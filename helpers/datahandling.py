import pickle
import os
import uuid
import deepdiff

from pathlib import Path
from helpers.configuration import app_config
import helpers.logging as logging

logger = logging.get_logger()


def print_config():
    print(app_config.get_nested("locations.meta_file"))
    print(app_config.get_nested("locations.offers_file"))


def exists(path) -> bool:
    try:
        logger.debug(f"{path} - path check is {Path(path).is_file()}")
        logger.debug(f"{path} - file size is {os.path.getsize(path)}")
        return Path(path).is_file() and os.path.getsize(path) > 0
    except Exception as e:
        logger.debug(f"File existence check failed for {path}. Assuming the file does not exist. ")
        return False


def load_data(path) -> dict:
    try:
        with open(path, 'rb') as r:
            data = pickle.load(r)
        return data
    except Exception as e:
        logger.warning(f"Failed to read file from {path} due to {e}")
    return {}


def persist_data(data, path):
    try:
        with open(path, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logger.warning(f"Failed to write file to {path} due to {e}")
        raise


def store_metadata(new_metadata, file_path=None):
    if not file_path:
        file_path = app_config.get_nested("locations.meta_file")
    logger.debug(f"Will write to {file_path}")
    logger.info(f"Storing meta data. Will append if exists. Previous meta file exists:  {exists(file_path)}")

    try:
        if not exists(file_path):
            logger.debug(f"Metadata file {file_path} not found")
            metadata_store = {new_metadata.get("searchRequestId"): new_metadata}
            logger.debug(f"Attempting to write new file {file_path}")
            persist_data(metadata_store, file_path)
            logger.debug(f"Wrote new metadata file {file_path}")
        else:
            logger.debug("Previous metadata file found, reading")
            metadata_store = load_data(file_path)
            metadata_store.update({new_metadata.get("searchRequestId"): new_metadata})
            persist_data(metadata_store, file_path)

    except Exception as e:
        logger.warning(f"Failed to write metadata due to {e}")


def get_known_image_ids(file_path=None) -> list:
    logger.info("Getting list of previously downloaded images")
    if not file_path:
        file_path = app_config.get_nested("locations.images_file")
    logger.debug(f"Attempting to read cache from {file_path}")
    try:
        if not exists(file_path):
            logger.debug(f"Images file container {file_path} not found")
            return []
        else:
            logger.debug("Previous images file container found, reading")
            previous_images = load_data(file_path)
            return list(previous_images.keys())
    except Exception as e:
        logger.warning(f"Failed to write metadata due to {e}")


def extract_image_information_from_offer(offer, exclude=None) -> dict:
    logger.debug("Extracting image information from the offer details")
    images_field = offer.get('photos', None)
    return_images = {}
    if not exclude or type(exclude) != list:
        logger.debug("No images id's to be excluded from the download")
        exclude = []
    if not images_field:
        logger.warning(f"Failed to extract image information from the offer {offer}")
    else:
        for image_block in images_field:
            image_id = image_block.get('id')
            if image_id not in exclude:
                return_images[image_id] = image_block.get('fullUrl')
    return return_images


# by design, overwrite previous images with the same id.
def store_images(images, file_path=None):
    if not file_path:
        file_path = app_config.get_nested("locations.images_file")
    logger.debug(f"Will write to {file_path}")
    logger.debug(f"Storing images. Will append if exists. Previous images file container exists:  {exists(file_path)}")
    try:
        if not exists(file_path):
            logger.debug(f"Images file container {file_path} not found")
            logger.debug(f"Attempting to write new file {file_path}")
            persist_data(images, file_path)
            logger.debug(f"Wrote new file {file_path}")
        else:
            logger.debug("Previous images file container found, reading")
            previous_images = load_data(file_path)
            previous_images.update(images)
            persist_data(previous_images, file_path)
    except Exception as e:
        logger.warning(f"Failed to write metadata due to {e}")


def store_offers(new_offers, search_request_id, file_path=None):
    if not file_path:
        file_path = app_config.get_nested("locations.offers_file")
    logger.debug(f"Will write to {file_path}")
    logger.info(f"Storing offers data. Will append if exists. Previous meta file exists:  {exists(file_path)}")
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
        if not exists(file_path):
            logger.debug(f"Previous offers file {file_path} not found, writing new.")
            persist_data(offers_to_add, file_path)
        else:
            logger.debug(f"Previous offers file {file_path} found, attempting to read")
            previous_offers = load_data(file_path)
            logger.debug(f"Previous offers file {file_path} found, read successfully")

            historic_ids = previous_offers.keys()
            new_ids = offers_to_add.keys()
            logger.debug(f"Comparing historic offers to new ones, finding duplicates")
            intersecting_ids = list(set(historic_ids) & set(new_ids))
            logger.debug(f"IDs found in both historic and the new data: {intersecting_ids}")

            if len(intersecting_ids) == 0:
                logger.debug("No duplicates found, attempting to persist")
                persist_data({**previous_offers, **offers_to_add}, file_path)

            else:
                logger.debug("Some offers id found in the historic data, attempting to merge.")
                # dict will get pretty huge, let's not delete keys, but create new dicts instead
                unique_historic_offers = dict((k, v) for (k, v) in previous_offers.items() if k not in intersecting_ids)
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
                    difference = deepdiff.DeepDiff(previous_offers.get(duplicate_id), offers_to_add.get(duplicate_id),
                                                   exclude_paths=["root['searchRequestId']",
                                                                  "root['previous_searchRequestId']",
                                                                  "root['previous_diff]"])
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
                persist_data(all_unique_offers, file_path)
    except Exception as e:
        logger.warning(f"Failed to write offers due to {e}")
