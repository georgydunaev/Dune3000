# Ticket 026: Economic Trade System — Buy and Sell Spice at Market Prices

**State:** open
**Labels:** dune3000, economy, mechanics

## Acceptance Criteria

Add a `trade_spice()` method to `GameState` in `dune3000/engine.py` that allows houses to buy and sell spice at dynamic market prices. This adds a new economic dimension beyond harvesting, building construction, and unit training, enabling players to manage spice liquidity when their capacity is full or when they need immediate credits.

**Changes to `dune3000/engine.py`:**
- Add a `trade_spice(house: str, amount: int, buy: bool) -> int` method to `GameState` that:
  - When `buy=True`: Spends `amount * 2` credits to increase the house's spice carried by `amount` (market buy price: 2 credits per spice unit).
  - When `buy=False` (sell): Gains `amount * 3` credits by decreasing the house's spice carried by `amount` (market sell price: 3 credits per spice unit).
  - Validates that the house has sufficient spice to sell (`spice_carried >= amount` when `buy=False`).
  - Validates that the house has sufficient credits to buy (`credits >= amount * 2` when `buy=True`).
  - Clamps spice carried to `max_spice_capacity(house)` — buying spice that exceeds capacity is rejected.
  - Returns the actual amount of spice traded (may be less than requested if resources are insufficient).
  - Does nothing and returns 0 if the house is unknown or has insufficient resources.

**Changes to `tests/test_engine.py`:**
- Add a new test method `test_trade_spice` within the `TestDune3000Engine` class that verifies:
  - Successful purchase of spice reduces credits and increases `spice_carried` for the house.
  - Successful sale of spice increases credits and decreases `spice_carried` for the house.
  - Insufficient spice to sell returns 0 and leaves state unchanged.
  - Insufficient credits to buy returns 0 and leaves state unchanged.
  - Buying spice that would exceed `max_spice_capacity` is rejected (returns 0, state unchanged).
  - The method works correctly for all three houses (Atreides, Harkonnen, Ordos).
  - Unknown houses return 0 without modifying state.

**Example test logic:**
```python
def test_trade_spice(self):
    gs = GameState(GridMap(8, 8))
    # Buy 50 spice: cost = 50 * 2 = 100 credits
    result = gs.trade_spice("Atreides", 50, buy=True)
    self.assertEqual(result, 50)
    self.assertEqual(gs.credits["Atreides"], 900)  # 1000 - 100
    self.assertEqual(gs.units[0].spice_carried, 50)  # assuming a harvester or just tracking

    # Sell 30 spice: gain = 30 * 3 = 90 credits
    result = gs.trade_spice("Atreides", 30, buy=False)
    self.assertEqual(result, 30)
    self.assertEqual(gs.credits["Atreides"], 990)  # 900 + 90
    self.assertEqual(gs.units[0].spice_carried, 20)  # 50 - 30
```