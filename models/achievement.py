class Achievement:
    def __init__(self, name, description, requirement, reward):
        self._name = name
        self._description = description
        self._requirement = requirement
        self._reward = reward
        self._earned = False

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_requirement(self):
        return self._requirement

    def get_reward(self):
        return self._reward

    def is_earned(self):
        return self._earned

    def earn(self):
        self._earned = True
        return self._reward