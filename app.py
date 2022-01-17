import pickle
import time
from random import randrange

from helpers.configuration import app_config
import helpers.mongodb as mongodb
import helpers.request as cian
import helpers.logging as logging
import helpers.datahandling as dh

config_path = "config.yaml"
logger = logging.get_logger()


def process_request(cian_response):
    cooloff_max = app_config.get_nested("cooloff.image.max")
    cooloff_min = app_config.get_nested("cooloff.image.min")

    cooldown_avg = (cooloff_max + cooloff_min) / 2.0

    try:
        cian_results = cian_response.json().get('data')
        search_request_id = cian_results.get("searchRequestId")
        logger.info(f"Attempting to processing cian data for request id {search_request_id}")
        if search_request_id is not None:
            offers = cian_results.get('offersSerialized')
            dh.store_offers(new_offers=offers, search_request_id=search_request_id)
            logger.debug(f"Stored {len(offers)} offers to file")

            cian_results.pop('offersSerialized', None)
            dh.store_metadata(cian_results)
            logger.info("Stored metadata")

            # we do not care about performance, we'll need to limit the rate anyways
            logger.debug("Starting to extract image information")
            offers_to_process = len(offers)

            # get images that we already know
            stored_images = dh.get_known_image_ids()
            logger.info(f"Found {len(stored_images)} images in the image database")
            # for offer in offers:
            for counter, offer in enumerate(offers):
                images_meta = dh.extract_image_information_from_offer(offer=offer, exclude=stored_images)
                logger.info(
                    f"For offer {counter + 1}/{offers_to_process}, {len(list(images_meta.keys()))} images to "
                    f"download, ~ {cooldown_avg*len(list(images_meta.keys()))} seconds")
                if len(list(images_meta.keys())) > 0:
                    logger.debug(f"extract image information {images_meta}, attempting to download data")
                    images = cian.get_images(images_meta, delay=cooloff_min, delay_max=cooloff_max)
                    logger.debug(f"attempting to persist images with ids: {list(images_meta.keys())}")
                    dh.store_images(images)
                    time.sleep(randrange(10, 45))
    except Exception as e:
        logger.warning(f"response did not contain any data to work with and threw {e}")
        with open(f'data/failed/failed_{str(time.time())}.pickle', 'wb') as f:
            pickle.dump(cian_response, f, pickle.HIGHEST_PROTOCOL)


def iterate(cian_request, current_page=1):
    try:
        logger.info("Pulling the first page")
        cian_response = cian_request.get_offer_page()
        process_request(cian_response)
    except Exception as e:
        logger.warning(f"Pulling and processing the data from cian failed due to {e}")

    sleep_time = randrange(25, 300)
    logger.info(f'sleeping for {sleep_time} seconds')
    time.sleep(sleep_time)
    logger.info("First page succeed, proceeding with pulling the following pages of the data..")
    try:
        for i in range(2, 3):
            logger.info(f'\n---------------------------------------------------------\n '
                        ' --------------------- PULLING PAGE {i} ---------------------'
                        ' \n---------------------------------------------------------\n ')
            cian_response = cian_request.get_next_offer_page()
            process_request(cian_response)
            sleep_time = randrange(25, 60)
            logger.info(f'sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)
    except Exception as e:
        logger.warning(f"Pulling and processing the following pages with data from cian failed due to {e}")


def main() -> None:
    app_config.load(config_path)
    # connection = mongodb.getConnection()
    # logger.info('Database connection ready to go')
    region = 4998
    logger.info("Preparing to pull the data")
    cian_query = cian.RequestOffers(region_values=[region], page=1)
    logger.info('Cian query ready to go')
    iterate(cian_query, 1)
    logger.info("Cian response processing completed")


if __name__ == '__main__':
    main()
