# Ticket 21: Implement Spice Bloom Detonation (`GameState.detonate_spice_bloom`)

**State:** open
**Labels:** dune3000, gameplay, terrain

## Context
When a Spice Bloom erupts on Arrakis, it converts the center tile into `SPICE_THICK` and adjacent orthogonal `SAND`/`DUNES` tiles into `SPICE_THIN`.

## Acceptance Criteria
1. Add method `detonate_spice_bloom(self, x: int, y: int) -> int` on `GameState` in `dune3000/engine.py`:
   - If `(x, y)` is out of bounds on `self.game_map`, return `0`.
   - Set `(x, y)` to `SPICE_THICK` (unless it is `ROCK` or `CONCRETE`).
   - For each of the 4 orthogonal neighbors `(nx, ny)` in bounds, if its tile is `SAND` or `DUNES`, set it to `SPICE_THIN`.
   - Return the total count of tiles modified (`int`).
2. Add unit test `test_detonate_spice_bloom` inside `TestDune3000Engine` in `tests/test_engine.py` verifying center `SPICE_THICK`, orthogonal `SPICE_THIN`, and `ROCK`/`CONCRETE` preservation.
3. Run `python3 -m unittest discover tests` and ensure all tests pass.
