import kdtree
from flask import Flask, jsonify, request
from time import time

from src.database import insert_location, create_database, get_locations, get_location_by_id, delete_location_by_id
from src.geocoding import geocode
from src.location import Location

app = Flask(__name__)
create_database()
locations = get_locations()
tree = kdtree.create(locations, dimensions=2)


@app.route('/', methods=['GET'])
def get_all_locations():
    begin = time()
    location_objects = get_locations()
    response = jsonify([
        {
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name,
            'description': location.description
        } for location in location_objects
    ])
    end = time()
    diff = round((end - begin) * 1000, 5)
    response.headers['X-Execution-Time'] = f'{diff}ms'
    return response


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
    begin = time()
    location = get_location_by_id(id)
    if not location:
        return jsonify({'error': 'No location found'}), 404
    else:
        response = jsonify({
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name,
            'description': location.description
        })
        end = time()
        diff = round((end - begin) * 1000, 5)
        response.headers['X-Execution-Time'] = f'{diff}ms'
        return response


@app.route('/location', methods=['POST'])
def add_location():
    global tree
    query = request.args.get('query', type=str)
    street = request.args.get('street', type=str)
    city = request.args.get('city', type=str)
    state = request.args.get('state', type=str)
    zipcode = request.args.get('zipcode', type=str)
    description = request.args.get('description', type=str)

    if not any([query, street, city, state, zipcode]):
        return jsonify({'error': 'No location/query specified'}), 400

    if query:
        search_result = geocode(query=query)
    else:
        search_result = geocode(street=street, city=city, state=state, zipcode=zipcode)

    if not search_result:
        return jsonify({'error': 'No location found'}), 400

    begin = time()
    name = search_result['display_name']
    lat = float(search_result['lat'])
    lon = float(search_result['lon'])
    location = Location(latitude=lat, longitude=lon, name=name, description=description)

    success = insert_location(location)
    if not success:
        return jsonify({'error': 'Could not add location'}), 500

    tree.add(location)
    if not tree.is_balanced:
        tree = tree.rebalance()

    response = jsonify({
        'success': 'Location added',
        'location': {
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name
        }
    })
    end = time()
    diff = round((end - begin) * 1000, 5)
    response.headers['X-Execution-Time'] = f'{diff}ms'
    return response


@app.route('/location/<float:latitude>/<float:longitude>', methods=['POST'])
def add_location_raw(latitude, longitude):
    global tree
    name = request.args.get('name', type=str)
    description = request.args.get('description', type=str)
    begin = time()
    location = Location(latitude=latitude, longitude=longitude, name=name, description=description)

    success = insert_location(location)
    if not success:
        return jsonify({'error': 'Could not add location'}), 500

    tree.add(location)
    if not tree.is_balanced:
        tree = tree.rebalance()

    response = jsonify({
        'success': 'Location added',
        'location': {
            'id': location.location_id,
            'lat': location.latitude,
            'lon': location.longitude,
            'name': location.name,
            'description': location.description
        }
    })
    end = time()
    diff = round((end - begin) * 1000, 5)
    response.headers['X-Execution-Time'] = f'{diff}ms'
    return response


@app.route('/location/<id>', methods=['DELETE'])
def delete_location(id):
    begin = time()
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

    response = jsonify({'success': 'Location deleted'})
    end = time()
    diff = round((end - begin) * 1000, 5)
    response.headers['X-Execution-Time'] = f'{diff}ms'
    return response


@app.route('/nearest', methods=['GET'])
def get_k_nearest_neighbors():
    global tree
    query = request.args.get('query', type=str)
    street = request.args.get('street', type=str)
    city = request.args.get('city', type=str)
    state = request.args.get('state', type=str)
    zipcode = request.args.get('zipcode', type=str)

    if not any([query, street, city, state, zipcode]):
        return jsonify({'error': 'No location/query specified'}), 400

    if query:
        search_result = geocode(query=query)
    else:
        search_result = geocode(street=street, city=city, state=state, zipcode=zipcode)

    if not search_result:
        return jsonify({'error': 'No location found'}), 400

    begin = time()
    name = search_result['display_name']
    lat = float(search_result['lat'])
    lon = float(search_result['lon'])
    location = Location(latitude=lat, longitude=lon, name=name)

    k = request.args.get('k', type=int)
    if not k:
        k = 10

    neighbors = tree.search_knn(location, k)
    if not neighbors:
        return jsonify({'error': 'No neighbors found'}), 404
    else:
        response = jsonify({
            'success': f'Found {len(neighbors)} nearest neighbors',
            'neighbors': [
                {
                    'location': {
                        'id': neighbor[0].data.location_id,
                        'lat': neighbor[0].data.latitude,
                        'lon': neighbor[0].data.longitude,
                        'name': neighbor[0].data.name,
                        'description': neighbor[0].data.description
                    },
                    'distance_miles': Location.distance(location, neighbor[0].data),
                    'distance_euclidean': neighbor[1]
                } for neighbor in neighbors
            ],
            'search-location': {
                'lat': location.latitude,
                'lon': location.longitude,
                'name': location.name
            }
        })
        end = time()
        diff = round((end - begin) * 1000, 5)
        response.headers['X-Execution-Time'] = f'{diff}ms'
        return response


if __name__ == '__main__':
    app.run(debug=True)
