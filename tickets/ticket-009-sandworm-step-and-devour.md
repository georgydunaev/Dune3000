# Ticket 9: Implement Sandworm Hunting Step and Unit Devouring (`Sandworm.step`)

**State:** open
**Priority:** high

## Description
Add a method `step(self, game_state: "GameState") -> Optional[Unit]` on `Sandworm` in `/botworkspace/dune3000/dune3000/engine.py`:
1. Find the nearest vulnerable unit via `target = self.find_nearest_target(game_state.units, game_state.game_map)`.
2. If `target is None`, return `None`.
3. Move the sandworm 1 step closer to `target`:
   - If `self.x < target.x`: `self.x += 1`
   - Elif `self.x > target.x`: `self.x -= 1`
   - Elif `self.y < target.y`: `self.y += 1`
   - Elif `self.y > target.y`: `self.y -= 1`
4. If `(self.x, self.y) == (target.x, target.y)`, devour the unit: set `target.hp = 0`, remove `target` from `game_state.units` if present, and return `target`. Otherwise return `None`.
5. Add a unit test `test_sandworm_step_and_devour` in `/botworkspace/dune3000/tests/test_engine.py` and run `python3 -m unittest discover tests`.
