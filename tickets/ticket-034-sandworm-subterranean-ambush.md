# Ticket 034: Implement Sandworm Subterranean Ambush Mechanic (`GameState.step_sandworm_ambush`)

**State:** closed
**Status:** RESOLVED
**Labels:** dune3000, gameplay, sandworm

## Acceptance Criteria
Add a subterranean ambush behavior to Sandworms in `dune3000/dune3000/engine.py` via `GameState.step_sandworm_ambush(min_seismic_threshold: int = 3) -> Optional[Unit]`:
1. When a Sandworm is submerged (`w.submerged == True`), it tracks the total seismic vibrations in its local area (moving units and harvesting operations on sand/dunes).
2. If there are at least `min_seismic_threshold` active vibration events or units on sand within distance `<= 8` of the submerged sandworm, the sandworm surfaces immediately (`w.submerged = False`), repositions to the densest unit cluster on sand, and emits a seismic tremor (`w.tremor = True`).
3. The method returns the ambushed unit if adjacent upon surfacing, or `None`.
4. Ensure units on `ROCK` or `CONCRETE` emit zero vibrations and are completely exempt from ambush.

## Unit Test Requirements
In `dune3000/tests/test_engine.py`:
- Add test `test_sandworm_subterranean_ambush`:
  - When units on sand exceed `min_seismic_threshold`, submerged worm breaches and attacks.
  - When units are on `ROCK` or `CONCRETE`, zero vibrations are counted, worm remains submerged.
  - Verify `python3 -m unittest discover tests` passes cleanly.

## Resolution
Implemented subterranean ambush logic in `GameState.step_sandworm_ambush` with seismic vibration sensing on sand, densest cluster targeting, tremor emission, and immunity for units on rock or concrete bedrock. Verified with unit test `test_sandworm_subterranean_ambush`.
