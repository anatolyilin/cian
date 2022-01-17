import unittest
import time
import responses
from responses import matchers
import requests
import tempfile
import os
from pathlib import Path
from library.configuration import app_config
import library.request as cian


class TestRequest(unittest.TestCase):

    def test_cian_offers_header(self):
        cookie = "my_secret_cookie"
        expected_header = {
            "Accept": "*/*",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://sochi.cian.ru",
            "Cookie": cookie,
            "Content-Length": "151",
            "Accept-Language": "en-GB,en;q=0.9",
            "Host": "api.cian.ru",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Referer": "https://sochi.cian.ru/",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"}
        generated_header = cian.create_cian_offers_header(cookie)
        self.assertEqual(expected_header, generated_header, "Generated cian header does not look right")

        custom_ua = "my_custom_ua"
        expected_header = {
            "Accept": "*/*",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://sochi.cian.ru",
            "Cookie": cookie,
            "Content-Length": "151",
            "Accept-Language": "en-GB,en;q=0.9",
            "Host": "api.cian.ru",
            "User-Agent": custom_ua,
            "Referer": "https://sochi.cian.ru/",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"}
        generated_header = cian.create_cian_offers_header(cookie, custom_ua)
        self.assertEqual(expected_header, generated_header, "Generated cian header does not look right")

    def test_cian_image_header(self):
        expected_header = {
            "Accept": "image/webp,image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "cdn-p.cian.site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Accept-Language": "en-GB,en;q=0.9",
            "Referer": "https://sochi.cian.ru/",
            "Connection": "keep-alive"
        }
        generated_header = cian.create_cian_image_header()
        self.assertEqual(expected_header, generated_header, "Generated cian header does not look right")

    def test_cian_query(self):
        region_value = [1227, 24]
        house_type = "my_house"
        page = 24
        expected = {'jsonQuery': {'region': {'type': 'terms', 'value': region_value}, '_type': house_type,
                                  'engine_version': {'type': 'term', 'value': 2},
                                  'page': {'type': 'term', 'value': page}}}

        self.assertEqual(expected, cian.create_cian_query(page, house_type, region_value),
                         "Geneated cian query does not look right")

    def test_request_class(self):
        app_config.load("test/test_config.yaml")
        cian_request = cian.RequestOffers([1227])
        self.assertIsNotNone(cian_request.url)
        self.assertIsNotNone(cian_request.user_agent)
        self.assertIsNotNone(cian_request.cookie)
        self.assertIsNotNone(cian_request.house_type)
        self.assertIsNotNone(cian_request.region_values)
        self.assertIsNotNone(cian_request.page)
        self.assertIsNotNone(cian_request.headers)
        self.assertIsNotNone(cian_request.query)

        expected_query = {'jsonQuery': {'region': {'type': 'terms', 'value': [1227]}, '_type': 'flatsale',
                                        'engine_version': {'type': 'term', 'value': 2},
                                        'page': {'type': 'term', 'value': 1}}}

        self.assertEqual(cian_request.query, expected_query)

        expected_headers = {
            "Accept": "*/*",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://sochi.cian.ru",
            "Cookie": "my-super-secret-cookie-1234",
            "Content-Length": "151",
            "Accept-Language": "en-GB,en;q=0.9",
            "Host": "api.cian.ru",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
            "Referer": "https://sochi.cian.ru/",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"}

        self.assertEqual(cian_request.headers, expected_headers)

    def test_get_image(self):
        # known existing image we can pull
        url = "https://i.imgur.com/ExdKOOz.png"
        response = cian._get(url, headers={})

        fd, path = tempfile.mkstemp()
        try:
            with open(path, 'wb') as f:
                f.write(response.content)

            self.assertTrue(Path(path).is_file())
            self.assertTrue(os.path.getsize(path) > 0)

        finally:
            os.remove(path)

    @responses.activate
    def test_get_images_fun(self):
        mock_response = b"blablablablablablabla"
        responses.add(responses.GET, 'http://127.0.0.1',
                      body=mock_response, status=200)

        data = {123: 'http://127.0.0.1'}
        modified_data = cian.get_images(data, delay=1, delay_max=1)
        self.assertEqual(data, modified_data)

        mock_response = None
        responses.add(responses.GET, 'http://127.0.0.2',
                      body=mock_response, status=500)

        data = {123: 'http://127.0.0.2'}
        modified_data = cian.get_images(data, delay=1, delay_max=1)
        # if picture could not be downloaded, it should keep url in place
        self.assertEqual(data, modified_data)

    @responses.activate
    def test_execute(self):
        mock_response = {'status': 'OK'}
        responses.add(responses.POST, 'http://127.0.0.1',
                      json=mock_response, status=200)

        response = cian._post(url='http://127.0.0.1',
                              headers={'header': 'yes'},
                              query={'query': 'yes'})

        self.assertEqual(response.json(), mock_response)

        responses.add(responses.POST, 'http://127.0.0.2',
                      json=mock_response, status=500)

        with self.assertRaises(requests.exceptions.HTTPError):
            cian._post(url='http://127.0.0.2',
                       headers={'header': 'yes'},
                       query={'query': 'yes'})

    @responses.activate
    def test_execute_next(self):
        app_config.load("test/test_config.yaml")
        cian_request = cian.RequestOffers([1227])

        self.assertEqual(cian_request.page, 1)

        mock_response = {'status': 'OK'}
        responses.add(responses.POST, 'http://127.0.0.1',
                      json=mock_response, status=200)

        response = cian_request.get_next_offer_page()

        self.assertEqual(cian_request.page, 2)
        self.assertEqual(response.json(), mock_response)

    @responses.activate
    def test_execute(self):
        # mock_response = {'status': 'OK'}
        # responses.add(responses.POST, 'http://127.0.0.1',
        #               json=mock_response, status=200)

        mock_response = {'status': 'NOGO'}
        responses.add(responses.POST, 'http://127.0.0.1',
                      json=mock_response, status=400,
                      match=[matchers.json_params_matcher({'jsonQuery': {'region': {'type': 'terms', 'value': [123]},
                                                                         '_type': 'flatsale',
                                                                         'engine_version': {'type': 'term', 'value': 2},
                                                                         'page': {'type': 'term', 'value': 1}}})])

        my_request = cian.RequestOffers(region_values=[123], page=1, url='http://127.0.0.1')
        print("trying")
        try:
            while True:
                print('executing. ')
                print(my_request.get_offer_page())
                print('sleeping. ')
                time.sleep(1)
        except requests.exceptions.HTTPError as e:
            print(f'done {e}')


if __name__ == '__main__':
    unittest.main()
