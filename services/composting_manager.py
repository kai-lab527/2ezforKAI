class CompostingManager:
    def __init__(self):
        self._scraps = 0
        self._soil = 0

    def add_scraps(self, amount):
        self._scraps += amount
        return self._scraps

    def get_scraps(self):
        return self._scraps

    def get_soil(self):
        return self._soil

    def convert_to_soil(self):
        if self._scraps >= 3:
            soil_produced = self._scraps // 3
            self._soil += soil_produced
            self._scraps = self._scraps % 3
            return soil_produced
        return 0

    def use_soil_to_grow(self, inventory):
        if self._soil >= 2:
            self._soil -= 2
            inventory.add_ingredient("vegetables", 3)
            return True, "Grew 3 vegetables using 2 soil"
        return False, f"Need 2 soil. Current soil: {self._soil}"