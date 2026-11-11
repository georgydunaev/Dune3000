# Ticket 6: Implement Algorithmic Building Sprite SVG Generator in `procgen.py`

- **State:** open
- **Labels:** feature, graphics

## Description
In `dune3000/procgen.py`, add a function `generate_building_svg(building_type: str, house: str, size: int = 32) -> str`:
1. Use `HOUSE_COLORS.get(house, "#2563eb")` for the faction trim color.
2. Return a deterministic `<svg ...>...</svg>` string representing `"WindTrap"`, `"Refinery"`, `"ConstructionYard"`, or `"Silo"`.
3. Add a unit test `test_generate_building_svg` in `tests/test_engine.py` and verify with `python3 -m unittest discover tests`.
