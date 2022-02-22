import requests

BASE_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {'User-Agent': 'Distance Graph Model +https://github.com/tbrittain'}


def geocode(**kwargs):
    """
    Geocode an address using the Nominatim API.
    https://nominatim.org/release-docs/develop/api/Search/#parameters
    :param q: query string - overrides all other parameters
    :param street: street name
    :param city: city name
    :param state: state name
    :param country: country name
    :param postalcode: postal code
    """

    params = {
        "format": "json",
        "addressdetails": 1,
        "countrycodes": "us",
        "limit": 1
    }

    if "q" in kwargs:
        params["q"] = kwargs["q"]
    else:
        for key, value in kwargs.items():
            if value:
                params[key] = value

    resp = requests.get(url=BASE_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    if resp.json():
        return resp.json()[0]
    else:
        return None


def geocode_coords(**kwargs):
    """
    Geocode an address using the Nominatim API and only return the coordinates.
    https://nominatim.org/release-docs/develop/api/Search/#parameters
    :param q: query string - overrides all other parameters
    :param street: street name
    :param city: city name
    :param state: state name
    :param country: country name
    :param postalcode: postal code
    """
    resp = geocode(**kwargs)
    return float(resp["lat"]), float(resp["lon"])


if __name__ == '__main__':
    print(geocode_coords(q="1600 Pennsylvania Ave NW, Washington, DC 20500"))
