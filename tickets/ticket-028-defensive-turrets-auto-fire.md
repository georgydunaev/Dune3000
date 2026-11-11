# Ticket 28: Implement Base Defense Turrets (`GunTurret` and `RocketTurret`) Auto-Fire (`GameState.step_turrets`)
**State:** open
**Labels:** dune3000

## Context
In Dune 2000, bases are defended by Gun Turrets (short range, works even on low power) and Rocket Turrets (long range, requires full power efficiency `>= 1.0` to operate).

## Acceptance Criteria
1. Add `"GunTurret": 250` and `"RocketTurret": 350` to `BUILDING_COSTS` in `/botworkspace/dune3000/dune3000/engine.py`.
2. Add a method `step_turrets(self) -> int` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - Iterate over all alive (`hp > 0`) buildings `b` in `self.buildings`:
     - If `b.building_type == "GunTurret"`: `rng = 3`, `dmg = 30`.
     - Else if `b.building_type == "RocketTurret"`:
       - Check `self.power_efficiency(b.house) >= 1.0`. If `< 1.0`, skip this turret (cannot fire under low power).
       - Otherwise `rng = 5`, `dmg = 45`.
     - Else: continue.
     - Find the first alive (`u.hp > 0`) enemy unit (`u.house != b.house`) in `self.units` with Manhattan distance `abs(u.x - b.x) + abs(u.y - b.y) <= rng`.
     - If found, deal `actual = min(u.hp, dmg)` damage (`u.hp -= actual`) and add `actual` to `total_damage`.
   - Return `total_damage`.
3. Add a unit test `test_step_turrets` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - `GunTurret` damages an enemy within range `3`.
   - `RocketTurret` fires at range `5` when `power_efficiency >= 1.0`, and does not fire when `power_efficiency < 1.0`.
4. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
