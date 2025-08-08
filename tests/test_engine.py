from core.game_engine import PitStopGame

def test_tick_increases_currency():
    g = PitStopGame()
    start = g.currency
    g.tick(5)
    assert g.currency > start

def test_remodel_multiplier_applies():
    g = PitStopGame()
    g.remodel()
    g.tick(1)
    assert g.income_per_second > 0
    assert g.remodel_multiplier >= 1.1

def test_prestige_resets_and_scales():
    g = PitStopGame()
    g.prestige()
    assert g.prestige_multiplier >= 2.0
    assert g.remodel_multiplier == 1.0
    assert g.gas_pumps == 1 and g.gas_pump_level == 1 and g.store_level == 1

