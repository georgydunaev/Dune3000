# Ticket 23: Implement Unit Experience & Veterancy Promotion (`Unit.gain_xp`)

**State:** open
**Labels:** dune3000, combat, gameplay

## Context
Combat units that survive battles in Dune 3000 earn experience (`xp`) and promote to Veteran (`xp >= 100`) and Elite (`xp >= 250`), boosting their `attack_damage`.

## Acceptance Criteria
1. Add integer attributes `xp: int = 0` and `rank: int = 0` (with defaults) to `Unit` in `dune3000/engine.py`.
2. Add method `gain_xp(self, amount: int) -> int` on `Unit`:
   - Increases `self.xp` by `max(0, amount)`.
   - When `self.xp >= 100` and `self.rank < 1`, promotes `self.rank = 1` and increases `self.attack_damage` by `5`.
   - When `self.xp >= 250` and `self.rank < 2`, promotes `self.rank = 2` and increases `self.attack_damage` by an additional `5` (total `+10` over base if jumping from rank 0 to rank 2).
   - Returns `self.rank`.
3. Add unit test `test_unit_veterancy_promotion` inside `TestDune3000Engine` in `tests/test_engine.py`.
4. Run `python3 -m unittest discover tests` and ensure all tests pass.
