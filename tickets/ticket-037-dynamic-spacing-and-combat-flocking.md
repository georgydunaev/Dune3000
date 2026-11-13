# Ticket 037: Dynamic Spacing, Flocking, and Combat Formations

**State:** closed
**Labels:** dune3000, ai, movement, formation

## Context
When multiple AI units receive attack orders, naive algorithms cause them to stack into a single cell or march in single-file columns that are easily decimated by area-of-effect weapons (Sonic Tanks, Siege Tanks, Death Hand). Units need combat spacing, standoff firing stances, and multi-vector flanking formations.

## Acceptance Criteria
1. Add formation offset calculation in `dune3000/engine.py`:
   - Compute standoff firing distance based on `attack_range` rather than collapsing into distance zero.
   - Disperse units in arc or flanking ring around target coordinate to avoid stacking.
2. In `move_towards` and AI advance steps, support collision repulsion and standoff positioning so units maintain tactical breathing room.
3. Enhance canvas rendering and flocking physics in `index.html` to maintain unit personal space and flanking arcs during battle maneuvers.
4. Add unit test coverage in `tests/test_engine.py` for formation spacing calculations.
