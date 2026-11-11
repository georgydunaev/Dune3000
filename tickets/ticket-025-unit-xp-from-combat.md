# Ticket 025: Unit XP from Combat Experience

**State:** closed
**Labels:** dune3000, gameplay, mechanics

## Acceptance Criteria

Add XP gain to the `Unit.attack()` method in `dune3000/engine.py` so that when a unit successfully damages an enemy, the attacker gains experience points equal to the damage dealt. This connects the existing `Unit.gain_xp()` method to combat gameplay and enables the rank promotion system defined in Ticket 023.

**Changes to `dune3000/engine.py`:**
- Modify `Unit.attack(target: Unit) -> int` to call `self.gain_xp(dmg)` after successfully damaging a target.
- The XP granted should equal the damage dealt (`dmg`), rewarding aggressive play and enabling rank progression.

**Changes to `tests/test_engine.py`:**
- Add a new test method `test_unit_xp_from_attack` within the `TestDune3000Engine` class that verifies:
  - When a unit damages an enemy target, its `xp` increases by the amount of damage dealt.
  - When a unit damages an enemy target, the target's `hp` decreases and the attacker's `xp` increases accordingly.
  - XP gain is 0 when the attack misses (target out of range or attacker/target dead).
  - XP gain works correctly with the existing rank promotion thresholds (rank 1 at xp >= 100, rank 2 at xp >= 250).

**Example test logic:**
```python
def test_unit_xp_from_attack(self):
    gs = GameState(GridMap(8, 8))
    attacker = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
    target = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
    gs.units.append(attacker)
    gs.units.append(target)
    # Attack with bullet vs heavy: 20 * 0.25 = 5 damage
    dmg = attacker.attack(target)
    self.assertEqual(dmg, 5)
    self.assertEqual(target.hp, 45)
    # Attacker should gain 5 XP
    self.assertEqual(attacker.xp, 5)
```