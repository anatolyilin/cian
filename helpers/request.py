import requests
import json
import time
from random import randrange

from helpers.configuration import app_config
import helpers.logging as logging

logger = logging.get_logger()


def create_cian_offers_header(cookie,
                              user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ("
                                         "KHTML, like Gecko) Version/15.2 Safari/605.1.15") -> dict:
    headers = {
        "Accept": "*/*",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://sochi.cian.ru",
        "Cookie": cookie,
        "Content-Length": "151",
        "Accept-Language": "en-GB,en;q=0.9",
        "Host": "api.cian.ru",
        "User-Agent": user_agent,
        "Referer": "https://sochi.cian.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    logger.debug(f"Generated Curl request header {headers}")
    return headers


def create_cian_image_header(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ("
                                        "KHTML, like Gecko) Version/15.2 Safari/605.1.15") -> dict:
    headers = {
        "Accept": "image/webp,image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "cdn-p.cian.site",
        "User-Agent": user_agent,
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://sochi.cian.ru/",
        "Connection": "keep-alive"
    }
    logger.debug(f"Generated Curl request header {headers}")
    return headers


'''
curl 'https://cdn-p.cian.site/images/51/866/811/kvartira-centralnyy-gorkogo-pereulok-1186681538-2.jpg' \
-X 'GET' \
-H 'Accept: image/webp,image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Host: cdn-p.cian.site' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15' \
-H 'Accept-Language: en-GB,en;q=0.9' \
-H 'Referer: https://sochi.cian.ru/' \
-H 'Connection: keep-alive'
'''


def create_cian_query(page=1, house_type='flatsale', region_values=None) -> dict:
    if region_values is None:
        logger.debug("No region has been provided, falling back to the region 4998.")
        region_values = [4998]
    query = {'jsonQuery': {'region': {'type': 'terms', 'value': region_values}, '_type': house_type,
                           'engine_version': {'type': 'term', 'value': 2}, 'page': {'type': 'term', 'value': page}}}
    logger.debug(f"Generated curl query {query}")
    return query


def _post(url, headers, query):
    logger.debug("Attempting to execute the curl POST command")
    logger.debug(f"with header \n {headers}, \n and query \n {query}")
    response = None
    try:
        response = requests.post(url,
                                 headers=headers,
                                 data=json.dumps(query).replace(" ", ""))
        # check if it is 200 OK, if not, fail the execution, there is no need to proceed
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.warning(f"Curl POST failed, unable pull data due to {err}")
        raise
    except requests.exceptions.RequestException as e:
        logger.warning(f"Curl POST failed, unable pull data due to {e}")
    return response


def _get(url, headers):
    logger.debug("Attempting to execute the curl GET command")
    logger.debug(f"with header \n {headers}")
    response = None
    try:
        response = requests.get(url, headers=headers)
        # check if it is 200 OK, if not, fail the execution, there is no need to proceed
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.warning(f"Curl GET failed, unable pull data due to {err}")
        raise
    except requests.exceptions.RequestException as e:
        logger.warning(f"Curl GET failed, unable pull data due to {e}")
    return response


# expecting images_url as a dict with k = image_id and v = URL
def get_images(images, delay=5, delay_max=None) -> dict:
    logger.info(f"Attempting to pull {len(list(images.keys()))} images")
    header = create_cian_image_header()

    images_to_download = len(list(images.keys()))
    for counter, image_id in enumerate(list(images.keys())):
        logger.info(f"Downloading image {counter + 1}/{images_to_download} - id {image_id} with URL: {images.get(image_id)}")
        try:
            images[image_id] = _get(images.get(image_id), header).content
            if delay_max:
                sleep_time = randrange(delay, delay_max)
                logger.info(f'Cool off for {sleep_time} seconds to pull the next image')
                time.sleep(sleep_time)
            else:
                logger.info(f'Cool off for {delay} seconds to pull the next image')
                time.sleep(delay)
        except Exception as e:
            logger.warning(f"Failed to pull image {image_id} - {images.get(image_id)}, due to {e}")

    logger.info(f"{len(list(images.keys()))} images downloaded")
    return images


class RequestOffers:
    def __init__(self, region_values, page=1, house_type='flatsale', user_agent=None, url=None, cookie=None):
        logger.debug("Gerenating Cian query")
        if url is None:
            url = app_config.get_nested("request.url")
        if user_agent is None:
            user_agent = app_config.get_nested("request.user_agent")
        if cookie is None:
            config_cookie = app_config.get_nested("request.cookie")
            cookie = "__cf_bm=FJNkZGoCnf7lThcjfcHfZCr4OQubYnlsTPqa5N0c0vs-1642011676-0" \
                     "-AXCoNmkGx2fdE8Z82HyJzMESR3t95PWwzeIwc5nC4SHlLZvHDzQxyjJeSxkYhxBOpZJzHzqmpp9DHzLO8VOkdJ0=; " \
                     "sopr_session=6adb14a2ea074e9a; " \
                     "sopr_utm=%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D; adb=1; " \
                     "session_main_town_region_id=1; session_region_id=1; serp_registration_trigger_popup=1; " \
                     "login_mro_popup=1; cf_chl_2=; cf_chl_prog=; " \
                     "cf_clearance=nUcXT3YhWeU3aQDaiaAw65tgUF.cKat.H9On0LJqb7s-1641404051-0-150; " \
                     "first_visit_time=1641295059125; _CIAN_GK=d056b7e5-2131-4b97-acb1-5d1f0e0b9a92"
            if config_cookie is not None:
                cookie = config_cookie

        self.url = url
        self.cookie = cookie
        self.page = page
        self.house_type = house_type
        self.region_values = region_values
        self.user_agent = user_agent

        self.headers = create_cian_offers_header(self.cookie, self.user_agent)
        self.query = create_cian_query(self.page, self.house_type, self.region_values)

        logger.debug("Generated query object"
                     "url {url}"
                     "cookie {cookie}"
                     "user agent {user_agent}"
                     "page {page}"
                     "house_type {house_type}"
                     "region_values {region_values}"
                     "headers {headers}"
                     "query {query}".format(url=self.url,
                                            cookie=self.cookie,
                                            user_agent=self.user_agent,
                                            page=self.page,
                                            house_type=self.house_type,
                                            region_values=self.region_values,
                                            headers=self.headers,
                                            query=self.query
                                            ))

    def get_offer_page(self):
        logger.info("Attempting to pull the page")
        logger.debug("Attempting to generate the query")
        self.query = create_cian_query(self.page, self.house_type, self.region_values)
        return _post(self.url, self.headers, self.query)

    def get_next_offer_page(self):
        self.page += 1
        logger.info(f"Attempting to pull the next page: {self.page}")
        return self.get_offer_page()
