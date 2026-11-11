# Ticket 22: Implement AI Skirmish Commander Step (`GameState.step_ai_commander`)

**State:** open
**Labels:** dune3000, ai, gameplay

## Context
To make single-player skirmish mode exciting, the AI house needs an autonomous commander method that spends excess credits to reinforce its army and directs combat units toward enemy targets.

## Acceptance Criteria
1. Add method `step_ai_commander(self, house: str) -> str` on `GameState` in `dune3000/engine.py`:
   - If `self.credits.get(house, 0) >= 200` and `house` owns at least one alive building:
     - Deduct `200` credits, spawn a `Unit("CombatTank", house, b.x, b.y, hp=120, max_hp=120, weapon_type="shell", armor_type="heavy", attack_damage=25, attack_range=3)` at the first alive building `b` of `house`, append to `self.units`, and return `"spawned_tank"`.
   - Otherwise, find all alive combat units (`unit_type != "Harvester"`) owned by `house` and move each one 1 step (`move_towards`) toward the nearest alive enemy unit or building, returning `"advanced_units"` if at least one unit moved, or `"idle"` otherwise.
2. Add unit test `test_step_ai_commander` inside `TestDune3000Engine` in `tests/test_engine.py`.
3. Run `python3 -m unittest discover tests` and ensure all tests pass.
