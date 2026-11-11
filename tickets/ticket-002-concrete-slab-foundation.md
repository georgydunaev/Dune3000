# Ticket 2: Implement Concrete Slab Foundation Penalty on Building Placement

- **State:** open
- **Labels:** feature, engine

## Description
In `/botworkspace/dune3000/dune3000/engine.py`, add a method `place_building(self, building: Building) -> Building` on `GameState`:
1. Check `tile = self.game_map.get_tile(building.x, building.y)`.
2. If `tile == CONCRETE`, keep `building.hp = building.max_hp`.
3. If `tile == ROCK`, set `building.hp = max(1, building.max_hp // 2)` (50% foundation penalty without concrete slab).
4. Append `building` to `self.buildings` and return `building`.
5. Add unit tests in `/botworkspace/dune3000/tests/test_engine.py` and verify with `python3 -m unittest discover tests`.
