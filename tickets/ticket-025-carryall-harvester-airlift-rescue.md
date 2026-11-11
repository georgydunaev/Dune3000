# Ticket 25: Implement Carryall Airlift Rescue of Harvesters from Sandworms (`GameState.step_carryall_rescue`)
**State:** open
**Labels:** dune3000

## Context
In Dune 2000, Carryall transport aircraft automatically rescue Spice Harvesters when a Sandworm approaches close to them, airlifting the Harvester back to the House's Refinery tile.

## Acceptance Criteria
1. Add a method `step_carryall_rescue(self, house: str) -> int` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - Find the first alive (`hp > 0`) `Refinery` building in `self.buildings` owned by `house`. If none exists, or if `self.power_efficiency(house) < 0.5`, return `0`.
   - For each alive (`hp > 0`) unit `u` in `self.units` where `u.house == house` and `u.unit_type == "Harvester"`:
     - If `(u.x, u.y) == (refinery.x, refinery.y)`, skip it (already at refinery).
     - Check if any `w` in `self.sandworms` is within Manhattan distance `abs(u.x - w.x) + abs(u.y - w.y) <= 2`.
     - If so, airlift the harvester by setting `u.x = refinery.x` and `u.y = refinery.y`, and increment the rescued count.
   - Return the integer count of rescued Harvesters.
2. Add a unit test `test_step_carryall_rescue` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - A Harvester within Manhattan distance `<= 2` of a `Sandworm` is moved to its house's `Refinery` coordinates and count `1` is returned.
   - If no `Refinery` exists or `power_efficiency < 0.5`, no rescue occurs (`0` returned).
3. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
