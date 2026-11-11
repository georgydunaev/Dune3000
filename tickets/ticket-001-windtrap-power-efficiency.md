# Ticket 1: Implement WindTrap Power Efficiency Ratio in `GameState`

- **State:** open
- **Labels:** feature, engine

## Description
In `dune3000/engine.py`, add a method `power_efficiency(self, house: str) -> float` on `GameState`:
1. Compute `(produced, consumed) = self.power_balance(house)`.
2. If `consumed <= 0` or `produced >= consumed`, return `1.0`.
3. Otherwise return `max(0.25, round(produced / consumed, 4))`.
4. Add a unit test `test_power_efficiency` in `tests/test_engine.py` verifying normal power (`1.0`), low power (`0.5`), and minimum clamp (`0.25`), and run `python3 -m unittest discover tests`.
