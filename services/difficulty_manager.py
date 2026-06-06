class DifficultyManager:
    def __init__(self):
        self._difficulty = "normal"
        self._modifiers = {
            "easy": {
                "restock_amount": 3,
                "customer_reduction": 0.7,
                "score_multiplier": 0.8,
                "event_frequency": 0.2,
                "penalty": 2
            },
            "normal": {
                "restock_amount": 2,
                "customer_reduction": 1.0,
                "score_multiplier": 1.0,
                "event_frequency": 0.4,
                "penalty": 5
            },
            "hard": {
                "restock_amount": 1,
                "customer_reduction": 1.3,
                "score_multiplier": 1.5,
                "event_frequency": 0.6,
                "penalty": 10
            }
        }

    def set_difficulty(self, difficulty):
        if difficulty in self._modifiers:
            self._difficulty = difficulty
            return True
        return False

    def get_difficulty(self):
        return self._difficulty

    def get_modifier(self, key):
        return self._modifiers[self._difficulty].get(key, 1)

    def get_restock_amount(self):
        return self._modifiers[self._difficulty]["restock_amount"]

    def get_customer_multiplier(self):
        return self._modifiers[self._difficulty]["customer_reduction"]

    def get_score_multiplier(self):
        return self._modifiers[self._difficulty]["score_multiplier"]

    def get_event_frequency(self):
        return self._modifiers[self._difficulty]["event_frequency"]

    def get_penalty(self):
        return self._modifiers[self._difficulty]["penalty"]