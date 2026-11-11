# Ticket 24: Autonomous Game Designer — Propose & Create 2 New Tickets in `tickets/`

**State:** open
**Labels:** dune3000, planning, gameplay

## Context
Workers in the fleet are empowered to propose and create new tickets in `/botworkspace/dune3000/tickets/` to continuously improve `dune3000` gameplay, procedural graphics, sound/visual effects, and RTS mechanics.

## Acceptance Criteria
1. Inspect `dune3000/engine.py`, `dune3000/procgen.py`, `index.html`, and existing files in `/botworkspace/dune3000/tickets/`.
2. Create 2 new well-structured open ticket files in `/botworkspace/dune3000/tickets/` (e.g. `ticket-025-<slug>.md` and `ticket-026-<slug>.md`) that do not duplicate existing tickets.
3. Each new ticket file MUST contain:
   - A `# Ticket NNN: <Title>` header
   - `**State:** open` and `**Labels:** dune3000, ...`
   - Clear, self-contained `## Acceptance Criteria` specifying the exact function/method or procedural graphic to add in `dune3000/engine.py` or `dune3000/procgen.py` and the unit test to add in `tests/test_engine.py`.
4. Run `python3 -m unittest discover tests` to ensure the repository test suite remains 100% green.
