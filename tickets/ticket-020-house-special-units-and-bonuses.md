# Ticket 20: Implement House Special Units (`SonicTank`, `Devastator`, `Deviator`)

**State:** open
**Labels:** dune3000, gameplay, combat

## Context
Each Great House on Arrakis fields a signature special vehicle:
- `"Atreides"`: `"SonicTank"` (`hp=130, max_hp=130, attack_damage=45, attack_range=4, weapon_type="shell", armor_type="heavy"`)
- `"Harkonnen"`: `"Devastator"` (`hp=220, max_hp=220, attack_damage=55, attack_range=3, weapon_type="shell", armor_type="heavy"`)
- `"Ordos"`: `"Deviator"` (`hp=110, max_hp=110, attack_damage=35, attack_range=4, weapon_type="missile", armor_type="heavy"`)

## Acceptance Criteria
1. Add dictionary `HOUSE_SPECIAL_UNITS` in `dune3000/engine.py` mapping each house (`"Atreides"`, `"Harkonnen"`, `"Ordos"`) to its special unit specification.
2. Add method `spawn_special_unit(self, house: str, x: int, y: int) -> Optional[Unit]` on `GameState` in `dune3000/engine.py`:
   - Costs `300` credits. If `self.credits.get(house, 0) < 300` or `house not in HOUSE_SPECIAL_UNITS`, return `None`.
   - Otherwise deduct `300` credits, create the house's special `Unit` at `(x, y)` with its configured stats, append it to `self.units`, and return it.
3. Add unit test `test_spawn_special_unit` inside `TestDune3000Engine` in `tests/test_engine.py` testing all three houses and insufficient credits.
4. Run `python3 -m unittest discover tests` and ensure all tests pass.
