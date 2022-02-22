import kdtree
from flask import Flask, jsonify, request
import json

from src.database import insert_location, create_database, get_locations, get_location_by_id, delete_location_by_id
from src.geocoding import geocode
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


@app.route('/tree-status', methods=['GET'])
def get_tree_stats():
    return jsonify({
        'height': tree.height(),
        'is_valid': tree.is_valid(),
        'is_balanced': tree.is_balanced,
        'root-node': tree.data.__dict__ if tree.data else None,
    })


@app.route('/<id>', methods=['GET'])
def get_single_location(id):
    location = get_location_by_id(id)
    if not location:
        return jsonify({'error': 'No location found'}), 404
    else:
        return jsonify({
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name,
        })


@app.route('/location', methods=['POST'])
def add_location():
    global tree
    q = request.args.get('q', type=str)
    street = request.args.get('street', type=str)
    city = request.args.get('city', type=str)
    state = request.args.get('state', type=str)
    country = request.args.get('country', type=str)
    zipcode = request.args.get('zipcode', type=str)

    if not any([q, street, city, state, country, zipcode]):
        return jsonify({'error': 'No location/query specified'}), 400

    if q:
        search_result = geocode(q=q)
    else:
        search_result = geocode(street=street, city=city, state=state, country=country, zipcode=zipcode)

    if not search_result:
        return jsonify({'error': 'No location found'}), 400

    name = search_result['display_name']
    lat = float(search_result['lat'])
    lon = float(search_result['lon'])
    location = Location(name=name, latitude=lat, longitude=lon)

    success = insert_location(location)
    if not success:
        return jsonify({'error': 'Could not add location'}), 500

    tree.add(location)
    if not tree.is_balanced:
        tree = tree.rebalance()

    return jsonify({
        'success': 'Location added',
        'location': {
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name
        }
    }), 200


@app.route('/location/<id>', methods=['DELETE'])
def delete_location(id):
    global tree
    location = get_location_by_id(id)
    if not location:
        return jsonify({'error': 'No location found'}), 400

    success = delete_location_by_id(id)
    if not success:
        return jsonify({'error': 'Could not delete location'}), 500

    tree.remove(location)
    if not tree.is_balanced:
        tree = tree.rebalance()

    return jsonify({'success': 'Location deleted'}), 200


if __name__ == '__main__':
    app.run()

    # city_hall = Location(29.760163, -95.369356, "City Hall")
    # closest_node = tree.search_nn(city_hall)
    # print(f"Closest node to {city_hall} is {closest_node[0]}")
