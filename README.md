# FoodQuest

## Application Description

FoodQuest is a Python desktop application with Tkinter GUI where players run a community kitchen. Players cook meals using recipes, manage ingredient inventory, compost food scraps into soil, serve customers before they leave, upgrade their kitchen, and earn points.

The application allows users to:

- Cook different meals using simple recipes
- Check ingredient inventory with visual progress bars
- Compost food scraps into soil for regrowing vegetables
- Serve customers with different patience levels and favorite foods
- Upgrade kitchen level to unlock better recipes
- View daily reports on customers served and points earned
- Save high scores across gameplay sessions

Built with a clean tabbed graphical user interface, the game operates entirely offline and follows MVC architecture with models, services, and UI separation.

## OOP Concepts Used

- **Encapsulation** – Private attributes using `_variable` naming convention
- **Abstraction** – DifficultyManager and MarketManager provide clean interfaces
- **Polymorphism** – Different recipe types processed through same interface
- **Modularity** – Code separated into models, services, tests, and UI

## Technologies Used

- Python 3.x (core programming language)
- Tkinter (GUI framework)
- File handling for ingredient tracking and score saving
- Pytest for automated unit testing

## Project Structure

```
FoodQuest/
│
├── models/
│   ├── __init__.py
│   ├── achievement.py
│   ├── customer.py
│   ├── ingredient.py
│   ├── recipe.py
│   └── score.py
│
├── services/
│   ├── __init__.py
│   ├── achievement_manager.py
│   ├── composting_manager.py
│   ├── cooking_manager.py
│   ├── customer_manager.py
│   ├── difficulty_manager.py
│   ├── inventory_manager.py
│   ├── market_manager.py
│   └── score_manager.py
│
├── tests/
│   ├── __init__.py
│   └── test_game.py
│
├── ui/
│   ├── __init__.py
│   └── main_gui.py
│
├── main.py
├── main_gui.py
├── score.txt (generated after gameplay)
├── final_score.txt (generated after gameplay)
└── Tutorial.txt\
```

## How to Run

### Requirements
- Python 3.x

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/kai-lab527/FoodQuest.git
   ```

2. Navigate to project folder:
   ```bash
   cd FoodQuest
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   or
   ```bash
   python main_gui.py
   ```

## Running Tests

Run automated tests using pytest:

```bash
py -m pytest -v
```

## How to Play

1. Select difficulty (Easy/Normal/Hard) at start
2. Day 1 begins with customers waiting
3. Select a recipe from the Cooking tab
4. Click **Cook** and watch the progress bar
5. Go to **Customers** tab and click checkmarks to serve customers
6. Cooked food can serve multiple customers
7. Use **Market** to buy/sell ingredients
8. Use **Compost** to convert scraps to soil and grow vegetables
9. Upgrade kitchen to unlock better recipes
10. Complete 7 days to win

## Export Report

Inside the application:
1. Go to the **Report** tab
2. Click **Export Report**
3. Output file will be saved as: `foodquest_report.txt`

## Author

Developed as a school project by:

- **Angelo Gosim** – Project documentation, testing, and quality assurance
- **Kevin Mendoza** – Flowcharts and class diagrams
- **Hector Gidoc** – Source code implementation and GitHub management

**In Partial Fulfillment** of CC103 Computer Programming 2 at Sorsogon State University – Bulan Campus

**With the Supervision of** Professor John Mark Gabrentina

## Notes

- Basic input validation using `strip()` checks
- Focus is on OOP structure, not advanced error handling
- Designed for educational purposes
- All project files are included in this repository for complete functionality
