import random

class MarketManager:
    def __init__(self, inventory, score_manager):
        self._inventory = inventory
        self._score_manager = score_manager
        self._prices = {"rice": 8, "vegetables": 6, "water": 3, "salt": 5}
        self._sell_prices = {"rice": 5, "vegetables": 4, "water": 2, "salt": 3}

    def get_prices(self):
        return self._prices

    def get_sell_prices(self):
        return self._sell_prices

    def buy(self, ingredient, amount):
        cost = self._prices.get(ingredient, 0) * amount
        if self._score_manager.get_current_score() >= cost:
            self._inventory.add_ingredient(ingredient, amount)
            self._score_manager.deduct(cost)
            return True, cost
        return False, cost

    def sell(self, ingredient, amount):
        if self._inventory.get_quantity(ingredient) >= amount:
            earnings = self._sell_prices.get(ingredient, 0) * amount
            self._inventory.use_ingredient(ingredient, amount)
            self._score_manager.add_bonus(earnings)
            return True, earnings
        return False, 0

    def update_prices(self):
        for item in self._prices:
            change = random.randint(-2, 3)
            self._prices[item] = max(3, self._prices[item] + change)
            self._sell_prices[item] = max(2, self._sell_prices[item] + change // 2)