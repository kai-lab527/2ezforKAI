from models.recipe import Recipe

class CookingManager:
    def __init__(self):
        self._recipes = self._load_recipes()
        self._chef_level = 1
        self._staff_bonus = 0

    def _load_recipes(self):
        return {
            "rice": Recipe("Rice", {"rice": 1, "water": 1}, 4, 1, 0, 1),
            "soup": Recipe("Soup", {"vegetables": 2, "water": 1, "salt": 1}, 3, 2, 0, 1),
            "vegetable_meal": Recipe("Vegetable Meal", {"vegetables": 3, "rice": 1}, 5, 1, 0, 2),
            "porridge": Recipe("Porridge", {"rice": 1, "water": 2, "salt": 1}, 3, 1, 0, 1),
            "feast": Recipe("Feast", {"rice": 3, "vegetables": 4, "salt": 2}, 15, 3, 50, 3),
            "deluxe_meal": Recipe("Deluxe Meal", {"rice": 2, "vegetables": 3, "water": 2}, 10, 1, 30, 2)
        }

    def get_recipes(self):
        unlocked = [name for name, recipe in self._recipes.items()
                    if recipe.get_level_required() <= self._chef_level]
        return sorted(unlocked)

    def get_all_recipes(self):
        return self._recipes

    def get_recipe(self, name):
        return self._recipes.get(name.lower())

    def set_chef_level(self, level):
        self._chef_level = level

    def get_chef_level(self):
        return self._chef_level

    def set_staff_bonus(self, bonus):
        self._staff_bonus = bonus

    def cook(self, recipe_name, inventory, compost_manager, customer_manager=None):
        recipe = self.get_recipe(recipe_name)
        if not recipe:
            return False, "Recipe not found"

        if recipe.get_level_required() > self._chef_level:
            return False, f"Chef level {recipe.get_level_required()} required. Upgrade your kitchen!"

        can_cook, missing = recipe.can_cook(inventory)
        if not can_cook:
            return False, f"Missing: {missing}"

        for ingredient, amount in recipe.get_ingredients().items():
            inventory.use_ingredient(ingredient, amount)

        people_fed = recipe.get_people_fed() + self._staff_bonus
        waste = max(0, recipe.get_waste() - self._staff_bonus // 2)
        
        compost_manager.add_scraps(waste)

        served = 0
        points_from_customers = 0
        
        if customer_manager:
            served, points_from_customers = customer_manager.serve_customers(people_fed)

        return True, (people_fed, waste, recipe.get_name(), served, points_from_customers)

    def upgrade_kitchen(self, points):
        cost = self._chef_level * 30
        if points >= cost:
            self._chef_level += 1
            return True, cost
        return False, cost
    