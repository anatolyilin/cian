import certifi
import fake_useragent
import requests
import json

# location = 'fake_useragent%s.json' % fake_useragent.VERSION
#
# ua = fake_useragent.UserAgent(path=location)
#
# print(ua.chrome)

headers = {
    "Accept": "*/*",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://sochi.cian.ru",
    "Cookie": "__cf_bm=FJNkZGoCnf7lThcjfcHfZCr4OQubYnlsTPqa5N0c0vs-1642011676-0-AXCoNmkGx2fdE8Z82HyJzMESR3t95PWwzeIwc5nC4SHlLZvHDzQxyjJeSxkYhxBOpZJzHzqmpp9DHzLO8VOkdJ0=; sopr_session=6adb14a2ea074e9a; sopr_utm=%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D; adb=1; session_main_town_region_id=1; session_region_id=1; serp_registration_trigger_popup=1; login_mro_popup=1; cf_chl_2=; cf_chl_prog=; cf_clearance=nUcXT3YhWeU3aQDaiaAw65tgUF.cKat.H9On0LJqb7s-1641404051-0-150; first_visit_time=1641295059125; _CIAN_GK=d056b7e5-2131-4b97-acb1-5d1f0e0b9a92",
    "Content-Length": "151",
    "Accept-Language": "en-GB,en;q=0.9",
    "Host": "api.cian.ru",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
    "Referer": "https://sochi.cian.ru/",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

url = "https://api.cian.ru/search-offers/v2/search-offers-desktop/"
# url = "http://127.0.0.1"
# url = "https://httpbin.org/anything"
# url = "https://httpbin.org/gzip"

query = {'jsonQuery':{'region':{'type':'terms','value':[4998]},'_type':'flatsale','engine_version':{'type':'term','value': 2},'page':{'type':'term','value':5}}}

# response = requests.post(url, headers=headers, data=json.dumps(query).replace(" ", ""))

try:
    response = requests.post(url, headers=headers, data=json.dumps(query).replace(" ", ""))
    response.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("HTTP error has occurred")
    raise SystemExit(err)
except requests.exceptions.RequestException as e:
    print("An exception has occurred:")
    raise SystemExit(e)

# import pdb; pdb.set_trace()

print(f'json: {response.json()}')

print(f'text: {response.text}')

response.close()

# ['apparent_encoding', 'close', 'connection', 'content', 'cookies', 'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect', 'is_redirect', 'iter_content', 'iter_lines', 'json', 'links', 'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request', 'status_code', 'text', 'url']


#
# curl "https://api.cian.ru/search-offers/v2/search-offers-desktop/" \
# -X 'POST' \
# -H 'Accept: */*' \
# -H 'Content-Type: text/plain;charset=UTF-8' \
# -H 'Origin: https://sochi.cian.ru' \
# -H 'Cookie: __cf_bm=FJNkZGoCnf7lThcjfcHfZCr4OQubYnlsTPqa5N0c0vs-1642011676-0-AXCoNmkGx2fdE8Z82HyJzMESR3t95PWwzeIwc5nC4SHlLZvHDzQxyjJeSxkYhxBOpZJzHzqmpp9DHzLO8VOkdJ0=; sopr_session=6adb14a2ea074e9a; sopr_utm=%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D; adb=1; session_main_town_region_id=1; session_region_id=1; serp_registration_trigger_popup=1; login_mro_popup=1; cf_chl_2=; cf_chl_prog=; cf_clearance=nUcXT3YhWeU3aQDaiaAw65tgUF.cKat.H9On0LJqb7s-1641404051-0-150; first_visit_time=1641295059125; _CIAN_GK=d056b7e5-2131-4b97-acb1-5d1f0e0b9a92' \
# -H 'Content-Length: 151' \
# -H 'Accept-Language: en-GB,en;q=0.9' \
# -H 'Host: api.cian.ru' \
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15' \
# -H 'Referer: https://sochi.cian.ru/' \
# -H 'Accept-Encoding: gzip, deflate, br' \
# -H 'Connection: keep-alive' \
# --data-binary '{"jsonQuery":{"region":{"type":"terms","value":[4998]},"_type":"flatsale","engine_version":{"type":"term","value":2},"page":{"type":"term","value":5}}}' > test2.json


