import kdtree
from flask import Flask, jsonify, request

from src.database import insert_location, create_database, get_locations, get_location_by_id
from src.location import Location

app = Flask(__name__)
create_database()
locations = get_locations()
tree = kdtree.create(locations, dimensions=2)


@app.route('/', methods=['GET'])
def get_all_locations():
    location_objects = get_locations()
    return jsonify([
        {
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name
        } for location in location_objects
    ])


@app.route('/<id>', methods=['GET'])
def get_single_location(id):
    location = get_location_by_id(id)
    return jsonify({
        'id': location.location_id,
        'lat': location.latitude,
        'lon': location.longitude,
        'name': location.name
    })


@app.route('/add/<lat>,<lon>', methods=['POST'])
def add_location(lat, lon):
    global tree
    name = request.args.get('name', None)
    location = Location(latitude=lat, longitude=lon, name=name)
    success = insert_location(location)

    if not success:
        return jsonify({'error': 'Could not add location'}), 500

    tree.add(location)
    tree = tree.rebalance()
    return jsonify({
        'success': 'Location added',
        'id': location.location_id,
    }), 200


if __name__ == '__main__':
    app.run()

    # city_hall = Location(29.760163, -95.369356, "City Hall")
    # closest_node = tree.search_nn(city_hall)
    # print(f"Closest node to {city_hall} is {closest_node[0]}")
