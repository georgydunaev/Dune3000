# Ticket 26: Implement CHOAM Starport Dynamic Pricing & Unit Delivery (`GameState.order_starport_unit`)
**State:** open
**Labels:** dune3000

## Context
In Dune 2000, building a Starport allows a House to order units from the CHOAM merchant guild at fluctuating market prices depending on the current game tick.

## Acceptance Criteria
1. Add `"Starport": 500` to `BUILDING_COSTS` in `/botworkspace/dune3000/dune3000/engine.py` (keep existing keys intact).
2. Add a method `order_starport_unit(self, house: str, unit_type: str, x: int, y: int) -> Optional[Unit]` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - Check if `house` owns at least one alive (`hp > 0`) building with `building_type == "Starport"`. If not, return `None`.
   - Compute base cost `base = UNIT_COSTS.get(unit_type, 200)`.
   - Compute dynamic CHOAM price: if `self.tick_count % 2 == 0`, `price = int(base * 0.8)` (20% discount on even ticks); otherwise `price = int(base * 1.2)` (20% surge on odd ticks).
   - If `self.credits.get(house, 0) < price`, return `None`.
   - Deduct `price` from `self.credits[house]`, create `Unit(unit_type=unit_type, house=house, x=x, y=y)`, append it to `self.units`, and return the created `Unit`.
3. Add a unit test `test_order_starport_unit` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - Ordering without a `Starport` returns `None`.
   - Ordering on an even tick applies the `0.8` discount multiplier, deducts credits, and spawns the unit.
   - Ordering on an odd tick applies the `1.2` multiplier.
4. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
