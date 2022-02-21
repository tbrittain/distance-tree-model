import kdtree
from flask import Flask

from src.database import insert_location, create_database, get_locations
from src.location import Location

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    create_database()
    app.run()

    # Some constants of latitude and longitude
    # https://www.latlong.net/convert-address-to-lat-long.html
    locations = get_locations()

    tree = kdtree.create(locations, dimensions=2)

    city_hall = Location(None, 29.760163, -95.369356, "City Hall")
    closest_node = tree.search_nn(city_hall)
    print(f"Closest node to {city_hall} is {closest_node[0]}")
