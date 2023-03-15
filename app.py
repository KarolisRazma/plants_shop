import json
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
    if len(data) == 3 and 'name' in data and 'type' in data and 'sellers' in data:

        # Convert to Sellers objects list
        sellers_objs = plant_shop.from_dict_to_sellers_objects(data['sellers'])

        # Check if sellers exists in plant_shop.sellers
        for seller in sellers_objs:
            if plant_shop.get_seller_by_id(seller.id) is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants"},
                                mimetype="application/json")

        # Append new plant to the list
        new_plant = pl.Plant(data['name'], data['type'], sellers_objs)
        plant_shop.plants.append(new_plant)

        return Response(response=json.dumps(data),
                        status=201,
                        headers={"location": "/plants/" + str(new_plant.id)},
                        mimetype="application/json")
    else:
        message = "Bad request, incorrect plant object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants"},
                        mimetype="application/json")


@app.post('/sellers')
def add_seller():
    data = request.get_json()
    if len(data) == 2 and 'name' in data and 'surname' in data:

        new_seller = sl.Seller(data['name'], data['surname'])
        plant_shop.sellers.append(new_seller)
        return Response(response=json.dumps(data),
                        status=201,
                        headers={"location": "/sellers/" + str(new_seller.id)},
                        mimetype="application/json")
    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/sellers"},
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
                        headers={"location": "/plants/" + str(plant_id) + "/sellers"},
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
                                headers={"location": "/plants/" + str(plant_id) + "/sellers"},
                                mimetype="application/json")
            else:
                plant.sellers.append(new_plant_seller)
                return Response(response=json.dumps(data),
                                status=201,
                                headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(data['id'])},
                                mimetype="application/json")
        else:
            message = "Bad request, seller already exists on plant's sellers list"
            return Response(response=json.dumps({"Failure": message}),
                            status=400,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers"},
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
    if len(data) == 3 and 'name' in data and 'type' in data and 'sellers' in data:

        # Convert to sellers dict list to sellers objects list
        sellers_objs = plant_shop.from_dict_to_sellers_objects(data['sellers'])

        # Check if sellers exists in plant_shop.sellers
        for seller in sellers_objs:
            if plant_shop.get_seller_by_id(seller.id) is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(plant_id)},
                                mimetype="application/json")

        plant = plant_shop.get_plant_by_id(plant_id)
        # If new plant is added
        if plant is None:
            # Append new plant to the list
            new_plant = pl.Plant(data['name'], data['type'], sellers_objs)
            new_plant.id = plant_id
            plant_shop.plants.append(new_plant)
            # If id in endpoint was higher than current static plant id
            if new_plant.id > pl.Plant.static_plant_id:
                pl.Plant.static_plant_id = new_plant.id + 1

            return Response(response=json.dumps(data),
                            status=201,
                            headers={"location": "/plants/" + str(plant_id)},
                            mimetype="application/json")
        else:
            # Update plant
            plant.name = data['name']
            plant.type = data['type']
            plant.sellers = sellers_objs
            return Response(response=json.dumps(data),
                            status=200,
                            headers={"location": "/plants/" + str(plant_id)},
                            mimetype="application/json")

    else:
        message = "Bad request, incorrect plant object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(plant_id)},
                        mimetype="application/json")


@app.put('/sellers/<int:seller_id>')
def update_seller(seller_id):
    data = request.get_json()
    # If json is correct
    if len(data) == 2 and 'name' in data and 'surname' in data:
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

            return Response(response=json.dumps(data),
                            status=201,
                            headers={"location": "/sellers/" + str(seller_id)},
                            mimetype="application/json")
        else:
            # Update seller
            seller.name = data['name']
            seller.surname = data['surname']
            return Response(response=json.dumps(data),
                            status=200,
                            headers={"location": "/sellers/" + str(seller_id)},
                            mimetype="application/json")

    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/sellers/" + str(seller_id)},
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
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(seller_id)},
                        mimetype="application/json")

    if len(data) == 2 and 'name' in data and 'surname' in data:
        seller = plant.find_seller(seller_id)
        # Check if seller exists in plant's sellers list
        if seller is None:
            # Check if seller exists in plant_shop.sellers
            new_plant_seller = plant_shop.get_seller_by_id(seller_id)
            if new_plant_seller is None:
                message = "Seller is not found in plant_shop"
                return Response(response=json.dumps({"Failure": message}),
                                status=404,
                                headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(seller_id)},
                                mimetype="application/json")
            # Append to plant's sellers list
            new_plant_seller.name = data['name']
            new_plant_seller.surname = data['surname']
            plant.sellers.append(new_plant_seller)
            return Response(response=json.dumps(data),
                            status=201,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(seller_id)},
                            mimetype="application/json")
        else:
            # Update seller in plant's sellers list
            seller.name = data['name']
            seller.surname = data['surname']
            return Response(response=json.dumps(data),
                            status=200,
                            headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(seller_id)},
                            mimetype="application/json")
    else:
        message = "Bad request, incorrect seller object given"
        return Response(response=json.dumps({"Failure": message}),
                        status=400,
                        headers={"location": "/plants/" + str(plant_id) + "/sellers/" + str(seller_id)},
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
                    status=204,
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
                    status=204,
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
                    status=204,
                    mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
