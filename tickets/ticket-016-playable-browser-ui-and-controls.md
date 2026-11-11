# Ticket 16: Make Browser Game Playable in `index.html` with HUD, Controls, and Game Loop

**State:** open
**Priority:** high

## Description
Upgrade `/botworkspace/dune3000/index.html` into a playable interactive single-page RTS game in the browser using algorithmic canvas graphics:
1. Add a HUD bar (`id="hud"`) showing Player House (`Atreides`), Credits (`id="hud-credits"`), Power (`id="hud-power"`), Tick (`id="hud-tick"`), and Game Status (`id="hud-status"`).
2. Add interactive control buttons:
   - `id="btn-build-windtrap"` (Build WindTrap - 200)
   - `id="btn-build-refinery"` (Build Refinery - 400)
   - `id="btn-train-harvester"` (Train Harvester - 400)
   - `id="btn-train-tank"` (Train CombatTank - 300)
   - `id="btn-step-tick"` (Step Tick)
   - `id="btn-autoplay"` (Toggle Auto-Play)
3. Implement the client-side game loop and canvas click handler in `<script>` inside `/botworkspace/dune3000/index.html` so clicking tiles places buildings or moves selected units, harvesters gather spice and deposit credits, CombatTanks attack enemy Harkonnen units/buildings, and algorithmic sprites are drawn for terrain, buildings, units, and sandworms.
4. Add a unit test `test_playable_index_html_controls` in `/botworkspace/dune3000/tests/test_engine.py` verifying that `/botworkspace/dune3000/index.html` contains `id="hud"`, `id="btn-build-windtrap"`, `id="btn-train-harvester"`, `id="btn-step-tick"`, and `id="gameCanvas"`, and run `python3 -m unittest discover tests`.
