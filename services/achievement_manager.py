from models.achievement import Achievement

class AchievementManager:
    def __init__(self):
        self._achievements = self._load_achievements()
        self._total_reward = 0

    def _load_achievements(self):
        return {
            "first_cook": Achievement("First Cook", "Cook your first meal", 1, 10),
            "five_star": Achievement("Five Star", "Serve 50 people total", 50, 25),
            "master_chef": Achievement("Master Chef", "Reach Chef Level 5", 5, 50),
            "zero_waste": Achievement("Zero Waste", "Have less than 5 total waste", 5, 30),
            "perfect_day": Achievement("Perfect Day", "Serve all customers in one day", 1, 40),
            "millionaire": Achievement("Millionaire", "Reach 500 points", 500, 100),
            "philanthropist": Achievement("Philanthropist", "Complete all 7 days", 7, 75),
            "happy_community": Achievement("Happy Community", "Reach 100% happiness", 100, 50)
        }

    def get_achievements(self):
        return self._achievements

    def check_achievements(self, stats, level, waste_total, happiness, day):
        rewards = []
        
        if stats["total_cooks"] >= self._achievements["first_cook"].get_requirement() and not self._achievements["first_cook"].is_earned():
            rewards.append(self._achievements["first_cook"].earn())
        
        if stats["total_people_fed"] >= self._achievements["five_star"].get_requirement() and not self._achievements["five_star"].is_earned():
            rewards.append(self._achievements["five_star"].earn())
        
        if level >= self._achievements["master_chef"].get_requirement() and not self._achievements["master_chef"].is_earned():
            rewards.append(self._achievements["master_chef"].earn())
        
        if waste_total <= self._achievements["zero_waste"].get_requirement() and not self._achievements["zero_waste"].is_earned():
            rewards.append(self._achievements["zero_waste"].earn())
        
        if stats["perfect_days"] >= 1 and not self._achievements["perfect_day"].is_earned():
            rewards.append(self._achievements["perfect_day"].earn())
        
        if stats["total_score"] >= self._achievements["millionaire"].get_requirement() and not self._achievements["millionaire"].is_earned():
            rewards.append(self._achievements["millionaire"].earn())
        
        if day >= self._achievements["philanthropist"].get_requirement() and not self._achievements["philanthropist"].is_earned():
            rewards.append(self._achievements["philanthropist"].earn())
        
        if happiness >= self._achievements["happy_community"].get_requirement() and not self._achievements["happy_community"].is_earned():
            rewards.append(self._achievements["happy_community"].earn())
        
        return rewards