# Ticket 039: Sandworm Evasion, Seismic Tremor Reaction, and Harvester Escort

**State:** closed
**Labels:** dune3000, ai, sandworm, economy

## Context
Sandworms are the primary environmental hazard on Arrakis. Naive AI units ignore worm signs until swallowed whole. Smart units should detect worm tremors, scatter towards bedrock or safe zones when Shai-Hulud approaches, and assign combat escorts to safeguard harvesters during harvesting runs.

## Acceptance Criteria
1. Add worm danger detection in `dune3000/engine.py`:
   - Units detect active sandworms within danger radius (default 5 tiles on sand/dunes).
   - Units on sand step away from the worm or towards the closest non-sand tile (`ROCK` or `CONCRETE`).
   - Escort allocation: Combat units in defensive stance position themselves within support range of harvesting units to repel enemy raiders.
2. Mirror worm evasion and harvester screening mechanics in `index.html`.
3. Unit test coverage in `tests/test_engine.py` for worm detection, scatter direction, and harvester defense coordination.
