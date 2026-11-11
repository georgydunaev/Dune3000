# Ticket 33: Implement Saboteur Stealth Demolition Unit

**State:** open
**Labels:** dune3000, gameplay, combat

## Context
In classic Dune 2000, the Saboteur is a stealthy demolition infantry used to instantly destroy enemy buildings. Adding it gives the engine a stealth/immolation mechanic that complements turrets (Ticket 28) and building capture (Ticket 30).

The Saboteur is a fragile, fast infantry that:
- Moves 2 tiles per `move_towards` step instead of 1 (fast).
- Is ignored by enemy Sandworms (expert dune walker) — `Sandworm.find_nearest_target` must skip it.
- Cannot attack normally (`attack` returns 0).
- Instead of attacking, it detonates: when adjacent (Manhattan distance <= 1) to an enemy building, it destroys that building instantly (hp = 0) and dies (hp = 0) in the blast.

## Acceptance Criteria
1. Add `"Saboteur": 250` to `UNIT_COSTS` in `dune3000/engine.py` and default unit spec `hp=45, max_hp=45, weapon_type="none", armor_type="infantry", attack_damage=0, attack_range=0`.
2. Add `Unit.move_steps` attribute defaulting to `1`; make `Unit.move_towards` move `self.move_steps` tiles along X (then Y if X did not change), still clamping to map bounds and returning the final `(x, y)` tuple. Saboteur instances set `move_steps=2`.
3. Make `Sandworm.find_nearest_target` skip units with `unit_type == "Saboteur"` (and the existing `hp <= 0` and safe-tile skips).
4. Add method `GameState.sabotage(self, saboteur: Unit, building: Building) -> bool`:
   - Returns `False` without side effects if either the saboteur or building is dead (`hp <= 0`), the saboteur and building belong to the same house, or the Manhattan distance is greater than 1.
   - Otherwise sets `building.hp = 0` and `saboteur.hp = 0`, returns `True`.
5. Add unit test `test_saboteur` inside `TestDune3000Engine` in `tests/test_engine.py` covering: fast 2-tile movement with bounds clamping, Sandworm ignoring the Saboteur, sabotage destroying the building and the saboteur, same-house sabotage rejection, out-of-range rejection, and dead-target rejection.
6. Run `python3 -m unittest discover tests` and ensure all tests pass.

## Test Requirements
- `python3 -m unittest discover tests` green.
- Existing `test_unit_move_towards` behavior for default `move_steps=1` units must remain unchanged (1-tile steps).
