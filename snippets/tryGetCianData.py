import requests
import json
import yaml


def get_user_agent():
    import fake_useragent
    location = 'misc/fake_useragent%s.json' % fake_useragent.VERSION
    ua = fake_useragent.UserAgent(path=location)
    return ua.chrome


def get_header(user_agent):
    headers = {
        "Accept": "*/*",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://sochi.cian.ru",
        "Cookie": "__cf_bm=FJNkZGoCnf7lThcjfcHfZCr4OQubYnlsTPqa5N0c0vs-1642011676-0"
                  "-AXCoNmkGx2fdE8Z82HyJzMESR3t95PWwzeIwc5nC4SHlLZvHDzQxyjJeSxkYhxBOpZJzHzqmpp9DHzLO8VOkdJ0=; "
                  "sopr_session=6adb14a2ea074e9a; "
                  "sopr_utm=%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D; adb=1; "
                  "session_main_town_region_id=1; session_region_id=1; serp_registration_trigger_popup=1; "
                  "login_mro_popup=1; cf_chl_2=; cf_chl_prog=; "
                  "cf_clearance=nUcXT3YhWeU3aQDaiaAw65tgUF.cKat.H9On0LJqb7s-1641404051-0-150; "
                  "first_visit_time=1641295059125; _CIAN_GK=d056b7e5-2131-4b97-acb1-5d1f0e0b9a92",
        "Content-Length": "151",
        "Accept-Language": "en-GB,en;q=0.9",
        "Host": "api.cian.ru",
        "User-Agent": user_agent,
        "Referer": "https://sochi.cian.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    return headers


def get_cian_query():
    query = {'jsonQuery': {'region': {'type': 'terms', 'value': [4998]}, '_type': 'flatsale',
                           'engine_version': {'type': 'term', 'value': 2}, 'page': {'type': 'term', 'value': 5}}}
    return query


def get_url():
    url = "https://api.cian.ru/search-offers/v2/search-offers-desktop/"
    return url


try:
    response = requests.post(get_url(), headers=get_header(), data=json.dumps(get_cian_query()).replace(" ", ""))
    response.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("HTTP error has occurred")
    raise SystemExit(err)
except requests.exceptions.RequestException as e:
    print("An exception has occurred:")
    raise SystemExit(e)


