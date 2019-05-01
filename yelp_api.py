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


def search(api_key, term, location, phone, sort_by='best_match'):
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
        phone = '+1' + phone.replace('-', '')
    except AttributeError:  # if not str
        phone = str(phone)

    url_params = {
        'term': term,
        'location': location,
        'phone': phone,
        'limit': SEARCH_LIMIT,
        'sort_by': sort_by
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


def get_business_match(api_key, term, location, phone, sort_by='best_match'):
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


def get_reviews(api_key, business_id):
    try:
        reviews = request(API_HOST, BUSINESS_PATH + business_id +
                          '/reviews', api_key)["reviews"]
    except AttributeError:
        pass
    except TypeError:
        pass
    return reviews


def query_api(search_term, location, phone):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    rest_info = None
    reviews = None
    try:
        match = get_business_match(api_key, search_term, location, phone)
        rest_id = match['id']
        rest_info = get_business(api_key, rest_id)
        reviews = get_reviews(api_key, rest_id)
    except AttributeError:
        pass
    except TypeError:
        pass
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )
    return rest_info, reviews
