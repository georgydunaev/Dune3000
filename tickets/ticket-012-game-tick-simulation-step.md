# Ticket 12: Implement Simulation Tick Step (`GameState.step_tick`)

**State:** open
**Priority:** high

## Description
Add a simulation tick counter and `step_tick` method on `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
1. Add default field `tick_count: int = 0` on `GameState`.
2. Add method `step_tick(self) -> Dict[str, int]` on `GameState`:
   - Increment `self.tick_count += 1`.
   - Remove destroyed buildings (`self.buildings = [b for b in self.buildings if b.hp > 0]`) and destroyed units (`self.units = [u for u in self.units if u.hp > 0]`).
   - For each unit `u` in `self.units` with `u.unit_type == "Harvester"`, find the first building `b` in `self.buildings` with `b.house == u.house and b.building_type == "Refinery"` (or `None`), and call `u.step_harvest(self.game_map, refinery, self)`, accumulating `total_deposited`.
   - Return `{"tick": self.tick_count, "spice_deposited": total_deposited, "alive_units": len(self.units), "alive_buildings": len(self.buildings)}`.
3. Add a unit test `test_game_state_step_tick` in `/botworkspace/dune3000/tests/test_engine.py` and run `python3 -m unittest discover tests`.
