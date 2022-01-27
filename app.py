import pickle # nosec
import time

from helpers.configuration import app_config
from helpers.persistance.mongohandler import MongoHandler
from helpers.persistance.filehander import FileHandler
from helpers.cooloff import CoolOff
import helpers.request as cian
import helpers.logging as logging
from helpers.persistance.datahandling import DataHandler

config_path = "config.yaml"
logger = logging.get_logger()
sleep = None


def process_request(cian_response, data_handler):
    logger.debug("Processing response")
    try:
        cian_results = cian_response.json().get('data')
        search_request_id = cian_results.get("searchRequestId")
        logger.info(f"Attempting to processing cian data for request id {search_request_id}")

        if search_request_id is not None:
            offers = cian_results.get('offersSerialized')

            data_handler.store_offers(new_offers=offers, search_request_id=search_request_id)
            logger.debug(f"Persisted {len(offers)} offers")

            cian_results.pop('offersSerialized', None)
            data_handler.store_metadata(cian_results)
            logger.info("Persisted metadata")

            # we do not care about performance, we'll need to limit the rate anyways
            logger.debug("Starting to extract image information")
            offers_to_process = len(offers)

            # get images that we already know
            stored_images = data_handler.get_known_image_ids(app_config.get_nested("locations.images_collection"))
            logger.info(f"{len(stored_images)} images in the image database")

            # for offer in offers:
            for counter, offer in enumerate(offers):
                # {image_id : blob }
                images_meta = data_handler.extract_image_information_from_offer(offer=offer, exclude=stored_images)
                logger.info(
                    f"For offer {counter + 1}/{offers_to_process}, {len(list(images_meta.keys()))} images to "
                    f"download, ~ {sleep.stats()['images_avg'] * len(list(images_meta.keys()))} seconds")

                for image_counter, image_id in enumerate(images_meta):
                    offer_id = offer.get("cianId", (offer.get("id"), None))
                    logger.debug(f"attempting to download and persist picture {image_id} for offer {offer_id}")

                    data_handler.store_images(images=cian.get_image({image_id: images_meta.get(image_id)}),
                                              offer_id=offer_id)

                    logger.info(f"{image_counter+1}/{len(list(images_meta.keys()))} images persisted")
                    sleep.images()
                if len(list(images_meta.keys())) != 0:
                    sleep.images()

    except Exception as e:
        logger.warning(f"response did not contain any data to work with and threw {e}")
        with open(f'data/failed/failed_{str(time.time())}.pickle', 'wb') as f:
            pickle.dump(cian_response, f, pickle.HIGHEST_PROTOCOL)
        raise


def iterate(regions: list, data_handler: DataHandler):
    try:
        logger.info("Attempting to pull the first page")
        cian_query = cian.RequestOffers(region_values=regions, page=1)
        cian_response = cian_query.get_offer_page()
        process_request(cian_response, data_handler)
    except Exception as e:
        logger.warning(f"Pulling and processing the data from the Cian's first offers page failed due to {e}")
        return

    sleep.offer_queries()

    try:
        for i in range(2, 1000):
            logger.info(f'\n---------------------------------------------------------\n '
                        f' --------------------- PULLING PAGE {i} ---------------------'
                        f' \n---------------------------------------------------------\n ')

            with open("lastpage.txt", "w") as f:
                f.write(str(i))
            f.close()

            cian_response = cian_query.get_next_offer_page()
            process_request(cian_response, data_handler)
            sleep.offer_queries()
    except Exception as e:
        logger.warning(f"Pulling and processing the following pages with data from cian failed due to {e}")


def main() -> None:
    app_config.load(config_path)
    global sleep
    sleep = CoolOff()

    region = 4998
    if app_config.get('storage') == 'mongodb':
        logger.info("MongoDB will be used for data persistence")
        persister = MongoHandler()
    else:
        logger.info("Local file storage will be used for data persistence")
        persister = FileHandler()

    data_handler = DataHandler(persister)
    iterate(regions=[region], data_handler=data_handler)
    logger.info("Cian response processing completed")


if __name__ == '__main__':
    # python -m unittest
    main()
