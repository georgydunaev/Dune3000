# Ticket 13: Implement Victory and Defeat Condition Check (`GameState.check_winner`)

**State:** open
**Priority:** high

## Description
Add a `check_winner(self) -> Optional[str]` method on `GameState` in `/botworkspace/dune3000/dune3000/engine.py`:
1. Compute `active_houses`, the set of houses that own at least one alive building (`b.hp > 0` in `self.buildings`) or at least one alive unit (`u.hp > 0` in `self.units`).
2. If `len(active_houses) == 1`, return the single remaining house name (e.g. `"Atreides"`).
3. If `len(active_houses) == 0`, return `"Draw"`.
4. Otherwise (`len(active_houses) >= 2`), return `None`.
5. Add a unit test `test_check_winner` in `/botworkspace/dune3000/tests/test_engine.py` testing ongoing battle (`None`), single winner (`"Atreides"`), and draw (`"Draw"`), and run `python3 -m unittest discover tests`.
