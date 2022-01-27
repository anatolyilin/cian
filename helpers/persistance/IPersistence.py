from abc import ABC, abstractmethod


class IPersistence(ABC):

    @abstractmethod
    def exists(self, path):
        pass

    @abstractmethod
    def store_metadata(self, new_metadata: dict, location: str = None):
        pass

    @abstractmethod
    def get_known_image_ids(self, location) -> list:
        pass

    @abstractmethod
    def store_images(self, images: dict, offer_id=None, location: str = None):
        pass

    @abstractmethod
    def store_offers(self, new_offers: list, search_request_id: str, location: str = None):
        pass
