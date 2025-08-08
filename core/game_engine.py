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
        # cost to buy NEXT pump
        return math.ceil(50 * (1.15 ** (self.gas_pumps - 1)))

    def upgrade_pump_cost(self) -> int:
        return math.ceil(10 * (1.25 ** (self.gas_pump_level - 1)))

    def upgrade_store_cost(self) -> int:
        return math.ceil(20 * (1.20 ** (self.store_level - 1)))

    # --- Income ---
    def calculate_income(self) -> None:
        base = (self.gas_pumps * self.gas_pump_level) + (self.store_level * 2)
        self.income_per_second = base * self.remodel_multiplier * self.prestige_multiplier

    def tick(self, seconds: int = 1) -> None:
        self.calculate_income()
        self.currency += self.income_per_second * seconds

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

