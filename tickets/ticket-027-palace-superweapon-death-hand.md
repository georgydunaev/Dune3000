# Ticket 27: Implement Palace Superweapon Death Hand Missile Strike (`GameState.fire_death_hand`)
**State:** open
**Labels:** dune3000

## Context
In Dune 2000, constructing a Palace unlocks devastating superweapons such as the Death Hand missile, which inflicts heavy area-of-effect splash damage around a target coordinate.

## Acceptance Criteria
1. Add `"Palace": 600` to `BUILDING_COSTS` in `/botworkspace/dune3000/dune3000/engine.py` (preserving existing keys).
2. Add a method `fire_death_hand(self, house: str, target_x: int, target_y: int) -> int` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - Verify that `house` has at least one alive (`hp > 0`) building with `building_type == "Palace"`. If not, return `0`.
   - For every alive (`hp > 0`) enemy unit (`u.house != house`) in `self.units` and every alive (`hp > 0`) enemy building (`b.house != house`) in `self.buildings`:
     - Let `dist = abs(obj.x - target_x) + abs(obj.y - target_y)`.
     - If `dist == 0`, apply `150` damage (`actual = min(obj.hp, 150); obj.hp -= actual`).
     - Else if `dist == 1`, apply `75` damage (`actual = min(obj.hp, 75); obj.hp -= actual`).
   - Return the total `actual` damage dealt across all hit enemy units and buildings.
3. Add a unit test `test_fire_death_hand` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - Without a `Palace`, `fire_death_hand` returns `0` and deals no damage.
   - With a `Palace`, enemy targets at distance `0` and `1` take splash damage while friendly units are unharmed.
4. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
