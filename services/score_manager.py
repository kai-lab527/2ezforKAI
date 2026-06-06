from models.score import Score
import os

class ScoreManager:
    def __init__(self):
        self._score = Score()
        self._stats = {
            "total_cooks": 0,
            "total_people_fed": 0,
            "total_score": 0,
            "perfect_days": 0,
        }
        self._high_score = self._load_high_score()

    def _load_high_score(self):
        if os.path.exists("score.txt"):
            try:
                with open("score.txt", "r") as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0

    def save_high_score(self, filename="score.txt"):
        if self._score.get_score() > self._high_score:
            self._high_score = self._score.get_score()
            with open(filename, "w") as f:
                f.write(str(self._high_score))
            return True
        return False

    def save_final_score(self, filename="final_score.txt"):
        with open(filename, "w") as f:
            f.write(str(self._score.get_score()))
        return True

    def get_high_score(self):
        return self._high_score

    def get_current_score(self):
        return self._score.get_score()

    def get_people_fed(self):
        return self._score.get_people_fed()

    def get_waste(self):
        return self._score.get_waste()

    def get_day(self):
        return self._score.get_day()

    def get_stats(self):
        self._stats["total_people_fed"] = self._score.get_people_fed()
        self._stats["total_score"] = self._score.get_score()
        return self._stats

    def add_points(self, people_fed, waste):
        pts = self._score.add_points(people_fed, waste)
        if people_fed > 0:
            self._stats["total_cooks"] += 1
            self._stats["total_people_fed"] += people_fed
            self._stats["total_score"] = self._score.get_score()
        return pts

    def add_bonus(self, amount):
        """Add flat bonus points without affecting people_fed/waste counters."""
        self._score._current_score += amount
        self._stats["total_score"] = self._score.get_score()

    def deduct(self, amount):
        """Deduct points (penalty), floor at 0."""
        self._score._current_score = max(0, self._score._current_score - amount)
        self._stats["total_score"] = self._score.get_score()

    def mark_perfect_day(self):
        self._stats["perfect_days"] += 1

    def next_day(self):
        self._score.next_day()

    def reset(self):
        self._score.reset()
        self._stats = {"total_cooks": 0, "total_people_fed": 0, "total_score": 0, "perfect_days": 0}

    def is_game_complete(self):
        return self._score.get_day() > 7