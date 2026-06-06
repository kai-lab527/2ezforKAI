from models.ingredient import Ingredient

class InventoryManager:
    def __init__(self):
        self._ingredients = self._load_inventory()

    def _load_inventory(self):
        return {
            "rice": Ingredient("rice", 10),
            "water": Ingredient("water", 15),
            "vegetables": Ingredient("vegetables", 8),
            "salt": Ingredient("salt", 5)
        }

    def get_all_ingredients(self):
        return {name: ing.get_quantity() for name, ing in self._ingredients.items()}

    def get_quantity(self, name):
        if name in self._ingredients:
            return self._ingredients[name].get_quantity()
        return 0

    def use_ingredient(self, name, amount):
        if name in self._ingredients:
            return self._ingredients[name].subtract(amount)
        return False

    def add_ingredient(self, name, amount):
        if name in self._ingredients:
            self._ingredients[name].add(amount)
        else:
            self._ingredients[name] = Ingredient(name, amount)

    def has_ingredient(self, name, amount):
        return self.get_quantity(name) >= amount