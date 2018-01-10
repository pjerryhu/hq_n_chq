
from googleapiclient.discovery import build
import pprint


my_api_key = "AIzaSyBv7qDkBUXiysQQqsPcgXCcFB9svNeTl4k"
my_cse_id = "012086291608697037198:z2impkka__g"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

results = google_search(
    'In the hit Beatles song, what is "Lucy in the Sky" with? "Diamonds"', \
    my_api_key, my_cse_id, num=10)

# for result in results:
results = map(lambda result: result['snippet'], results)
# pprint.pprint(results)
print (results)


