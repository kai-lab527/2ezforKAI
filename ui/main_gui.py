import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# Ensure the project root is on sys.path when running this file directly.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.cooking_manager import CookingManager
from services.inventory_manager import InventoryManager
from services.composting_manager import CompostingManager
from services.score_manager import ScoreManager
from services.customer_manager import CustomerManager
from services.achievement_manager import AchievementManager
from services.market_manager import MarketManager
from services.difficulty_manager import DifficultyManager

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0f1923"
PANEL     = "#16232f"
CARD      = "#1e3040"
ACCENT    = "#e8a020"
GREEN     = "#3db87a"
RED       = "#e05555"
BLUE      = "#4a9edd"
PURPLE    = "#a07fd4"
TEXT      = "#e8dcc8"
MUTED     = "#7a8fa0"
GOLD      = "#f0c040"

FONT_TITLE  = ("Arial", 26, "bold")
FONT_HEAD   = ("Arial", 13, "bold")
FONT_BODY   = ("Arial", 10)
FONT_BTN    = ("Arial", 10, "bold")
FONT_STAT   = ("Arial", 22, "bold")
FONT_SMALL  = ("Arial", 9)

# ── Helpers ───────────────────────────────────────────────────────────────────
def styled_btn(parent, text, cmd, bg=ACCENT, fg="#000", width=None):
    kw = dict(text=text, command=cmd, bg=bg, fg=fg,
              font=FONT_BTN, relief=tk.FLAT, cursor="hand2",
              padx=12, pady=6, bd=0, activebackground=bg, activeforeground=fg)
    if width:
        kw["width"] = width
    b = tk.Button(parent, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def _lighten(hex_color):
    h = hex_color.lstrip("#")
    rgb = [min(255, int(h[i:i+2], 16) + 30) for i in (0, 2, 4)]
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def log(widget, text, color=TEXT):
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, text + "\n", ("col_" + color,))
    widget.tag_config("col_" + color, foreground=color)
    widget.see(tk.END)
    widget.config(state=tk.DISABLED)

def log_clear(widget):
    widget.config(state=tk.NORMAL)
    widget.delete(1.0, tk.END)
    widget.config(state=tk.DISABLED)

# ── Main App ──────────────────────────────────────────────────────────────────
class FoodQuestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Food Quest — Community Kitchen")
        self.root.geometry("1100x780")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self._init_managers()
        self._show_start_screen()

    # ── Init ──────────────────────────────────────────────────────────────────
    def _init_managers(self, difficulty="normal"):
        self.difficulty_mgr = DifficultyManager()
        self.difficulty_mgr.set_difficulty(difficulty)

        self.inventory  = InventoryManager()
        self.score      = ScoreManager()
        self.cooking    = CookingManager()
        self.compost    = CompostingManager()
        self.customers  = CustomerManager()
        self.achievements = AchievementManager()
        self.market     = MarketManager(self.inventory, self.score)

        self.current_day  = 1
        self._new_achievements = []
        
        # Track cooked food that hasn't been served
        self._cooked_food = []  # List of {"recipe": name, "people": count, "portions_left": count}
        
        # Timer system for day/transition cycles
        self._phase = "day"  # "day" or "transition"
        self._timer_id = None
        self._clock_time = 300  # Start at 5:00 AM (in minutes from midnight) (in minutes from midnight)

        # Generate day-1 customers
        self.customers.generate_daily_customers(1, difficulty)

    # ── Start Screen ──────────────────────────────────────────────────────────
    def _show_start_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True)

        tk.Label(f, text="🍲", font=("Arial", 60), bg=BG).pack(pady=(40, 5))
        tk.Label(f, text="FOOD QUEST", font=("Arial", 38, "bold"), bg=BG, fg=ACCENT).pack()
        tk.Label(f, text="Community Kitchen Management", font=("Arial", 14), bg=BG, fg=MUTED).pack(pady=(0, 30))

        tk.Label(f, text="Select Difficulty", font=FONT_HEAD, bg=BG, fg=TEXT).pack()

        diff_frame = tk.Frame(f, bg=BG)
        diff_frame.pack(pady=15)

        descs = {
            "easy":   ("EASY",   GREEN,  "+3 restock · Cook twice · 0.8× score"),
            "normal": ("NORMAL", ACCENT, "+2 restock · Cook once  · 1.0× score"),
            "hard":   ("HARD",   RED,    "+1 restock · Cook once  · 1.5× score"),
        }
        for key, (label, color, desc) in descs.items():
            col = tk.Frame(diff_frame, bg=CARD, padx=20, pady=15)
            col.pack(side=tk.LEFT, padx=10)
            tk.Label(col, text=label, font=FONT_HEAD, bg=CARD, fg=color).pack()
            tk.Label(col, text=desc, font=FONT_SMALL, bg=CARD, fg=MUTED).pack(pady=4)
            styled_btn(col, "START", lambda k=key: self._start_game(k), bg=color).pack(pady=(6, 0))

        if self.score.get_high_score() > 0:
            tk.Label(f, text=f"🏆  High Score: {self.score.get_high_score()}",
                     font=FONT_HEAD, bg=BG, fg=GOLD).pack(pady=20)

    def _start_game(self, difficulty):
        hs = self.score.get_high_score() if hasattr(self, 'score') else 0
        self._init_managers(difficulty)
        self.score._high_score = hs
        self._cooked_food = []  # Initialize cooked food list
        self._phase = "day"
        self._clock_time = 300  # Start at 5:00 AM
        self._build_main_ui()
        self._refresh_all()
        self._trigger_day_start_log()
        self._start_timer()

    # ── Main UI Shell ─────────────────────────────────────────────────────────
    def _build_main_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        # ── Top bar ──
        top = tk.Frame(self.root, bg=PANEL, pady=8)
        top.pack(fill=tk.X)

        # Left side: title and phase/timer
        left_top = tk.Frame(top, bg=PANEL)
        left_top.pack(side=tk.LEFT, padx=18)
        tk.Label(left_top, text="🍲 FOOD QUEST", font=("Arial", 16, "bold"),
                 bg=PANEL, fg=ACCENT).pack(side=tk.LEFT)
        
        # Timer and phase info
        self._phase_label = tk.Label(left_top, text="Day 1 - DAY", font=FONT_BTN, bg=PANEL, fg=GOLD)
        self._phase_label.pack(side=tk.LEFT, padx=(20, 5))
        self._timer_label = tk.Label(left_top, text="30s", font=FONT_STAT, bg=PANEL, fg=GREEN)
        self._timer_label.pack(side=tk.LEFT)

        self._stat_vars = {}
        stats = [("DAY", ACCENT), ("SCORE", GREEN), ("PEOPLE FED", BLUE)]
        for label, color in reversed(stats):
            sf = tk.Frame(top, bg=PANEL)
            sf.pack(side=tk.RIGHT, padx=18)
            v = tk.StringVar(value="—")
            self._stat_vars[label] = v
            tk.Label(sf, textvariable=v, font=FONT_STAT, bg=PANEL, fg=color).pack()
            tk.Label(sf, text=label, font=("Arial", 8), bg=PANEL, fg=MUTED).pack()

        # ── Notebook ──
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=MUTED,
                        font=FONT_BTN, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", TEXT)])

        # ── Bottom bar — must be packed BEFORE the notebook so expand=True doesn't bury it ──
        bot = tk.Frame(self.root, bg=PANEL, pady=8)
        bot.pack(fill=tk.X, side=tk.BOTTOM)

        styled_btn(bot, "⟳ RESET", self._confirm_reset, bg="#444", fg=TEXT).pack(side=tk.LEFT, padx=10)

        diff_lbl = self.difficulty_mgr.get_difficulty().upper()
        tk.Label(bot, text=f"Difficulty: {diff_lbl}",
                 font=FONT_SMALL, bg=PANEL, fg=MUTED).pack(side=tk.RIGHT, padx=10)

        # ── Notebook — packed last so it fills remaining space between top and bottom bars ──
        nb = ttk.Notebook(self.root)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 0))

        self._tabs = {}
        tab_defs = [
            ("🍳 Cook",       "_build_cook_tab"),
            ("📦 Inventory",  "_build_inventory_tab"),
            ("🛒 Market",     "_build_market_tab"),
            ("♻️ Compost",    "_build_compost_tab"),
            ("👥 Customers",  "_build_customers_tab"),
            ("🏆 Achievements","_build_achievements_tab"),
        ]
        for name, builder in tab_defs:
            frame = tk.Frame(nb, bg=CARD)
            nb.add(frame, text=name)
            self._tabs[name] = frame
            getattr(self, builder)(frame)

    # ── Cook Tab ──────────────────────────────────────────────────────────────
    def _build_cook_tab(self, parent):
        left = tk.Frame(parent, bg=CARD)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 6), pady=12)

        tk.Label(left, text="PREPARE A MEAL", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(left, text="Select a recipe and cook for the community.",
                 font=FONT_SMALL, bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 10))

        # Recipe picker
        pick = tk.Frame(left, bg=CARD)
        pick.pack(fill=tk.X, pady=4)
        tk.Label(pick, text="Recipe:", font=FONT_BTN, bg=CARD, fg=TEXT, width=8, anchor="w").pack(side=tk.LEFT)
        self._recipe_var = tk.StringVar()
        self._recipe_cb = ttk.Combobox(pick, textvariable=self._recipe_var,
                                        state="readonly", font=("Arial", 10), width=22)
        self._recipe_cb.pack(side=tk.LEFT, padx=6)
        self._recipe_cb.bind("<<ComboboxSelected>>", self._on_recipe_select)

        self._cook_btn = styled_btn(pick, "COOK 🍳", self._do_cook, bg=GREEN)
        self._cook_btn.pack(side=tk.LEFT, padx=6)

        # Recipe info card
        self._recipe_info = tk.Frame(left, bg=PANEL, relief=tk.FLAT, padx=10, pady=8)
        self._recipe_info.pack(fill=tk.X, pady=8)
        self._recipe_info_lbl = tk.Label(self._recipe_info, text="← Select a recipe to see details",
                                          font=FONT_SMALL, bg=PANEL, fg=MUTED, justify="left", anchor="w")
        self._recipe_info_lbl.pack(anchor="w")

        # Progress bar
        self._progress = ttk.Progressbar(left, length=400, mode='determinate')
        self._progress.pack(fill=tk.X, pady=4)
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", troughcolor=PANEL,
                         background=GREEN, thickness=12)
        self._progress.config(style="green.Horizontal.TProgressbar")

        self._cook_status_lbl = tk.Label(left, text="", font=FONT_SMALL, bg=CARD, fg=MUTED)
        self._cook_status_lbl.pack(anchor="w")

        # Cook log
        tk.Label(left, text="Kitchen Log", font=FONT_BTN, bg=CARD, fg=TEXT).pack(anchor="w", pady=(8, 2))
        self._cook_log = tk.Text(left, bg="#0a1520", fg=GREEN, font=FONT_BODY,
                                  relief=tk.FLAT, bd=0, state=tk.DISABLED, wrap=tk.WORD)
        self._cook_log.pack(fill=tk.BOTH, expand=True)

        # Right side: upgrades
        right = tk.Frame(parent, bg=PANEL, width=230)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=12)
        right.pack_propagate(False)

        tk.Label(right, text="KITCHEN LEVEL", font=FONT_HEAD, bg=PANEL, fg=ACCENT).pack(pady=(10, 2))
        self._level_lbl = tk.Label(right, text="Level 1", font=FONT_STAT, bg=PANEL, fg=GOLD)
        self._level_lbl.pack()
        self._upgrade_cost_lbl = tk.Label(right, text="", font=FONT_SMALL, bg=PANEL, fg=MUTED)
        self._upgrade_cost_lbl.pack()
        styled_btn(right, "UPGRADE KITCHEN", self._upgrade_kitchen, bg=PURPLE, fg="white", width=20).pack(pady=6)

        tk.Frame(right, bg=MUTED, height=1).pack(fill=tk.X, padx=10, pady=10)

    def _on_recipe_select(self, event=None):
        name = self._recipe_var.get()
        recipe = self.cooking.get_recipe(name)
        if not recipe:
            return
        ings = ", ".join(f"{v} {k}" for k, v in recipe.get_ingredients().items())
        info = (f"Ingredients: {ings}\n"
                f"Feeds: {recipe.get_people_fed()} people    "
                f"Waste: {recipe.get_waste()}    "
                f"Level needed: {recipe.get_level_required()}")
        self._recipe_info_lbl.config(text=info)

    def _do_cook(self):
        if self.current_day > 7:
            messagebox.showinfo("Game Over", "Game is complete. Press RESET to play again.")
            return
        recipe_name = self._recipe_var.get()
        if not recipe_name:
            messagebox.showwarning("No Recipe", "Please select a recipe first.")
            return

        success, result = self.cooking.cook(recipe_name, self.inventory, self.compost, customer_manager=None)
        if not success:
            log(self._cook_log, f"✗ FAILED: {result}", RED)
            return

        # Animate progress
        self._cook_btn.config(state=tk.DISABLED)
        for i in range(101):
            self._progress['value'] = i
            self._cook_status_lbl.config(text=f"Cooking {recipe_name}... {i}%")
            self.root.update()
            time.sleep(0.006)
        self._progress['value'] = 0
        self._cook_status_lbl.config(text="")
        self._cook_btn.config(state=tk.NORMAL)

        people_fed, waste, recipe_display, _, _ = result
        portion_count = 1

        existing_food = None
        for f in self._cooked_food:
            if f["recipe"] == recipe_name:
                existing_food = f
                break

        if existing_food:
            existing_food["people"] += portion_count
            existing_food["portions_left"] += portion_count
        else:
            self._cooked_food.append({
                "recipe": recipe_name,
                "people": portion_count,
                "portions_left": portion_count
            })

        pts = self.score.add_points(portion_count, waste)

        log(self._cook_log, f"\n{'─'*48}", MUTED)
        log(self._cook_log, f"  ✅  COOKED: {recipe_display.upper()}", ACCENT)
        log(self._cook_log, f"  👥  Food ready for:   {portion_count} customer", BLUE)
        log(self._cook_log, f"  🗑️   Waste produced: {waste}", RED if waste > 2 else MUTED)
        log(self._cook_log, f"  📌  Click the checkmarks below to serve customers!", ACCENT)
        log(self._cook_log, f"  ⭐  Points earned (cooking): +{pts}", GOLD)
        log(self._cook_log, f"{'─'*48}", MUTED)

        remaining = self.customers.get_remaining_customers()
        if remaining > 0:
            log(self._cook_log, f"  ⏳  {remaining} customer(s) still waiting...", ACCENT)

        self._check_achievements()
        self._refresh_all()

    # ── Inventory Tab ─────────────────────────────────────────────────────────
    def _build_inventory_tab(self, parent):
        tk.Label(parent, text="CURRENT INVENTORY", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(pady=(14, 4))

        self._inv_frame = tk.Frame(parent, bg=CARD)
        self._inv_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def _refresh_inventory_tab(self):
        for w in self._inv_frame.winfo_children():
            w.destroy()

        ingredients = self.inventory.get_all_ingredients()
        max_qty = max(ingredients.values(), default=1) or 1

        for name, qty in ingredients.items():
            row = tk.Frame(self._inv_frame, bg=PANEL, pady=6, padx=12)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=name.capitalize(), font=FONT_BTN, bg=PANEL, fg=TEXT, width=14, anchor="w").pack(side=tk.LEFT)
            # bar
            bar_bg = tk.Frame(row, bg="#223", height=14, width=220)
            bar_bg.pack(side=tk.LEFT, padx=8)
            fill_w = int((qty / max_qty) * 220) if max_qty else 0
            color = GREEN if qty >= 5 else (ACCENT if qty >= 2 else RED)
            tk.Frame(bar_bg, bg=color, height=14, width=max(4, fill_w)).place(x=0, y=0)
            tk.Label(row, text=f"{qty}", font=FONT_BTN, bg=PANEL, fg=color, width=4).pack(side=tk.LEFT)

        # Compost section
        tk.Frame(self._inv_frame, bg=MUTED, height=1).pack(fill=tk.X, pady=10)
        row2 = tk.Frame(self._inv_frame, bg=PANEL, pady=6, padx=12)
        row2.pack(fill=tk.X, pady=3)
        tk.Label(row2, text="♻️ Scraps", font=FONT_BTN, bg=PANEL, fg=TEXT, width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(row2, text=str(self.compost.get_scraps()), font=FONT_BTN, bg=PANEL, fg=MUTED).pack(side=tk.LEFT, padx=8)
        row3 = tk.Frame(self._inv_frame, bg=PANEL, pady=6, padx=12)
        row3.pack(fill=tk.X, pady=3)
        tk.Label(row3, text="🪱 Soil",   font=FONT_BTN, bg=PANEL, fg=TEXT, width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(row3, text=str(self.compost.get_soil()), font=FONT_BTN, bg=PANEL, fg=GREEN).pack(side=tk.LEFT, padx=8)

    # ── Market Tab ────────────────────────────────────────────────────────────
    def _build_market_tab(self, parent):
        tk.Label(parent, text="MARKET", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(pady=(14, 2))
        tk.Label(parent, text="Buy and sell ingredients. Prices shift each day.",
                 font=FONT_SMALL, bg=CARD, fg=MUTED).pack()

        self._market_frame = tk.Frame(parent, bg=CARD)
        self._market_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self._market_log = tk.Text(parent, height=6, bg="#0a1520", fg=GREEN, font=FONT_BODY,
                                    relief=tk.FLAT, state=tk.DISABLED)
        self._market_log.pack(fill=tk.X, padx=20, pady=(0, 10))

    def _refresh_market_tab(self):
        for w in self._market_frame.winfo_children():
            w.destroy()

        headers = tk.Frame(self._market_frame, bg=PANEL, pady=4, padx=12)
        headers.pack(fill=tk.X, pady=(0, 4))
        for col, fg, w in [("Item", MUTED, 12), ("Have", MUTED, 6),
                            ("Buy (pts)", MUTED, 10), ("Sell (pts)", MUTED, 10), ("Actions", MUTED, 22)]:
            tk.Label(headers, text=col, font=FONT_SMALL, bg=PANEL, fg=fg, width=w, anchor="w").pack(side=tk.LEFT)

        for ing, buy_price in self.market.get_prices().items():
            sell_price = self.market.get_sell_prices()[ing]
            qty = self.inventory.get_quantity(ing)
            row = tk.Frame(self._market_frame, bg=CARD, pady=5, padx=12)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=ing.capitalize(), font=FONT_BTN, bg=CARD, fg=TEXT, width=12, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=str(qty), font=FONT_BTN, bg=CARD, fg=BLUE, width=6).pack(side=tk.LEFT)
            tk.Label(row, text=str(buy_price), font=FONT_BTN, bg=CARD, fg=RED, width=10).pack(side=tk.LEFT)
            tk.Label(row, text=str(sell_price), font=FONT_BTN, bg=CARD, fg=GREEN, width=10).pack(side=tk.LEFT)
            btns = tk.Frame(row, bg=CARD)
            btns.pack(side=tk.LEFT)
            styled_btn(btns, "Buy 1", lambda i=ing, p=buy_price: self._market_buy(i, 1, p),
                       bg="#244", fg=TEXT).pack(side=tk.LEFT, padx=2)
            styled_btn(btns, "Buy 3", lambda i=ing, p=buy_price: self._market_buy(i, 3, p),
                       bg="#355", fg=TEXT).pack(side=tk.LEFT, padx=2)
            styled_btn(btns, "Sell 1", lambda i=ing, p=sell_price: self._market_sell(i, 1),
                       bg="#422", fg=TEXT).pack(side=tk.LEFT, padx=2)

    def _market_buy(self, ing, amt, price):
        success, cost = self.market.buy(ing, amt)
        if success:
            log(self._market_log, f"✅ Bought {amt}x {ing} for {cost} pts.", GREEN)
        else:
            log(self._market_log, f"✗ Not enough points. Need {cost} pts.", RED)
        self._refresh_all()

    def _market_sell(self, ing, amt):
        success, earned = self.market.sell(ing, amt)
        if success:
            log(self._market_log, f"💰 Sold {amt}x {ing} for {earned} pts.", GOLD)
        else:
            log(self._market_log, f"✗ Not enough {ing} to sell.", RED)
        self._refresh_all()

    # ── Compost Tab ───────────────────────────────────────────────────────────
    def _build_compost_tab(self, parent):
        tk.Label(parent, text="COMPOSTING SYSTEM", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(pady=(14, 2))
        tk.Label(parent, text="Turn food scraps into soil, then grow vegetables.",
                 font=FONT_SMALL, bg=CARD, fg=MUTED).pack()

        info_frame = tk.Frame(parent, bg=PANEL, padx=20, pady=14)
        info_frame.pack(fill=tk.X, padx=20, pady=12)

        self._compost_scraps_lbl = tk.Label(info_frame, text="Scraps: 0", font=FONT_STAT, bg=PANEL, fg=ACCENT)
        self._compost_scraps_lbl.pack(side=tk.LEFT, expand=True)
        tk.Label(info_frame, text="→  3 scraps = 1 soil  →  2 soil = 3 vegetables",
                 font=FONT_BTN, bg=PANEL, fg=MUTED).pack(side=tk.LEFT, expand=True)
        self._compost_soil_lbl = tk.Label(info_frame, text="Soil: 0", font=FONT_STAT, bg=PANEL, fg=GREEN)
        self._compost_soil_lbl.pack(side=tk.LEFT, expand=True)

        btn_row = tk.Frame(parent, bg=CARD)
        btn_row.pack(pady=10)
        styled_btn(btn_row, "♻️  Convert Scraps → Soil", self._convert_scraps, bg="#5D4037", fg="white").pack(side=tk.LEFT, padx=10)
        styled_btn(btn_row, "🌱  Grow Vegetables (2 soil)", self._grow_veg, bg=GREEN, fg="#000").pack(side=tk.LEFT, padx=10)

        self._compost_log = tk.Text(parent, height=10, bg="#0a1520", fg=GREEN,
                                     font=FONT_BODY, relief=tk.FLAT, state=tk.DISABLED)
        self._compost_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    def _convert_scraps(self):
        soil = self.compost.convert_to_soil()
        if soil > 0:
            log(self._compost_log, f"♻️  Converted {soil*3} scraps → {soil} soil!", GREEN)
        else:
            log(self._compost_log, f"Need at least 3 scraps. Have: {self.compost.get_scraps()}", RED)
        self._refresh_compost()
        self._refresh_inventory_tab()

    def _grow_veg(self):
        success, msg = self.compost.use_soil_to_grow(self.inventory)
        log(self._compost_log, ("🌱 " if success else "✗ ") + msg, GREEN if success else RED)
        self._refresh_compost()
        self._refresh_inventory_tab()

    def _refresh_compost(self):
        self._compost_scraps_lbl.config(text=f"Scraps: {self.compost.get_scraps()}")
        self._compost_soil_lbl.config(text=f"Soil: {self.compost.get_soil()}")

    # ── Customers Tab ─────────────────────────────────────────────────────────
    def _build_customers_tab(self, parent):
        tk.Label(parent, text="TODAY'S CUSTOMERS", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(pady=(14, 2))

        top_row = tk.Frame(parent, bg=CARD)
        top_row.pack(fill=tk.X, padx=20, pady=6)
        self._cust_goal_lbl    = tk.Label(top_row, text="Goal: —",     font=FONT_BTN, bg=CARD, fg=TEXT)
        self._cust_served_lbl  = tk.Label(top_row, text="Served: —",   font=FONT_BTN, bg=CARD, fg=GREEN)
        self._cust_angry_lbl   = tk.Label(top_row, text="Left angry: —", font=FONT_BTN, bg=CARD, fg=RED)
        self._cust_happy_lbl   = tk.Label(top_row, text="Happiness: —", font=FONT_BTN, bg=CARD, fg=BLUE)
        for lbl in [self._cust_goal_lbl, self._cust_served_lbl, self._cust_angry_lbl, self._cust_happy_lbl]:
            lbl.pack(side=tk.LEFT, padx=16)

        self._cust_progress = ttk.Progressbar(parent, length=600, mode='determinate')
        self._cust_progress.pack(pady=6)

        self._cust_frame = tk.Frame(parent, bg=CARD)
        self._cust_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=6)

    def _refresh_customers_tab(self):
        for w in self._cust_frame.winfo_children():
            w.destroy()

        goal    = self.customers.get_daily_goal()
        served  = self.customers.get_served_today()
        angry   = self.customers.get_left_angry()
        happy   = self.customers.get_happiness()
        pct     = self.customers.get_completion_percentage()

        self._cust_goal_lbl.config(text=f"Goal: {goal}")
        self._cust_served_lbl.config(text=f"Served: {served}")
        self._cust_angry_lbl.config(text=f"Left angry: {angry}")
        self._cust_happy_lbl.config(text=f"Happiness: {happy}%",
                                     fg=(GREEN if happy >= 70 else (ACCENT if happy >= 40 else RED)))
        self._cust_progress['value'] = pct

        available_food = {f["recipe"]: f["portions_left"] for f in self._cooked_food}
        display_customers = [c for c in self.customers.get_customers() if c.get("status") != "left_angry"]

        for c in display_customers:
            type_color = BLUE if c.get("type") == "VIP" else (ACCENT if c.get("type") == "Picky" else MUTED)
            if c.get("status") == "served":
                # Already served - show with green checkmark
                row = tk.Frame(self._cust_frame, bg=PANEL, pady=4, padx=10)
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text="✅", font=FONT_BTN, bg=PANEL, fg=GREEN, width=3, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"{c['name']}", font=FONT_BTN, bg=PANEL, fg=TEXT, width=12, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=c.get("type", "Regular"), font=FONT_SMALL, bg=PANEL, fg=type_color, width=8, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"Fav: {c['favorite']}", font=FONT_SMALL, bg=PANEL, fg=MUTED, width=14, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text="Served", font=FONT_BTN, bg=PANEL, fg=GREEN, width=10, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"+{c['reward']} pts", font=FONT_BTN, bg=PANEL, fg=GOLD, anchor="e").pack(side=tk.RIGHT)
            else:
                # Not served - show with empty checkbox and countdown
                row = tk.Frame(self._cust_frame, bg=CARD, pady=4, padx=10)
                row.pack(fill=tk.X, pady=2)
                
                # Calculate turns remaining
                turns_remaining = max(0, c['patience'] - c['wait_time'])
                is_urgent = turns_remaining <= 1
                countdown_color = RED if is_urgent else ACCENT
                
                # Check if cooked food is available for this customer's favorite
                has_match = False
                matched_recipe = None
                if available_food.get(c["favorite"], 0) > 0:
                    has_match = True
                    matched_recipe = c["favorite"]
                    available_food[c["favorite"]] -= 1
                
                # Checkmark button (clickable if there's a match)
                if has_match:
                    btn = tk.Button(row, text="✓", font=("Arial", 14, "bold"), bg=GREEN, fg="#000",
                                   relief=tk.FLAT, cursor="hand2", width=2, padx=0,
                                   command=lambda cid=c["id"], recipe=matched_recipe: self._serve_customer(cid, recipe))
                    btn.pack(side=tk.LEFT, padx=(0, 5))
                else:
                    tk.Label(row, text="○", font=("Arial", 14), bg=CARD, fg=MUTED, width=2).pack(side=tk.LEFT, padx=(0, 5))
                
                tk.Label(row, text=f"{c['name']}", font=FONT_BTN, bg=CARD, fg=TEXT, width=12, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=c.get("type", "Regular"), font=FONT_SMALL, bg=CARD, fg=type_color, width=8, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"Fav: {c['favorite']}", font=FONT_SMALL, bg=CARD, fg=MUTED, width=14, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"Turns: {turns_remaining}", font=FONT_BTN, bg=CARD, fg=countdown_color, width=10, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"+{c['reward']} pts", font=FONT_BTN, bg=CARD, fg=GOLD, anchor="e").pack(side=tk.RIGHT)
    
    def _serve_customer(self, customer_id, recipe_name):
        """Manually serve a customer with a cooked dish."""
        # Find the customer
        customer = None
        for c in self.customers.get_customers():
            if c["id"] == customer_id:
                customer = c
                break
        
        if not customer or customer.get("status") != "waiting":
            return
        
        # Find the cooked food
        food = None
        for f in self._cooked_food:
            if f["recipe"] == recipe_name and f["portions_left"] > 0:
                food = f
                break
        
        if not food:
            return
        
        # Serve the customer
        customer["status"] = "served"
        food["portions_left"] -= 1
        points = customer["reward"]
        
        self.score.add_bonus(points)
        self.customers._happiness = min(100, self.customers._happiness + 2)
        
        log(self._cook_log, f"🤝 {customer['name']} served {recipe_name}! +{points} pts", GREEN)
        
        # Remove food if all portions used
        self._cooked_food = [f for f in self._cooked_food if f["portions_left"] > 0]

        if self.customers.get_remaining_customers() == 0 and self._phase == "day":
            if self._timer_id:
                self.root.after_cancel(self._timer_id)
                self._timer_id = None
            self._start_transition()
        else:
            self._refresh_all()

    # ── Achievements Tab ──────────────────────────────────────────────────────
    def _build_achievements_tab(self, parent):
        tk.Label(parent, text="ACHIEVEMENTS", font=FONT_HEAD, bg=CARD, fg=ACCENT).pack(pady=(14, 4))
        self._ach_frame = tk.Frame(parent, bg=CARD)
        self._ach_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=6)

    def _refresh_achievements_tab(self):
        for w in self._ach_frame.winfo_children():
            w.destroy()

        for key, ach in self.achievements.get_achievements().items():
            earned = ach.is_earned()
            row = tk.Frame(self._ach_frame, bg=PANEL if earned else CARD, pady=7, padx=14)
            row.pack(fill=tk.X, pady=3)
            icon = "🏅" if earned else "🔒"
            name_color = GOLD if earned else MUTED
            tk.Label(row, text=f"{icon}  {ach.get_name()}", font=FONT_BTN,
                     bg=row['bg'], fg=name_color, width=22, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=ach.get_description(), font=FONT_SMALL,
                     bg=row['bg'], fg=TEXT if earned else MUTED, width=32, anchor="w").pack(side=tk.LEFT)
            reward_lbl = f"+{ach.get_reward()} pts" if earned else f"Req: {ach.get_requirement()}"
            tk.Label(row, text=reward_lbl, font=FONT_BTN,
                     bg=row['bg'], fg=GREEN if earned else MUTED).pack(side=tk.RIGHT)

        self._refresh_stats()

    # ── Kitchen Upgrade ───────────────────────────────────────────────────────
    def _upgrade_kitchen(self):
        available_before = set(self.cooking.get_recipes())
        success, cost = self.cooking.upgrade_kitchen(self.score.get_current_score())
        if success:
            self.score.deduct(cost)
            level = self.cooking.get_chef_level()
            available_after = set(self.cooking.get_recipes())
            unlocked = sorted(available_after - available_before)
            log(self._cook_log, f"⬆️  Kitchen upgraded to Level {level}!", PURPLE)
            if unlocked:
                log(self._cook_log, f"  🍳 New recipes unlocked: {', '.join(unlocked)}", ACCENT)
            self._refresh_all()
            messagebox.showinfo("Kitchen Upgraded", f"Level {level}! New recipes may now be available.")
        else:
            messagebox.showwarning("Upgrade Failed", f"Need {cost} pts to upgrade. You have {self.score.get_current_score()}.")

    # ── Next Day ──────────────────────────────────────────────────────────────
    # ── Achievements check ────────────────────────────────────────────────────
    def _check_achievements(self):
        stats     = self.score.get_stats()
        level     = self.cooking.get_chef_level()
        waste     = self.score.get_waste()
        happiness = self.customers.get_happiness()
        day       = self.current_day

        new_rewards = self.achievements.check_achievements(stats, level, waste, happiness, day)
        for reward in new_rewards:
            self.score.add_bonus(reward)
            log(self._cook_log, f"🏅 ACHIEVEMENT UNLOCKED! +{reward} pts!", GOLD)

        self._refresh_achievements_tab()

    # ── End Game ──────────────────────────────────────────────────────────────
    def _end_game(self):
        # Cancel timer
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        
        mult = self.difficulty_mgr.get_score_multiplier()
        final_pts = int(self.score.get_current_score() * mult)
        # Apply difficulty multiplier
        self.score._score._current_score = final_pts
        self.score.save_high_score()
        self.score.save_final_score()

        msg = (f"Game Complete!\n\n"
               f"Final Score:    {self.score.get_current_score()}\n"
               f"High Score:     {self.score.get_high_score()}\n"
               f"People Fed:     {self.score.get_people_fed()}\n"
               f"Total Waste:    {self.score.get_waste()}\n"
               f"Happiness:      {self.customers.get_happiness()}%\n"
               f"Difficulty:     {self.difficulty_mgr.get_difficulty().upper()}\n"
               f"Score Mult:     ×{mult}")
        log(self._cook_log, f"\n{'═'*48}", GOLD)
        log(self._cook_log, "  🎉  GAME COMPLETE!", GOLD)
        for line in msg.split("\n")[2:]:
            log(self._cook_log, f"  {line}", TEXT)
        log(self._cook_log, f"{'═'*48}", GOLD)
        messagebox.showinfo("🎉 Game Complete!", msg)
        self._refresh_stats()

    # ── Refresh All ───────────────────────────────────────────────────────────
    def _refresh_all(self):
        self._refresh_stats()
        self._refresh_recipes_dropdown()
        self._refresh_inventory_tab()
        self._refresh_market_tab()
        self._refresh_compost()
        self._refresh_customers_tab()
        self._refresh_achievements_tab()

    def _refresh_stats(self):
        self._stat_vars["DAY"].set(f"{min(self.current_day, 7)}/7")
        self._stat_vars["SCORE"].set(str(self.score.get_current_score()))
        self._stat_vars["PEOPLE FED"].set(str(self.score.get_people_fed()))
        self._level_lbl.config(text=f"Level {self.cooking.get_chef_level()}")
        cost = self.cooking.get_chef_level() * 30
        self._upgrade_cost_lbl.config(text=f"Next upgrade: {cost} pts")

    def _refresh_recipes_dropdown(self):
        available = self.cooking.get_recipes()
        self._recipe_cb['values'] = available
        if available and self._recipe_var.get() not in available:
            self._recipe_cb.current(0)
            self._on_recipe_select()

    def _trigger_day_start_log(self):
        log_clear(self._cook_log)
        log(self._cook_log, "FOOD QUEST — Community Kitchen", ACCENT)
        log(self._cook_log, f"Difficulty: {self.difficulty_mgr.get_difficulty().upper()}", MUTED)
        log(self._cook_log, f"{'═'*48}", MUTED)
        log(self._cook_log, f"  DAY 1 / 7 — Let's feed the community!", GOLD)
        log(self._cook_log, f"  👥 {self.customers.get_daily_goal()} customers waiting.", TEXT)
        log(self._cook_log, f"  Select a recipe and press COOK to begin.", MUTED)

    # ── Timer System ──────────────────────────────────────────────────────────
    def _start_timer(self):
        """Start the day/night countdown timer."""
        self._update_timer()
    
    def _format_clock(self, minutes):
        hours = (minutes // 60) % 24
        mins = minutes % 60
        period = "AM" if hours < 12 else "PM"
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{mins:02d} {period}"

    def _update_timer(self):
        """Update timer display and handle phase transitions."""
        self._clock_time += 1  # Increment by 1 minute every iteration (fast clock)

        # Phase display
        if self._phase == "day":
            phase_name = "DAY"
        else:
            next_day = min(self.current_day + 1, 7)
            phase_name = f"TRANSITION to Day {next_day}"

        self._phase_label.config(text=f"Day {self.current_day} - {phase_name}")
        self._timer_label.config(text=self._format_clock(self._clock_time))

        if self._phase == "day":
            self._timer_label.config(fg=GOLD)
        else:
            self._timer_label.config(fg=BLUE)

        # Check phase transitions by clock time
        if self._phase == "day" and self._clock_time >= 1440:
            self._start_transition()
        elif self._phase == "transition" and self._clock_time >= 300:
            self._start_new_day()
        else:
            self._timer_id = self.root.after(100, self._update_timer)
    
    def _start_transition(self):
        """Begin the transition period from 12:00 AM to 5:00 AM."""
        self._phase = "transition"
        self._clock_time = 0  

        left = self.customers.close_day()
        if left > 0:
            log(self._cook_log, f"😠  {left} customer(s) left hungry and angry!", RED)

        next_day = min(self.current_day + 1, 7)
        log(self._cook_log, f"\n⏳ Transitioning to Day {next_day} from 12:00 AM to 5:00 AM...", ACCENT)
        self._refresh_all()
        self._timer_id = self.root.after(100, self._update_timer)

    def _start_new_day(self):
        """Begin the next day at 5:00 AM."""
        self.current_day += 1
        if self.current_day > 7:
            self._end_game()
            return

        self._phase = "day"
        self._clock_time = 300  # 5:00 AM
        self.score.next_day()
        self._cooked_food = []

        left = self.customers.update_waiting()
        if left > 0:
            log(self._cook_log, f"😠  {left} customer(s) left hungry and angry!", RED)

        if self.customers.get_remaining_customers() == 0 and self.customers.get_served_today() > 0:
            self.score.mark_perfect_day()
            self.score.add_bonus(10)
            log(self._cook_log, f"🌟 PERFECT DAY! +10 bonus pts!", GOLD)

        self.customers.reset_daily()
        num = self.customers.generate_daily_customers(self.current_day, self.difficulty_mgr.get_difficulty())
        self.market.update_prices()

        restock_n = self.difficulty_mgr.get_restock_amount()
        restocked = []
        ings = ["rice", "water", "vegetables", "salt"]
        for _ in range(restock_n):
            ing = random.choice(ings)
            self.inventory.add_ingredient(ing, 1)
            restocked.append(ing)

        log(self._cook_log, f"\n{'═'*48}", MUTED)
        log(self._cook_log, f"  DAY {self.current_day} / 7", ACCENT)
        log(self._cook_log, f"{'═'*48}", MUTED)
        log(self._cook_log, f"  📦 Restocked: {', '.join(restocked)}", BLUE)
        log(self._cook_log, f"  👥 {num} new customers arrived.", TEXT)

        self._check_achievements()
        self._refresh_all()
        self._timer_id = self.root.after(100, self._update_timer)

    # ── Reset ─────────────────────────────────────────────────────────────────
    def _confirm_reset(self):
        if messagebox.askyesno("Reset Game", "Start over? All progress will be lost."):
            if self._timer_id:
                self.root.after_cancel(self._timer_id)
            self._show_start_screen()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FoodQuestGUI()
    app.run()