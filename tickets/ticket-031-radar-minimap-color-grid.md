# Ticket 31: Implement Radar Outpost Minimap SVG Generator (`generate_minimap_svg` in `procgen.py`)
**State:** open
**Labels:** dune3000, graphics

## Context
In Dune 2000, an active Outpost radar displays a tactical overhead minimap showing terrain tiles, house-colored units/buildings, and sandworm signatures.

## Acceptance Criteria
1. Add a function `generate_minimap_svg(state_dict: dict, pixel_size: int = 4) -> str` in `/botworkspace/dune3000/dune3000/procgen.py`:
   - Reads `width = state_dict.get("width", 16)`, `height = state_dict.get("height", 16)`, `tiles = state_dict.get("tiles", [])`.
   - Total SVG dimensions: `w_px = width * pixel_size`, `h_px = height * pixel_size`.
   - Renders a `<rect>` of size `pixel_size` for each terrain cell `(x, y)` using `TERRAIN_COLORS.get(tile, "#e5c07b")`.
   - Renders a `<rect>` at `(b["x"] * pixel_size, b["y"] * pixel_size)` for each building in `state_dict.get("buildings", [])` using `HOUSE_COLORS.get(b["house"], "#2563eb")`.
   - Renders a `<circle>` at center `(u["x"] * pixel_size + pixel_size // 2, u["y"] * pixel_size + pixel_size // 2)` for each unit in `state_dict.get("units", [])` using `HOUSE_COLORS.get(u["house"], "#2563eb")`.
   - Renders a `<circle>` with fill `"#b45309"` for each sandworm in `state_dict.get("sandworms", [])`.
   - Returns the complete `<svg xmlns="http://www.w3.org/2000/svg" width="{w_px}" height="{h_px}" ...>...</svg>` string.
2. Add a unit test `test_generate_minimap_svg` in `/botworkspace/dune3000/tests/test_engine.py` verifying that `generate_minimap_svg(gs.to_dict(), pixel_size=4)` returns a valid `<svg` string containing the terrain, house, and sandworm colors.
3. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
