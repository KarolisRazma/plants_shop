class Seller:
    def __init__(self, seller_id, seller_name, seller_surname):
        self.id = seller_id
        self.name = seller_name
        self.surname = seller_surname

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname
        }
