class Ingredient:
    def __init__(self, name, quantity):
        self._name = name
        self._quantity = quantity

    def get_name(self):
        return self._name

    def get_quantity(self):
        return self._quantity

    def add(self, amount):
        self._quantity += amount

    def subtract(self, amount):
        if self._quantity >= amount:
            self._quantity -= amount
            return True
        return False