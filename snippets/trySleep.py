import time
import requests
import helpers.request as request
import unittest

my_request = request.Request(region_values=[123], page=1, url='http://127.0.0.1')

try:
    while True:
        print('executing. ')
        cian_response = my_request.get_next_offer_page()
        print('sleeping. ')
        time.sleep(1)
except requests.exceptions.HTTPError as e:
    print('done')


