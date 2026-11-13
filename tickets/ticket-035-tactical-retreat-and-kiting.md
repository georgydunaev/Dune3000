# Ticket 035: Tactical Retreat and Unit Kiting Mechanics

**State:** closed
**Labels:** dune3000, ai, tactical, combat

## Context
Previously, units in both the Python engine and browser simulation would charge suicidally into enemy formations regardless of remaining hit points or tactical disadvantage. To provide human-like behavior, damaged and long-range units must evaluate threats, fall back to safe positions or repair bays, and maintain optimal firing distance (kiting).

## Acceptance Criteria
1. Add tactical retreat evaluation to `Unit`:
   - `should_retreat(self, threat_level: float = 1.0, health_ratio: float = 0.35) -> bool`: returns True if `hp / max_hp <= health_ratio`.
   - `compute_kiting_step(self, target, game_map) -> Tuple[int, int]`: if target is closer than optimal weapon range, calculates step away from target toward safety.
2. In `GameState.step_ai_commander`, evaluate retreat before advancing:
   - Critically damaged units seek retreat toward nearest friendly building or repair facility.
   - Kiting units with attack range >= 3 step away when enemies approach inside minimum range.
3. Mirror kiting and retreat behaviors in `index.html` game loop with clear visual feedback in combat logs and unit states.
4. Unit tests in `tests/test_engine.py` verifying retreat trigger conditions and kiting step calculations.
