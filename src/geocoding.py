import requests

BASE_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {'User-Agent': 'Distance Tree Model +github.com/tbrittain/distance-tree-model'}


def geocode(query=None, street=None, city=None, state=None, zipcode=None):
    """
    Geocode an address using the Nominatim API.
    https://nominatim.org/release-docs/develop/api/Search/#parameters

    :param query: query string - overrides all other parameters
    :param street: street name
    :param city: city name
    :param state: state name
    :param zipcode: zip code
    """

    params = {
        "format": "json",
        "addressdetails": 1,
        "countrycodes": "us",
        "limit": 1
    }

    if query:
        params["q"] = query
    else:
        if street:
            params["street"] = street
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zipcode:
            params["postalcode"] = zipcode

    resp = requests.get(url=BASE_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    if resp.json():
        return resp.json()[0]
    else:
        return None
