# Ticket 036: Target Prioritization and Focus Fire Heuristics

**State:** closed
**Labels:** dune3000, ai, tactical, targeting

## Context
AI combat units historically locked onto whatever target happened to be closest in raw coordinate distance, often hitting low-threat structures while enemy siege artillery or economic harvesters operated unimpeded. Smart human players prioritize high-value targets, focus fire to eliminate wounded enemies quickly, and exploit armor-weapon matchups.

## Acceptance Criteria
1. Add `calculate_target_priority(self, target, distance: int) -> float` on `Unit`:
   - High-value target bonus: Harvester (+80), Siege Tank / Palace Artillery (+60), Missile Tank (+40).
   - Weakened target bonus: extra priority for low HP targets (focus fire to reduce incoming DPS: up to +50 points for near-death enemies).
   - Matchup effectiveness: multiplier bonus when attacker weapon deals elevated damage against target armor.
   - Distance penalty: reduces score proportionally to distance to balance proximity versus priority.
2. Integrate `select_priority_target(self, candidates, game_map)` into combat and AI commander decision loops in `dune3000/engine.py`.
3. Mirror prioritized target selection in `index.html` combat update loop.
4. Verify via unit tests in `tests/test_engine.py`.
