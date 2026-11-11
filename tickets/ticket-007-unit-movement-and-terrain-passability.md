# Ticket 7: Implement Unit Movement and Bounds Clamping (`Unit.move_towards`)

**State:** open
**Priority:** high

## Description
Add a method `move_towards(self, target_x: int, target_y: int, game_map: "GridMap") -> Tuple[int, int]` on `Unit` in `/botworkspace/dune3000/dune3000/engine.py`:
1. If `self.x < target_x`, set `nx = self.x + 1`; elif `self.x > target_x`, set `nx = self.x - 1`; else `nx = self.x`.
2. If `nx != self.x`, set `ny = self.y` (move 1 cardinal tile step along X first). Otherwise, if `self.y < target_y`, set `ny = self.y + 1`; elif `self.y > target_y`, set `ny = self.y - 1`; else `ny = self.y`.
3. Clamp `nx` to `0 <= nx < game_map.width` and `ny` to `0 <= ny < game_map.height`.
4. Update `self.x = nx` and `self.y = ny`, and return `(self.x, self.y)`.
5. Add a unit test `test_unit_move_towards` in `/botworkspace/dune3000/tests/test_engine.py` and run `python3 -m unittest discover tests`.
