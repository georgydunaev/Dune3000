# Ticket 29: Implement Arrakis Coriolis Sandstorm Weather Hazard (`GameState.apply_sandstorm`)
**State:** open
**Labels:** dune3000

## Context
Coriolis sandstorms sweep across the open desert of Arrakis, damaging units caught on exposed sand or spice tiles while units positioned on `ROCK` or `CONCRETE` foundations are sheltered.

## Acceptance Criteria
1. Add a method `apply_sandstorm(self, center_x: int, center_y: int, radius: int = 2) -> int` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - For each alive (`hp > 0`) unit `u` in `self.units`:
     - If `abs(u.x - center_x) + abs(u.y - center_y) <= radius`:
       - Check `tile = self.game_map.get_tile(u.x, u.y)`.
       - If `tile not in (ROCK, CONCRETE)`, reduce `u.hp = max(0, u.hp - 15)` and increment `damaged_count`.
   - Return `damaged_count` (the number of units damaged by the sandstorm).
2. Add a unit test `test_apply_sandstorm` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - Units on `SAND` or `SPICE_THICK` within `radius` lose `15` HP and are counted.
   - Units on `ROCK` or `CONCRETE` within `radius`, or units outside `radius`, take `0` damage.
3. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
