# Ticket 5: Implement Rock-Paper-Scissors Weapon vs Armor Damage Calculation

- **State:** open
- **Labels:** feature, combat

## Description
In `dune3000/engine.py`, add a function `compute_damage(weapon_type: str, armor_type: str, base_damage: int) -> int`:
1. Apply multipliers:
   - `weapon_type == "bullet"` and `armor_type == "infantry"`: `1.5`
   - `weapon_type == "bullet"` and `armor_type == "heavy"`: `0.25`
   - `weapon_type == "shell"` and `armor_type == "heavy"`: `1.25`
   - `weapon_type == "missile"` and `armor_type == "building"`: `1.5`
   - All other combinations: `1.0`
2. Return `max(1, int(round(base_damage * multiplier)))`.
3. Add unit tests in `tests/test_engine.py` and run `python3 -m unittest discover tests`.
