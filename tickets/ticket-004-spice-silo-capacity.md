# Ticket 4: Implement Spice Silo Capacity and Credit Storage Cap in `GameState`

- **State:** open
- **Labels:** feature, engine

## Description
In `/botworkspace/dune3000/dune3000/engine.py`, add a method `max_spice_capacity(self, house: str) -> int` on `GameState`:
1. Base capacity for any house is `1000`.
2. Each alive (`hp > 0`) `"Refinery"` owned by `house` adds `1000`, and each alive `"Silo"` owned by `house` adds `1000`.
3. Add a unit test `test_max_spice_capacity` in `/botworkspace/dune3000/tests/test_engine.py` and verify with `python3 -m unittest discover tests`.
