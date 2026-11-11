# Ticket 30: Implement Infantry Engineer Building Capture (`GameState.capture_building`)
**State:** open
**Labels:** dune3000

## Context
In Dune 2000, an Engineer infantry unit can enter an adjacent enemy structure to capture it immediately for the Engineer's House, consuming the Engineer in the process.

## Acceptance Criteria
1. Add `"Engineer": 200` to `UNIT_COSTS` in `/botworkspace/dune3000/dune3000/engine.py` (preserving existing keys).
2. Add a method `capture_building(self, unit: Unit, building: Building) -> bool` to `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
   - Return `False` if `unit.unit_type != "Engineer"`, `unit.hp <= 0`, `building.hp <= 0`, `unit.house == building.house`, or `abs(unit.x - building.x) + abs(unit.y - building.y) > 1`.
   - Change ownership: `building.house = unit.house`.
   - Restore up to 100 HP: `building.hp = min(building.max_hp, building.hp + 100)`.
   - Consume the Engineer: set `unit.hp = 0` and remove `unit` from `self.units` (if present).
   - Return `True`.
3. Add a unit test `test_capture_building` in `/botworkspace/dune3000/tests/test_engine.py` verifying:
   - An adjacent `Engineer` captures an enemy building, switches `building.house`, consumes the engineer, and returns `True`.
   - Non-engineer units or out-of-range engineers return `False` and do not capture.
4. Run `cd /botworkspace/dune3000 && python3 -m unittest discover -v tests` and ensure all tests pass.
