import json

from flask import Flask, request, jsonify, Response
import resources.plants_shop as p_shop
import resources.plant as pl
import resources.seller as sl

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
    return jsonify(plant_shop.make_plants_dict())


@app.get('/sellers')
def show_sellers():
    return jsonify(plant_shop.make_sellers_dict())


@app.get('/plants/<int:plant_id>')
def show_specific_plant(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant not found"
        return Response(json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")

    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    return jsonify(plant_dict)


@app.get('/sellers/<int:seller_id>')
def show_specific_seller(seller_id):
    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        message = "Seller not found"
        return Response(json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")

    seller_dict = plant_shop.get_seller_dict_by_id(seller_id=seller_id)
    return jsonify(seller_dict)


@app.get('/plants/<int:plant_id>/sellers')
def show_plant_sellers(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant not found"
        return Response(json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")

    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    sellers_dict = plant_dict['sellers']
    return jsonify(sellers_dict)


@app.get('/plants/<int:plant_id>/sellers/<int:seller_id>')
def show_plant_specific_seller(plant_id, seller_id):
    # Check if plant and seller exists
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant not found"
        return Response(json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        message = "Seller not found"
        return Response(json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    # Return json
    plant_dict = plant_shop.get_plant_dict_by_id(plant_id=plant_id)
    sellers_dict = plant_dict['sellers']
    for seller in sellers_dict:
        if seller['id'] == seller_id:
            return jsonify(seller)


# HTTP POST method functions
@app.post('/plants')
def add_plant():
    data = request.get_json()
    # Check if json is correct
    if len(data) == 4 and 'id' in data and 'name' in data and 'type' in data and 'sellers' in data:

        # Check if plant already exists
        for plant in plant_shop.plants:
            if plant.id == data['id']:
                message = "Bad request, plant already exists"
                return Response(response=json.dumps({"Failure": message}),
                                status=400,
                                headers={"location": "/sellers/" + str(data['id'])},
                                mimetype="application/json")

        # Convert to Sellers objects list
        sellers_objs = plant_shop.from_dict_to_sellers_objects(data['sellers'])

        # Check if sellers exists in plant_shop.sellers
        for seller in sellers_objs:
            if plant_shop.get_seller_by_id(seller.id) is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(data['id'])},
                                mimetype="application/json")

        # Append new plant to the list
        plant_shop.plants.append(pl.Plant(data['id'], data['name'], data['type'], sellers_objs))

        message = "Successfully added new plant to plant shop"
        return Response(response=json.dumps({"Success": message}),
                        status=201,
                        headers={"location": "/plants/" + str(data['id'])},
                        mimetype="application/json")
    else:
        message = "Bad request, incorrect plant object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(data['id'])},
                        mimetype="application/json")


@app.post('/sellers')
def add_seller():
    data = request.get_json()
    if len(data) == 3 and 'id' in data and 'name' in data and 'surname' in data:
        # Check if seller already exists
        for plant_shop_seller in plant_shop.sellers:
            if plant_shop_seller.id == data['id']:
                message = "Bad request, seller already exists"
                return Response(response=json.dumps({"Failure": message}),
                                status=400,
                                headers={"location": "/sellers/" + str(data['id'])},
                                mimetype="application/json")

        plant_shop.sellers.append(sl.Seller(data['id'], data['name'], data['surname']))
        message = "Successfully added new seller to plant shop"
        return Response(response=json.dumps({"Success": message}),
                        status=201,
                        headers={"location": "/sellers/" + str(data['id'])},
                        mimetype="application/json")
    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/sellers/" + str(data['id'])},
                        mimetype="application/json")


@app.post('/plants/<int:plant_id>/sellers')
def add_seller_to_plant(plant_id):
    data = request.get_json()

    plant = plant_shop.get_plant_by_id(plant_id)
    # Check if plant exists
    if plant is None:
        message = "Plant is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                        mimetype="application/json")

    if len(data) == 3 and 'id' in data and 'name' in data and 'surname' in data:
        seller = plant.find_seller(data['id'])
        # Check if seller exists in plant's sellers list
        if seller is None:
            # Check if seller exists in plant_shop.sellers
            new_plant_seller = plant_shop.get_seller_by_id(data['id'])
            if new_plant_seller is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                                mimetype="application/json")
            else:
                plant.sellers.append(new_plant_seller)
                message = "Successfully added new seller to plant id={}".format(plant_id)
                return Response(response=json.dumps({"Success": message}),
                                status=201,
                                headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                                mimetype="application/json")
        else:
            message = "Bad request, seller already exists on plant's sellers list"
            return Response(response=json.dumps({"Failure": message}),
                            status=400,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                            mimetype="application/json")

    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                        mimetype="application/json")


# HTTP PUT method functions
@app.put('/plants/<int:plant_id>')
def update_plant(plant_id):
    data = request.get_json()
    # If json is correct
    if len(data) == 4 and 'id' in data and 'name' in data and 'type' in data and 'sellers' in data \
            and data['id'] == plant_id:

        # Convert to sellers dict list to sellers objects list
        sellers_objs = plant_shop.from_dict_to_sellers_objects(data['sellers'])

        # Check if sellers exists in plant_shop.sellers
        for seller in sellers_objs:
            if plant_shop.get_seller_by_id(seller.id) is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(data['id'])},
                                mimetype="application/json")

        plant = plant_shop.get_plant_by_id(plant_id)
        # If new plant is added
        if plant is None:
            # Append new plant to the list
            plant_shop.plants.append(pl.Plant(data['id'], data['name'], data['type'], sellers_objs))
            message = "Successfully added new plant to plant shop"
            return Response(response=json.dumps({"Success": message}),
                            status=201,
                            headers={"location": "/plants/" + str(data['id'])},
                            mimetype="application/json")
        else:
            # Update plant
            plant.name = data['name']
            plant.type = data['type']
            plant.sellers = sellers_objs
            message = "Successfully updated plant in the plant shop"
            return Response(response=json.dumps({"Success": message}),
                            status=200,
                            headers={"location": "/plants/" + str(data['id'])},
                            mimetype="application/json")

    else:
        message = "Bad request, incorrect plant object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(data['id'])},
                        mimetype="application/json")


@app.put('/sellers/<int:seller_id>')
def update_seller(seller_id):
    data = request.get_json()
    # If json is correct
    if len(data) == 3 and 'id' in data and 'name' in data and 'surname' in data and data['id'] == seller_id:
        seller = plant_shop.get_seller_by_id(seller_id)
        # If new seller is added
        if seller is None:
            # Append new seller to the list
            plant_shop.sellers.append(sl.Seller(data['id'], data['name'], data['surname']))
            message = "Successfully added new seller to plant shop"
            return Response(response=json.dumps({"Success": message}),
                            status=201,
                            headers={"location": "/sellers/" + str(data['id'])},
                            mimetype="application/json")
        else:
            # Update seller
            seller.name = data['name']
            seller.surname = data['surname']
            message = "Successfully updated seller in the plant shop"
            return Response(response=json.dumps({"Success": message}),
                            status=200,
                            headers={"location": "/sellers/" + str(data['id'])},
                            mimetype="application/json")

    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/sellers/" + str(data['id'])},
                        mimetype="application/json")


@app.put('/plants/<int:plant_id>/sellers/<int:seller_id>')
def update_plant_seller(plant_id, seller_id):
    data = request.get_json()

    plant = plant_shop.get_plant_by_id(plant_id)
    # Check if plant exists
    if plant is None:
        message = "Plant is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                        mimetype="application/json")

    if len(data) == 3 and 'id' in data and 'name' in data and 'surname' in data and data['id'] == seller_id:
        seller = plant.find_seller(seller_id)
        # Check if seller exists in plant's sellers list
        if seller is None:
            # Check if seller exists in plant_shop.sellers
            new_plant_seller = plant_shop.get_seller_by_id(seller_id)
            if new_plant_seller is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                                mimetype="application/json")
            # Append to plant's sellers list
            # TODO or should it also update name/surname?
            plant.sellers.append(new_plant_seller)
            message = "Successfully added new seller to plant id={}".format(plant_id)
            return Response(response=json.dumps({"Success": message}),
                            status=201,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                            mimetype="application/json")
        else:
            # Update seller in plant's sellers list
            seller.name = data['name']
            seller.surname = data['surname']
            message = "Successfully updated seller to plant id={}".format(plant_id)
            return Response(response=json.dumps({"Success": message}),
                            status=200,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                            mimetype="application/json")
    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                        mimetype="application/json")


# HTTP Delete method functions
@app.delete('/plants/<int:plant_id>')
def delete_plant(plant_id):
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    plant_shop.plants.remove(plant)
    message = "Plant deleted successfully"
    return Response(response=json.dumps({"Success": message}),
                    status=200,
                    headers={"location": "/plants/" + str(plant_id)},
                    mimetype="application/json")


@app.delete('/sellers/<int:seller_id>')
def delete_seller(seller_id):
    seller = plant_shop.get_seller_by_id(seller_id)
    if seller is None:
        message = "Seller is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    # Delete this seller from plants sellers list
    for plant in plant_shop.plants:
        if plant.find_seller(seller.id) is not None:
            plant.sellers.remove(seller)

    plant_shop.sellers.remove(seller)
    message = "Seller deleted successfully"
    return Response(response=json.dumps({"Success": message}),
                    status=200,
                    mimetype="application/json")


@app.delete('/plants/<int:plant_id>/sellers/<int:seller_id>')
def delete_plant_seller(plant_id, seller_id):
    # Find plant in plant_shop
    plant = plant_shop.get_plant_by_id(plant_id)
    if plant is None:
        message = "Plant is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    # Find seller in plant's sellers list
    seller = plant.find_seller(seller_id)
    if seller is None:
        message = "Seller is not found"
        return Response(response=json.dumps({"Failure": message}),
                        status=404,
                        mimetype="application/json")
    # Remove seller from plant's sellers list
    plant.sellers.remove(seller)
    message = "Seller deleted successfully from plant's sellers list"
    return Response(response=json.dumps({"Success": message}),
                    status=200,
                    mimetype="application/json")
