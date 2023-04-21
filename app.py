import json
import requests
import plant as pl
import seller as sl
import plants_shop as p_shop
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

plant_shop = p_shop.PlantShop()


# ENDPOINTS
# /plants
# /sellers
# /plants/<int:plant_id>
# /sellers/<int:seller_id>
# /plants/<int:plant_id>/sellers
# /plants/<int:plant_id>/sellers/<int:seller_id>


# HTTP GET method functions
@app.get('/plants')
def show_plants():
    plants = plant_shop.make_plants_dict()
    if not plants:
        return jsonify({'message': 'No plants found'}), 404
    return jsonify(plants), 200


@app.get('/sellers')
def show_sellers():
    sellers = plant_shop.make_sellers_dict()
    if not sellers:
        return jsonify({'message': 'No sellers found'}), 404
    return jsonify(sellers), 200


@app.get('/plants/<int:plant_id>')
def show_specific_plant(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        return jsonify({'message': 'Plant not found'}), 404

    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    return jsonify(plant_dict), 200


@app.get('/sellers/<int:seller_id>')
def show_specific_seller(seller_id):
    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        return jsonify({'message': 'Seller not found'}), 404

    seller_dict = plant_shop.get_seller_dict_by_id(seller_id=seller_id)
    return jsonify(seller_dict), 200


@app.get('/plants/<int:plant_id>/sellers')
def show_plant_sellers(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        return jsonify({'message': 'Plant not found'}), 404

    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    sellers_dict = plant_dict.get('sellers', [])
    return jsonify(sellers_dict), 200


@app.get('/plants/<int:plant_id>/sellers/<int:seller_id>')
def show_plant_specific_seller(plant_id, seller_id):
    # Check if plant and seller exists
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        return jsonify({'message': 'Plant not found'}), 404

    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        return jsonify({'message': 'Seller not found'}), 404

    # Return json
    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    sellers_dict = plant_dict['sellers']
    for seller in sellers_dict:
        if seller['id'] == seller_id:
            return jsonify(seller)

    return jsonify({'message': 'Seller not found for this plant'}), 404


# HTTP POST method functions
@app.post('/plants')
def create_plant():
    data = request.get_json()
    if len(data) == 4 and 'id' in data:
        del data['id']

    # Check if json is correct
    if len(data) != 3 or 'name' not in data or 'type' not in data or 'sellers' not in data:
        message = "Bad request, incorrect plant object given"
        return jsonify({"Failure": message}), 400

    # Check if sellers exists in plant_shop.sellers
    seller_ids = {seller.id for seller in plant_shop.sellers}
    if not all(seller['id'] in seller_ids for seller in data['sellers']):
        message = "Seller is not found in plant_shop"
        return jsonify({"Failure": message}), 404

    # Append new plant to the list
    sellers_list = plant_shop.from_dict_to_sellers_objects(data['sellers'])
    new_plant = pl.Plant(data['name'], data['type'], sellers_list)
    plant_shop.plants.append(new_plant)

    # Return a JSON response containing information about the newly created plant
    response_data = {
        'id': new_plant.id,
        'name': new_plant.name,
        'type': new_plant.type,
        'sellers': new_plant.sellers_dict()
    }
    return jsonify(response_data), 201, {"location": f"/plants/{new_plant.id}"}


@app.post('/sellers')
def add_seller():
    data = request.get_json()
    if len(data) == 3 and 'id' in data:
        del data['id']

    # Check if JSON object contains the required fields
    if not all(field in data for field in ['name', 'surname']):
        return jsonify({'error': 'Name and surname fields are required.'}), 400

    new_seller = sl.Seller(data['name'], data['surname'])
    plant_shop.sellers.append(new_seller)

    # Return a JSON response containing information about the newly created seller
    response_data = {
        'id': new_seller.id,
        'name': new_seller.name,
        'surname': new_seller.surname
    }
    return jsonify(response_data), 201, {"location": f"/sellers/{new_seller.id}"}


@app.post('/plants/<int:plant_id>/sellers')
def add_seller_to_plant(plant_id):
    data = request.get_json()

    plant = plant_shop.get_plant_by_id(plant_id)
    # Check if plant exists
    if not plant:
        message = "Plant not found"
        return jsonify({"error": message}), 404

    # Check if data is valid
    if not all(key in data for key in ('id', 'name', 'surname')):
        message = "Bad request, incorrect seller object given"
        return jsonify({"error": message}), 400

    # Check if seller exists in plant's sellers list
    if plant.find_seller(data['id']):
        message = "Bad request, seller already exists on plant's sellers list"
        return jsonify({"error": message}), 400

    # Check if seller exists in plant_shop.sellers
    seller = plant_shop.get_seller_by_id(data['id'])
    if not seller or seller.name != data['name'] or seller.surname != data['surname']:
        message = "Seller not found"
        return jsonify({"error": message}), 404

    # Add seller to plant's sellers list
    plant.sellers.append(seller)
    return jsonify(seller.__dict__()), 201, {"location": f"/sellers/{seller.id}"}


# HTTP PUT method functions
@app.put('/plants/<int:plant_id>')
def update_plant(plant_id):
    data = request.get_json()

    # Check if id is provided in json
    # And check if id in json is matching with id from argument plant_id
    if len(data) == 4 and 'id' in data:
        if data['id'] != plant_id:
            message = "Bad request, ids are not matching"
            return jsonify({"error": message}), 400
        del data['id']

    # Validation
    if len(data) != 3 or 'name' not in data or 'type' not in data or 'sellers' not in data:
        message = "Bad request, incorrect plant object given"
        return jsonify({"error": message}), 400

    # Check if sellers exists in plant_shop.sellers
    seller_ids = {seller.id for seller in plant_shop.sellers}
    if not all(seller['id'] in seller_ids for seller in data['sellers']):
        message = "Seller is not found in plant_shop"
        return jsonify({"Failure": message}), 404

    # Get plant by id
    plant = plant_shop.get_plant_by_id(plant_id)

    # Convert to sellers dict list to sellers objects list
    sellers_objs = plant_shop.from_dict_to_sellers_objects(data['sellers'])

    # If new plant is added
    if plant is None:
        # Append new plant to the list
        new_plant = pl.Plant(data['name'], data['type'], sellers_objs)
        new_plant.id = plant_id
        plant_shop.plants.append(new_plant)
        # If id in endpoint was higher than current static plant id
        if new_plant.id > pl.Plant.static_plant_id:
            pl.Plant.static_plant_id = new_plant.id + 1
        return jsonify(data), 201, {"location": f"/plants/{plant_id}"}

    else:
        # Update existing plant
        plant.name = data['name']
        plant.type = data['type']
        plant.sellers = sellers_objs
        return jsonify(data), 200, {"location": f"/plants/{plant_id}"}


@app.put('/sellers/<int:seller_id>')
def update_seller(seller_id):
    data = request.get_json()

    # Check if id is provided in json
    # And check if id in json is matching with id from argument seller_id
    if len(data) == 3 and 'id' in data:
        if data['id'] != seller_id:
            message = "Bad request, ids are not matching"
            return jsonify({"error": message}), 400
        del data['id']

    # Validation
    if len(data) != 2 or 'name' not in data or 'surname' not in data:
        message = "Bad request, incorrect seller object given"
        return jsonify({"error": message}), 400

    # Get seller by id
    seller = plant_shop.get_seller_by_id(seller_id)

    # If new seller is added
    if seller is None:
        # Append new seller to the list
        new_seller = sl.Seller(data['name'], data['surname'])
        new_seller.id = seller_id
        plant_shop.sellers.append(new_seller)
        # If id in endpoint was higher than current static seller id
        if new_seller.id > sl.Seller.static_seller_id:
            sl.Seller.static_seller_id = new_seller.id + 1
        return jsonify(data), 201, {"location": f"/sellers/{seller_id}"}

    else:
        # Update existing seller
        seller.name = data['name']
        seller.surname = data['surname']
        return jsonify(data), 200, {"location": f"/sellers/{seller_id}"}


@app.put('/plants/<int:plant_id>/sellers/<int:seller_id>')
def update_plant_seller(plant_id, seller_id):
    data = request.get_json()

    # Get plant
    plant = plant_shop.get_plant_by_id(plant_id)

    # Check if plant exists
    if plant is None:
        message = "Plant is not found"
        return jsonify({"error": message}), 404

    # Get seller from plant's sellers
    seller = plant.find_seller(seller_id)

    # Check if seller exists in plant's sellers list
    if seller is None:
        message = "Seller is not found in plant_shop"
        return jsonify({"error": message}), 404

    if len(data) != 2 or 'name' not in data or 'surname' not in data:
        message = "Bad request, incorrect seller object given"
        return jsonify({"error": message}), 400

    # Update seller in plant's sellers list
    seller.name = data['name']
    seller.surname = data['surname']
    return jsonify(data), 200, {"location": f"/plants/{plant_id}/sellers/{seller_id}"}


# HTTP Delete method functions
@app.delete('/plants/<int:plant_id>')
def delete_plant(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant is not found"
        return jsonify({"error": message}), 404

    plant_shop.plants.remove(plant)
    message = "Plant deleted successfully"
    return jsonify({"success": message}), 204, {"location": f"/plants/{plant_id}"}


@app.delete('/sellers/<int:seller_id>')
def delete_seller(seller_id):
    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        message = "Seller is not found"
        return jsonify({"error": message}), 404

    # Delete this seller from plants sellers list
    for plant in plant_shop.plants:
        if plant.find_seller(seller.id) is not None:
            plant.sellers.remove(seller)

    plant_shop.sellers.remove(seller)
    message = "Seller deleted successfully"
    return jsonify({"success": message}), 204, {"location": f"/sellers/{seller_id}"}


@app.delete('/plants/<int:plant_id>/sellers/<int:seller_id>')
def delete_plant_seller(plant_id, seller_id):
    # Find plant in plant_shop
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant is not found"
        return jsonify({"error": message}), 404

    # Find seller in plant's sellers list
    seller = plant.find_seller(seller_id)
    if seller is None:
        message = "Seller is not found"
        return jsonify({"error": message}), 404

    # Remove seller from plant's sellers list
    plant.sellers.remove(seller)
    message = "Seller deleted successfully from plant's sellers list"
    return jsonify({"success": message}), 204, {"location": f"/plants/{plant_id}/sellers/{seller_id}"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
