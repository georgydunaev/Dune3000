# Ticket 11: Implement Building Construction with Credit Cost (`GameState.construct_building`)

**State:** closed
**Priority:** high

## Description
Add credit-based building construction to `/botworkspace/dune3000/dune3000/engine.py`:
1. Define `BUILDING_COSTS: Dict[str, int] = {"WindTrap": 200, "Refinery": 400, "Barracks": 250, "Silo": 150}` at module level in `/botworkspace/dune3000/dune3000/engine.py`.
2. Add method `construct_building(self, house: str, building_type: str, x: int, y: int) -> Optional[Building]` on `GameState`:
   - Look up `cost = BUILDING_COSTS.get(building_type, 250)`.
   - If `self.credits.get(house, 0) < cost`, return `None`.
   - Deduct `cost` from `self.credits[house]`.
   - Set `power_produced = 100 if building_type == "WindTrap" else 0` and `power_consumed = 0 if building_type == "WindTrap" else 30`.
   - Create `b = Building(building_type=building_type, house=house, x=x, y=y, power_produced=power_produced, power_consumed=power_consumed)`, call `self.place_building(b)`, and return `b`.
3. Add a unit test `test_construct_building` in `/botworkspace/dune3000/tests/test_engine.py` and run `python3 -m unittest discover tests`.
