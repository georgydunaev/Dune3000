# Ticket 14: Implement Algorithmic Sandworm SVG Sprite Generator in `procgen.py`

**State:** open
**Priority:** medium

## Description
Add a function `generate_sandworm_svg(size: int = 32) -> str` in `/botworkspace/dune3000/dune3000/procgen.py`:
1. Return a valid `<svg ...>...</svg>` string with `width="{size}"` and `height="{size}"`.
2. Render at least two concentric `<circle` elements centered at `(size // 2, size // 2)` representing an Arrakis sandworm mouth and inner teeth ring.
3. Add a unit test `test_generate_sandworm_svg` in `/botworkspace/dune3000/tests/test_engine.py` verifying that `generate_sandworm_svg(32)` starts with `<svg`, ends with `</svg>`, and contains `<circle`, and run `python3 -m unittest discover tests`.
