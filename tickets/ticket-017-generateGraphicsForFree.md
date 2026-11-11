# Ticket 17: Generate for Free Better Multi-Layer Procedural Graphics & Sprites (`procgen.py`)

**State:** closed
**Labels:** user, dune3000, graphics

## User Request
Generate for free somehow better graphics for the game.

## Context & Requirements
Upgrade `/botworkspace/dune3000/dune3000/procgen.py` so that all game graphics are generated completely for free using rich, multi-layered deterministic SVG geometry (shadows, metallic chassis, treads/wheels, gun turrets, windtrap turbines, refinery silos, spice crystal shimmer, and explosion effects) without any paid APIs or external binary assets:

1. **Add `generate_explosion_svg(size: int = 32, frame: int = 0) -> str` in `dune3000/procgen.py`**:
   - Generates a valid `<svg ...>...</svg>` string of width/height `size` depicting a multi-layer combat explosion/fireball (`#ff4500`, `#f59e0b`, `#fef08a`) whose inner/outer blast radii vary deterministically with `frame`.
2. **Enhance `generate_unit_svg(unit_type: str, house: str, size: int = 32) -> str`**:
   - Keep existing return contract (`<svg`, house color hex from `HOUSE_COLORS`, `<polygon` for `Harvester` and `Trike`, `<rect` for `CombatTank`), AND add detailed multi-layer SVG sub-elements (dark armored treads/wheels, turret/cannon barrel, cockpit canopy, or spice collector scoop) so units look like authentic RTS vehicles.
   - Support additional unit types (`"LightInfantry"`, `"RocketInfantry"`, `"SonicTank"`, `"Devastator"`, `"Deviator"`) with distinct SVG silhouettes and faction colors.
3. **Enhance `generate_building_svg(building_type: str, house: str, size: int = 32) -> str`**:
   - Keep existing return contract (`<svg`, house color hex from `HOUSE_COLORS`, `<polygon` for `WindTrap`, `<rect` for `Refinery`, `ConstructionYard`, `Silo`), AND add rich architectural details (foundation shadow border, windtrap turbine vents, refinery spice unloading pad, construction crane bays, and storage domes).
4. **Unit Test**:
   - Add `test_free_enhanced_graphics_svg` to `TestDune3000Engine` in `tests/test_engine.py` verifying `generate_explosion_svg` across frames and multi-element SVG output for units and buildings.
   - Run `python3 -m unittest discover tests` and ensure all tests pass.
