# Ticket 8: Implement Unit Combat Attack (`Unit.attack`)

**State:** closed
**Priority:** high

## Description
Extend `Unit` in `/botworkspace/dune3000/dune3000/engine.py` with combat attributes and an `attack` method:
1. Add default fields to `Unit`: `weapon_type: str = "bullet"`, `armor_type: str = "heavy"`, `attack_damage: int = 20`, `attack_range: int = 3`.
2. Add method `attack(self, target) -> int` on `Unit`:
   - If `self.hp <= 0` or `target.hp <= 0`, return `0`.
   - Compute Manhattan distance `dist = abs(self.x - target.x) + abs(self.y - target.y)`. If `dist > self.attack_range`, return `0`.
   - Determine `target_armor = getattr(target, "armor_type", "building")`.
   - Calculate `dmg = compute_damage(self.weapon_type, target_armor, self.attack_damage)`.
   - Update `target.hp = max(0, target.hp - dmg)` and return `dmg`.
3. Add a unit test `test_unit_attack` in `/botworkspace/dune3000/tests/test_engine.py` verifying in-range damage, out-of-range (`0`), and HP clamping at `0`, and run `python3 -m unittest discover tests`.
