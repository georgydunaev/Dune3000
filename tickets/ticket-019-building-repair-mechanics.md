# Ticket 19: Implement Building Repair Mechanics (`GameState.repair_building`)

**State:** closed
**Labels:** dune3000, gameplay, economy

## Context
Damaged structures in Dune 3000 can be repaired by spending Spice credits (1 credit per 2 HP restored).

## Acceptance Criteria
1. Add method `repair_building(self, building: Building, max_hp_to_restore: int = 50) -> int` on `GameState` in `dune3000/engine.py`:
   - If `building.hp <= 0` or `building.hp >= building.max_hp` or `max_hp_to_restore <= 0`, return `0`.
   - Calculate `missing = min(building.max_hp - building.hp, max_hp_to_restore)`.
   - Each 1 credit restores up to 2 HP (`cost = (missing + 1) // 2`).
   - If the building's `house` has fewer credits than `cost`, only restore `available_credits * 2` HP and spend `available_credits`.
   - Deduct the credits from `self.credits[building.house]`, increase `building.hp` (clamped to `building.max_hp`), and return the actual HP restored (`int`).
2. Add unit test `test_repair_building` inside `TestDune3000Engine` in `tests/test_engine.py` verifying normal repair, credit deduction, clamping at `max_hp`, and dead building (`hp == 0`) rejection.
3. Run `python3 -m unittest discover tests` and ensure all tests pass.
