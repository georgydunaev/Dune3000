# Ticket 040: Dynamic Coriolis Weather Fronts and Sietch Infiltration Mechanics

**State:** closed
**Status:** RESOLVED
**Labels:** dune3000, gameplay, weather, fremen, tactics

## Context
Arrakis experiences severe Coriolis weather fronts that sweep across desert sectors, threatening exposed harvesting and military operations. Additionally, Fremen Sietches embedded in cliff rocks provide strategic desert hubs for shelter, guerrilla recruitment, and tactical infiltration.

## Acceptance Criteria
1. Implement `WeatherFront` and dynamic storm front trajectory processing in `dune3000/dune3000/engine.py`:
   - `WeatherFront` tracks position `(x, y)`, velocity vector `(vx, vy)`, `radius`, `intensity`, `duration`, and `active` state.
   - `GameState.spawn_weather_front(x, y, vx, vy, radius, intensity, duration)` registers and returns an active weather front.
   - `GameState.step_weather_fronts()` advances active weather fronts along their velocity vector, decrements duration, and applies sandstorm damage.
   - Units located on `ROCK` or `CONCRETE`, or sheltered within distance `<= 1` of an active `FremenSietch`, are sheltered and take zero storm damage.
   - Exposed units within Manhattan distance `<= radius` of the front take `intensity` damage.
2. Implement Sietch tactical infiltration in `dune3000/dune3000/engine.py`:
   - `GameState.infiltrate_sietch(unit: Unit, sietch: Building) -> Optional[Dict[str, Any]]`.
   - Validates that `unit.hp > 0`, `sietch.hp > 0`, `sietch.building_type == "FremenSietch"`, and Manhattan distance between unit and sietch `<= 1`. Returns `None` on invalid requests.
   - Allied Garrison (`unit.house == sietch.house`):
     - Restores up to 25 HP to the unit (clamped to `max_hp`).
     - Returns status dict indicating sheltered action and HP healed.
   - Hostile Infiltration (`unit.house != sietch.house`):
     - Extracts spice cache (transfers up to 250 credits to the infiltrating unit's house).
     - Liberates and recruits an allied `FremenWarrior` at the Sietch location added to `game_state.units`.
     - Infiltrator survival: Covert units (`Saboteur`, `FremenWarrior`) survive and gain 50 XP (triggering rank promotion if threshold reached); other units are consumed.
     - Returns status dict with extracted credits, recruited unit, and survival status.

## Unit Test Requirements
In `dune3000/tests/test_engine.py`:
- Add `test_dynamic_weather_front_trajectory_and_shelter`:
  - Verify front advances position by velocity each step and decrements duration until deactivation.
  - Verify exposed units on sand within radius take storm damage.
  - Verify units on rock or within distance `<= 1` of a Fremen Sietch remain sheltered and unharmed.
- Add `test_sietch_tactical_infiltration`:
  - Verify allied unit infiltration restores health up to 25 HP.
  - Verify enemy infiltration drains credits, spawns an allied FremenWarrior, and checks covert unit survival vs standard unit consumption.
  - Verify out of range or destroyed Sietch returns `None`.

## Resolution
Implemented `WeatherFront`, `GameState.spawn_weather_front`, `GameState.step_weather_fronts`, and `GameState.infiltrate_sietch` in `dune3000/dune3000/engine.py`. Added comprehensive unit tests in `dune3000/tests/test_engine.py` covering trajectory advancement, bedrock and Sietch shelter, allied garrison repair, hostile spice extraction, Fremen guerilla recruitment, and stealth specialist survival.
