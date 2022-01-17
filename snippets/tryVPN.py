import requests

try:
    ip = requests.get('https://api.ipify.org')
    ip.raise_for_status()
except requests.exceptions.HTTPError as err:
    print("HTTP error has occurred")
    raise SystemExit(err)
except requests.exceptions.RequestException as e:
    print("An exception has occurred:")
    raise SystemExit(e)

# try:
#     ip = perform_request(retry_counter)
# except requests.exceptions.Timeout:
#     # Maybe set up for a retry, or continue in a retry loop
# except requests.exceptions.TooManyRedirects:
#     # Tell the user their URL was bad and try a different one
# except requests.exceptions.RequestException as e:
#     # catastrophic error. bail.
#     raise SystemExit(e)

print(f'status code is: {ip.status_code}')
print(f'My ip is: {ip.text}')


