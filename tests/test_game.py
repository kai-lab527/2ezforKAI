import random
import pytest
from services.cooking_manager import CookingManager
from services.inventory_manager import InventoryManager
from services.composting_manager import CompostingManager
from services.customer_manager import CustomerManager
from services.score_manager import ScoreManager

def test_cook_valid_recipe():
    cooking = CookingManager()
    inventory = InventoryManager()
    compost = CompostingManager()
    success, result = cooking.cook("rice", inventory, compost)
    assert success == True
    assert result[0] == 4

def test_cook_invalid_recipe():
    cooking = CookingManager()
    inventory = InventoryManager()
    compost = CompostingManager()
    success, result = cooking.cook("pizza", inventory, compost)
    assert success == False
    assert "not found" in result

def test_cook_insufficient_ingredients():
    cooking = CookingManager()
    inventory = InventoryManager()
    compost = CompostingManager()
    for i in range(15):
        inventory.use_ingredient("rice", 1)
    success, result = cooking.cook("rice", inventory, compost)
    assert success == False

def test_inventory_use_ingredient():
    inventory = InventoryManager()
    initial = inventory.get_quantity("rice")
    inventory.use_ingredient("rice", 2)
    assert inventory.get_quantity("rice") == initial - 2

def test_inventory_add_ingredient():
    inventory = InventoryManager()
    initial = inventory.get_quantity("vegetables")
    inventory.add_ingredient("vegetables", 5)
    assert inventory.get_quantity("vegetables") == initial + 5

def test_compost_add_scraps():
    compost = CompostingManager()
    compost.add_scraps(5)
    assert compost.get_scraps() == 5

def test_compost_convert_to_soil():
    compost = CompostingManager()
    compost.add_scraps(7)
    soil = compost.convert_to_soil()
    assert soil == 2
    assert compost.get_scraps() == 1

def test_score_add_points():
    score = ScoreManager()
    points = score.add_points(5, 2)
    assert points == (5 * 10) - (2 * 2)
    assert score.get_people_fed() == 5
    assert score.get_waste() == 2

def test_score_next_day():
    score = ScoreManager()
    assert score.get_day() == 1
    score.next_day()
    assert score.get_day() == 2

def test_save_final_score(tmp_path):
    score = ScoreManager()
    score.add_points(5, 2)
    final_file = tmp_path / "final_score.txt"
    score.save_final_score(str(final_file))
    assert final_file.read_text() == str(score.get_current_score())

def test_customer_service_flow():
    random.seed(0)
    customer_manager = CustomerManager()
    num_customers = customer_manager.generate_daily_customers(1, "easy")
    assert num_customers == 4
    inventory = InventoryManager()
    compost = CompostingManager()
    cooking = CookingManager()

    success, result = cooking.cook("rice", inventory, compost, customer_manager)
    assert success is True
    assert result[0] == 4
    assert result[3] == 4
    assert customer_manager.get_served_today() == 4
    assert customer_manager.get_remaining_customers() == 0

def test_close_day_marks_unserved_angry():
    customer_manager = CustomerManager()
    customer_manager._customers = [
        {"id": 0, "name": "Ana", "patience": 5, "reward": 10, "favorite": "rice", "type": "Regular", "status": "waiting", "wait_time": 0},
        {"id": 1, "name": "Jose", "patience": 5, "reward": 8, "favorite": "soup", "type": "Regular", "status": "waiting", "wait_time": 0},
    ]
    left = customer_manager.close_day()
    assert left == 2
    assert customer_manager.get_left_angry() == 2
    assert customer_manager.get_remaining_customers() == 0
    assert all(c["status"] == "left_angry" for c in customer_manager.get_customers())

@pytest.mark.parametrize('recipe, expected_people', [
    ("rice", 4),
    ("soup", 3),
    ("vegetable_meal", 5),
    ("porridge", 3),
])
def test_multiple_recipes(recipe, expected_people):
    cooking = CookingManager()
    inventory = InventoryManager()
    compost = CompostingManager()
    success, result = cooking.cook(recipe, inventory, compost)
    if success:
        assert result[0] == expected_people
