# Ticket 3: Implement Algorithmic Unit Sprite SVG Generator in `procgen.py`

- **State:** open
- **Labels:** feature, graphics

## Description
In `dune3000/procgen.py`, add a function `generate_unit_svg(unit_type: str, house: str, size: int = 32) -> str`:
1. Look up the house color from `HOUSE_COLORS.get(house, "#2563eb")`.
2. Return a valid `<svg ...>...</svg>` string of width/height `size` containing the house color and a geometric shape distinguishing `"Harvester"`, `"Trike"`, and `"CombatTank"`.
3. Add a unit test `test_generate_unit_svg` in `tests/test_engine.py` and run `python3 -m unittest discover tests`.
