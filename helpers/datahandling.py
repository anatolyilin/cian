import helpers.logging as logging

logger = logging.get_logger()


class DataHandler:

    def __init__(self, persister):
        self._persister = persister

    def store_metadata(self, new_metadata, location=None):
        self._persister.store_metadata(new_metadata, location)

    def get_known_image_ids(self, location: None) -> list:
        return self._persister.get_known_image_ids(location)

    # by design, overwrite previous images with the same id.
    def store_images(self, images: dict, offer_id=None, location: str = None):
        return self._persister.store_images(images, offer_id, location)

    def store_offers(self, new_offers, search_request_id, location=None):
        return self._persister.store_offers(new_offers, search_request_id, location)

    def extract_image_information_from_offer(self, offer, exclude: list = None) -> dict:
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
