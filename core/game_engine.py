# core/game_engine.py
import math
from typing import Optional, Dict, Any

class PitStopGame:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        # Base state
        self.currency: float = 0.0
        self.gas_pumps: int = 1
        self.gas_pump_level: int = 1
        self.store_level: int = 1
        self.propane_tanks_level: int = 0
        self.arcade_level: int = 0
        self.drinks_level: int = 0
        self.lottery_level: int = 0
        self.carwash_level: int = 0
        self.restaurant_level: int = 0
        self.hotel_level: int = 0
        self.income_per_second: float = 0.0
        self.remodel_count: int = 0
        self.prestige_count: int = 0

        # New: progression multipliers
        self.remodel_multiplier: float = 1.0
        self.prestige_multiplier: float = 1.0

        if data:
            self.__dict__.update(data)

    # --- Costs (tweak these if growth feels off) ---
    def pump_cost(self) -> int:
        return math.ceil(50 * (1.15 ** (self.gas_pumps - 1)))

    def upgrade_pump_cost(self) -> int:
        return math.ceil(10 * (1.25 ** (self.gas_pump_level - 1)))

    def upgrade_store_cost(self) -> int:
        return math.ceil(20 * (1.20 ** (self.store_level - 1)))
        
    def upgrade_propane_cost(self) -> int:
        return math.ceil(50 * (1.3 ** self.propane_tanks_level))

    def upgrade_arcade_cost(self) -> int:
        return math.ceil(100 * (1.4 ** self.arcade_level))

    def upgrade_drinks_cost(self) -> int:
        return math.ceil(75 * (1.35 ** self.drinks_level))

    def upgrade_lottery_cost(self) -> int:
        return math.ceil(200 * (1.5 ** self.lottery_level))

    def upgrade_carwash_cost(self) -> int:
        return math.ceil(300 * (1.6 ** self.carwash_level))

    def upgrade_restaurant_cost(self) -> int:
        return math.ceil(500 * (1.7 ** self.restaurant_level))

    def upgrade_hotel_cost(self) -> int:
        return math.ceil(1000 * (1.8 ** self.hotel_level))

    # --- Income ---
    def calculate_income(self) -> None:
        base = (
            (self.gas_pumps * self.gas_pump_level) +
            (self.store_level * 2) +
            (self.propane_tanks_level * 5) +
            (self.arcade_level * 10) +
            (self.drinks_level * 7) +
            (self.lottery_level * 15) +
            (self.carwash_level * 25) +
            (self.restaurant_level * 50) +
            (self.hotel_level * 100)
        )
        self.income_per_second = base * self.remodel_multiplier * self.prestige_multiplier

    def tick(self, seconds: int = 1) -> None:
        self.calculate_income()
        self.currency += self.income_per_second * seconds
        self.currency = int(self.currency) # No fractions

    # --- Actions ---
    def upgrade_gas_pump(self) -> bool:
        cost = self.upgrade_pump_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.gas_pump_level += 1
            return True
        return False

    def buy_gas_pump(self) -> bool:
        cost = self.pump_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.gas_pumps += 1
            return True
        return False

    def upgrade_store(self) -> bool:
        cost = self.upgrade_store_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.store_level += 1
            return True
        return False
        
    def upgrade_propane(self) -> bool:
        cost = self.upgrade_propane_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.propane_tanks_level += 1
            return True
        return False

    def upgrade_arcade(self) -> bool:
        cost = self.upgrade_arcade_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.arcade_level += 1
            return True
        return False

    def upgrade_drinks(self) -> bool:
        cost = self.upgrade_drinks_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.drinks_level += 1
            return True
        return False

    def upgrade_lottery(self) -> bool:
        cost = self.upgrade_lottery_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.lottery_level += 1
            return True
        return False

    def upgrade_carwash(self) -> bool:
        cost = self.upgrade_carwash_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.carwash_level += 1
            return True
        return False
        
    def upgrade_restaurant(self) -> bool:
        cost = self.upgrade_restaurant_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.restaurant_level += 1
            return True
        return False

    def upgrade_hotel(self) -> bool:
        cost = self.upgrade_hotel_cost()
        if self.currency >= cost:
            self.currency -= cost
            self.hotel_level += 1
            return True
        return False

    def remodel(self) -> float:
        # +10% income each remodel (stacking)
        self.remodel_multiplier *= 1.10
        self.currency = 0.0
        self.gas_pumps = 1
        self.gas_pump_level = 1
        self.store_level = 1
        self.remodel_count += 1
        return self.remodel_multiplier

    def prestige(self) -> None:
        # Full reset; double income each prestige (example)
        self.currency = 0.0
        self.gas_pumps = 1
        self.gas_pump_level = 1
        self.store_level = 1
        self.remodel_count = 0
        self.remodel_multiplier = 1.0
        self.prestige_multiplier *= 2.0
        self.prestige_count += 1

    def get_state(self) -> Dict[str, Any]:
        return self.__dict__

