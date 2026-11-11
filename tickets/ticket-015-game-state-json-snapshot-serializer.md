# Ticket 15: Implement JSON Snapshot Serializer (`GameState.to_dict`)

**State:** closed
**Priority:** medium

## Description
Add a `to_dict(self) -> Dict` method on `GameState` in `/botworkspace/dune3000/dune3000/engine.py` for serializing the game state to the browser UI:
1. Return a dictionary with keys:
   - `"width"`: `self.game_map.width`
   - `"height"`: `self.game_map.height`
   - `"tiles"`: `self.game_map.tiles`
   - `"credits"`: `dict(self.credits)`
   - `"buildings"`: list of dicts `{"building_type": b.building_type, "house": b.house, "x": b.x, "y": b.y, "hp": b.hp, "max_hp": b.max_hp}` for `b` in `self.buildings`
   - `"units"`: list of dicts `{"unit_type": u.unit_type, "house": u.house, "x": u.x, "y": u.y, "hp": u.hp, "max_hp": u.max_hp, "spice_carried": u.spice_carried}` for `u` in `self.units`
   - `"sandworms"`: list of dicts `{"x": w.x, "y": w.y}` for `w` in `self.sandworms`
2. Add a unit test `test_game_state_to_dict` in `/botworkspace/dune3000/tests/test_engine.py` and run `python3 -m unittest discover tests`.
