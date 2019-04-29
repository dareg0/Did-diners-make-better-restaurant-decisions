import requests
import json
import requests
import sys
import urllib

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

# API constants
# https://api.yelp.com/v3/businesses/search
# https://api.yelp.com/v3/businesses/{id}/reviews
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

SEARCH_LIMIT = 3

file = open('my_key.txt', 'r')
api_key = file.read().strip()
# print(api_key)
file.close()

headers = {'Authorization': 'Bearer %s' % api_key}

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search (api_key, term, location, phone, sort_by='best_match'):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        sort_by (str): How to filter search results.

    Returns:
        dict: The JSON response from the request.
    """

    try:
        term = term.replace(' ', '+')
    except AttributeError:  # if not str
        term = str(term)

    try:
        location = location.replace(' ', '+')
    except AttributeError:  # if not str
        location = str(location)

    try:
        phone = '+1'+phone.replace('-','')
    except AttributeError:  # if not str
        phone = str(phone)

    url_params = {
        'term':term,
        'location':location,
        'phone':phone,
        'limit':SEARCH_LIMIT,
        'sort_by':sort_by
        }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_business(api_key, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)

def get_business_match (api_key, term, location, phone, sort_by='best_match'):
    """Queries API for best match among businesses.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
        sort_by (str): How to filter search results.

    Returns:
        dict: The first JSON response from the request.
    """
    response = search(api_key, term, location, phone, sort_by)
    businesses = response.get('businesses')

    if not businesses:
        return None

    return businesses[0]

def query_api(search_term, location, phone):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    try:
        rest_id = get_business_match(api_key, search_term, location, phone)['id']
        rest_info = get_business(api_key, rest_id)
        print(rest_info.get('name'))
        rating = rest_info.get('rating')
        review_count = rest_info.get('review_count')
        price = rest_info.get('price')
        print(review_count)
        print(rating)
        print(price)
    except AttributeError:
        rating = ""
        review_count = ""
        price = ""
    except HTTPError as error:
        sys.exit(
              'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                    error.code,
                    error.url,
                    error.read(),
                    )
              )

def test(search_term, location, phone):
    try:
        business_id = get_business_match(api_key, search_term, location, phone)
        print('Business id for best match of below params = {0}\n' \
              'Search Term: {1}\nLocation: {2}\n'.format(
              business_id, search_term, location))
        business_info = get_business(api_key, business_id)
        rating = business_info.get('rating')
        price = business_info.get('price')
        print(rating)
        print(price)

    except HTTPError as error:
        sys.exit(
              'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                    error.code,
                    error.url,
                    error.read(),
                    )
              )

# def main():
#     for i, rest in unique_rest.iloc[70:80].iterrows():
#       camis = rest['CAMIS']
#       name = rest['DBA']
#       print(name)
#       phone = rest['PHONE']
#       loc = rest['Location']
#       query_api(name, loc, phone)

# if __name__ == '__main__':
    # main()
