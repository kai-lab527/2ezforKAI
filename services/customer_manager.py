import random

class CustomerManager:
    def __init__(self):
        self._customers = []
        self._served_today = 0
        self._left_angry = 0
        self._happiness = 100
        self._daily_goal = 0

    def generate_daily_customers(self, day, difficulty):
        base = 3 + (day * 1)
        if difficulty == "easy":
            self._daily_goal = base
        elif difficulty == "normal":
            self._daily_goal = base + 2
        else:
            self._daily_goal = base + 4
        
        self._customers = []
        names = ["Maria", "Juan", "Pedro", "Jose", "Ana", "Luz", "Ramon", "Elena", "Mario", "Carla", 
                 "Teresa", "Rico", "Bella", "Miguel", "Sofia", "Lito", "Nena", "Paolo", "Gina", "Rudy"]
        foods = ["rice", "soup", "vegetable_meal", "porridge", "rice", "soup"]
        
        for i in range(self._daily_goal):
            vip_chance = min(0.15, 0.03 * day)
            picky_chance = 0.2 if difficulty == "easy" else (0.25 if difficulty == "normal" else 0.3)
            roll = random.random()
            if roll < vip_chance:
                customer_type = "VIP"
                patience = random.randint(4, 6)
                reward = random.randint(10, 18)
            elif roll < vip_chance + picky_chance:
                customer_type = "Picky"
                patience = random.randint(2, 3)
                reward = random.randint(7, 15)
            else:
                customer_type = "Regular"
                patience = random.randint(2, 4)
                reward = random.randint(5, 12)

            customer = {
                "id": i,
                "name": random.choice(names),
                "patience": patience,
                "reward": reward,
                "favorite": random.choice(foods),
                "type": customer_type,
                "status": "waiting",
                "wait_time": 0
            }
            self._customers.append(customer)
        
        return self._daily_goal

    def get_customers(self):
        return self._customers

    def get_daily_goal(self):
        return self._daily_goal

    def get_served_today(self):
        served = 0
        for customer in self._customers:
            if customer.get("status") == "served":
                served += 1
        return served

    def serve_customers(self, people_fed):
        served_count = 0
        points_earned = 0
        
        for customer in self._customers:
            if customer.get("status") == "waiting" and people_fed > 0:
                customer["status"] = "served"
                served_count += 1
                people_fed -= 1
                points_earned += customer["reward"]
                self._happiness = min(100, self._happiness + 2)
        
        self._served_today = served_count
        return served_count, points_earned

    def update_waiting(self):
        left = 0
        for customer in self._customers:
            if customer.get("status") == "waiting":
                customer["wait_time"] += 1
                if customer["wait_time"] >= customer["patience"]:
                    customer["status"] = "left_angry"
                    left += 1
                    self._left_angry += 1
                    self._happiness = max(0, self._happiness - 8)
        return left

    def close_day(self):
        left = 0
        for customer in self._customers:
            if customer.get("status") == "waiting":
                customer["status"] = "left_angry"
                left += 1
                self._left_angry += 1
                self._happiness = max(0, self._happiness - 8)
        return left

    def get_left_angry(self):
        return self._left_angry

    def get_happiness(self):
        return self._happiness

    def get_remaining_customers(self):
        count = 0
        for customer in self._customers:
            if customer.get("status") == "waiting":
                count += 1
        return count

    def get_completion_percentage(self):
        if self._daily_goal == 0:
            return 0
        return (self.get_served_today() / self._daily_goal) * 100

    def reset_daily(self):
        self._served_today = 0
        self._left_angry = 0