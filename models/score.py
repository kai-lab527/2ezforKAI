class Score:
    def __init__(self):
        self._current_score = 0
        self._total_people_fed = 0
        self._total_waste = 0
        self._day = 1

    def add_points(self, people_fed, waste):
        self._total_people_fed += people_fed
        self._total_waste += waste
        points = (people_fed * 10) - (waste * 2)
        if points < 0:
            points = 0
        self._current_score += points
        return points

    def get_score(self):
        return self._current_score

    def get_people_fed(self):
        return self._total_people_fed

    def get_waste(self):
        return self._total_waste

    def get_day(self):
        return self._day

    def next_day(self):
        self._day += 1

    def reset(self):
        self._current_score = 0
        self._total_people_fed = 0
        self._total_waste = 0
        self._day = 1