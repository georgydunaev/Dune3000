# Ticket 18: Implement Fog of War and Sight Radius Visibility (`GameState.compute_visibility`)

**State:** closed
**Labels:** dune3000, gameplay, rts

## Context
In Dune 2000, players only see terrain and enemy forces within the sight radius of their alive buildings (radius 4) and alive units (radius 3).

## Acceptance Criteria
1. Add method `compute_visibility(self, house: str) -> set` on `GameState` in `dune3000/engine.py`:
   - Returns a `set` of `(x, y)` integer coordinate tuples that are in bounds on `self.game_map`.
   - Every alive (`hp > 0`) building owned by `house` reveals all in-bounds tiles `(tx, ty)` with Manhattan distance `abs(b.x - tx) + abs(b.y - ty) <= 4`.
   - Every alive (`hp > 0`) unit owned by `house` reveals all in-bounds tiles `(tx, ty)` with Manhattan distance `abs(u.x - tx) + abs(u.y - ty) <= 3`.
2. Add a unit test `test_compute_visibility` inside `TestDune3000Engine` in `tests/test_engine.py` verifying sight radius reveal for alive units/buildings and that dead (`hp == 0`) or enemy entities do not reveal tiles for `house`.
3. Run `python3 -m unittest discover tests` and ensure all tests pass.
