class Customer:
    def __init__(self, name, patience, reward, favorite_food):
        self._name = name
        self._patience = patience
        self._reward = reward
        self._favorite_food = favorite_food
        self._waiting_time = 0

    def get_name(self):
        return self._name

    def get_patience(self):
        return self._patience

    def get_reward(self):
        return self._reward

    def get_favorite_food(self):
        return self._favorite_food

    def get_waiting_time(self):
        return self._waiting_time

    def increase_wait(self):
        self._waiting_time += 1

    def is_leaving(self):
        return self._waiting_time >= self._patience

    def reset_wait(self):
        self._waiting_time = 0