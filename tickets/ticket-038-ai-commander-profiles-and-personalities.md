# Ticket 038: AI Commander Profiles and Tactical Personalities

**State:** closed
**Labels:** dune3000, ai, commander, skirmish

## Context
A single monolithic AI behavior feels predictable and robotic. Real RTS gameplay features varied opponent doctrines: aggressive raiders who harass early, methodical mentats who assemble combined-arms siege forces, and economic turtlers who fortify behind defensive turrets and amass spice wealth.

## Acceptance Criteria
1. Define AI Commander Profiles in `dune3000/engine.py`:
   - `AggressiveRaider`: Favors fast strike units (Trikes, Quads), attacks early, lower retreat threshold (0.20), prioritizes economic targets.
   - `MethodicalMentat`: Balanced combined arms, respects weapon ranges, kites diligently, retreats at 0.35 health, prioritizes high-threat siege units.
   - `EconomicTurtler`: Invests in refineries and turrets, assigns escorts to harvesters, conservative retreat threshold (0.45).
2. Support profile parameter in `GameState.step_ai_commander(self, house: str, profile: str = "balanced")`.
3. Provide selectable commander personality controls in `index.html` Tactical menu and display active commander stance on the tactical HUD overlay.
4. Add comprehensive unit tests in `tests/test_engine.py` verifying each profile's production and tactical decisions.
