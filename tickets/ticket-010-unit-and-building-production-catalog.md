# Ticket 10: Implement Unit Production Catalog and `GameState.train_unit`

**State:** open
**Priority:** high

## Description
Add unit production to `/botworkspace/dune3000/dune3000/engine.py`:
1. Define `UNIT_COSTS: Dict[str, int] = {"Trike": 150, "CombatTank": 300, "Harvester": 400}` at module level in `/botworkspace/dune3000/dune3000/engine.py`.
2. Add method `train_unit(self, house: str, unit_type: str, x: int, y: int) -> Optional[Unit]` on `GameState`:
   - Look up `cost = UNIT_COSTS.get(unit_type, 200)`.
   - If `self.credits.get(house, 0) < cost`, return `None`.
   - Deduct `cost` from `self.credits[house]`.
   - Create `unit = Unit(unit_type=unit_type, house=house, x=x, y=y)`, append `unit` to `self.units`, and return `unit`.
3. Add a unit test `test_train_unit` in `/botworkspace/dune3000/tests/test_engine.py` testing both successful training (credit deduction and unit creation) and insufficient credits (`None`), and run `python3 -m unittest discover tests`.
