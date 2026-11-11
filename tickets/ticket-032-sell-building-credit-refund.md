# Ticket 32: Implement Sell Structure for Proportional Credit Refund (`GameState.sell_building`)
**State:** closed
**Labels:** dune3000

## Context
In Dune 2000, commanders can sell any existing structure to recover up to 50% of its construction cost proportional to its remaining hit points.

## Acceptance Criteria
1. Add a method `sell_building(self, building: Building) -> int` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - If `building not in self.buildings` or `building.hp <= 0`, return `0`.
   - Look up `cost = BUILDING_COSTS.get(building.building_type, 250)`.
   - Compute `refund = max(1, int((cost * building.hp) // (2 * building.max_hp)))`.
   - Set `building.hp = 0`, remove `building` from `self.buildings`, and add `refund` to `self.credits[building.house]` via `self.add_credits(building.house, refund)`.
   - Return `refund`.
2. Add a unit test `test_sell_building` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - Selling a full-HP `Refinery` (cost 400) refunds `200` credits, removes the building from `gs.buildings`, and sets `building.hp = 0`.
   - Selling a half-HP `Refinery` (hp 200/400) refunds `100` credits.
   - Selling a building not in `gs.buildings` returns `0`.
3. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
