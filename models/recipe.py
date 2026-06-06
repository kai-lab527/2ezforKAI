class Recipe:
    def __init__(self, name, ingredients, people_fed, waste_produced, cost=0, level_required=1):
        self._name = name
        self._ingredients = ingredients
        self._people_fed = people_fed
        self._waste_produced = waste_produced
        self._cost = cost
        self._level_required = level_required
        self._unlocked = False

    def get_name(self):
        return self._name

    def get_ingredients(self):
        return self._ingredients

    def get_people_fed(self):
        return self._people_fed

    def get_waste(self):
        return self._waste_produced

    def get_cost(self):
        return self._cost

    def get_level_required(self):
        return self._level_required

    def is_unlocked(self):
        return self._unlocked

    def unlock(self):
        self._unlocked = True

    def can_cook(self, inventory):
        for ingredient, amount in self._ingredients.items():
            if inventory.get_quantity(ingredient) < amount:
                return False, ingredient
        return True, None