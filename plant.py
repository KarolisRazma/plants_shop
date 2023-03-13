class Plant:
    def __init__(self, plant_id, name, plant_type, sellers=None):
        if sellers is None:
            sellers = []
        self.id = plant_id
        self.name = name
        self.type = plant_type
        self.sellers = sellers

    def __dict__(self):
        sellers_list = []
        for seller in self.sellers:
            sellers_list.append(seller.__dict__())

        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'sellers': sellers_list
        }

    def find_seller(self, seller_id):
        for seller in self.sellers:
            if seller.id == seller_id:
                return seller
        return None
