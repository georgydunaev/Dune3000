import unittest
from dune3000.engine import (
    CONCRETE,
    ROCK,
    SAND,
    SPICE_THICK,
    SPICE_THIN,
    Building,
    GameState,
    GridMap,
    Sandworm,
    Unit,
)
from dune3000.procgen import generate_terrain_svg


class TestDune3000Engine(unittest.TestCase):
    def test_harvester_cycle(self):
        gs = GameState(GridMap(8, 8))
        gs.game_map.set_tile(2, 2, SPICE_THICK)
        ref = Building("Refinery", "Atreides", 1, 1, power_consumed=30)
        gs.buildings.append(ref)
        harv = Unit("Harvester", "Atreides", 2, 2)
        gs.units.append(harv)

        harv.step_harvest(gs.game_map, ref, gs)
        self.assertEqual(harv.spice_carried, 100)
        self.assertEqual(gs.game_map.get_tile(2, 2), SPICE_THIN)

        harv.x, harv.y = 1, 1
        deposited = harv.step_harvest(gs.game_map, ref, gs)
        self.assertEqual(deposited, 100)
        self.assertEqual(gs.credits["Atreides"], 1100)

    def test_sandworm_ignores_rock_units(self):
        gm = GridMap(8, 8)
        gm.set_tile(1, 1, ROCK)
        gm.set_tile(5, 5, SAND)
        u_safe = Unit("LightInfantry", "Atreides", 1, 1)
        u_sand = Unit("Trike", "Harkonnen", 5, 5)
        worm = Sandworm(0, 0)
        target = worm.find_nearest_target([u_safe, u_sand], gm)
        self.assertIs(target, u_sand)

    def test_procedural_terrain_svg(self):
        svg = generate_terrain_svg(SPICE_THICK, size=32, seed=3)
        self.assertIn("<svg", svg)
        self.assertIn("#be5046", svg)

    def test_place_building_on_concrete(self):
        """CONCRETE tile keeps building at full HP."""
        gs = GameState(GridMap(8, 8, default_tile=CONCRETE))
        b = Building("Barracks", "Atreides", 2, 2)
        result = gs.place_building(b)
        self.assertEqual(result.hp, result.max_hp)
        self.assertIn(result, gs.buildings)

    def test_place_building_on_rock(self):
        """ROCK tile applies 50% foundation penalty (minimum HP 1)."""
        gs = GameState(GridMap(8, 8, default_tile=ROCK))
        b = Building("Barracks", "Atreides", 2, 2)
        result = gs.place_building(b)
        expected_hp = max(1, b.max_hp // 2)
        self.assertEqual(result.hp, expected_hp)
        self.assertIn(result, gs.buildings)

    def test_place_building_on_sand_default(self):
        """SAND tile (default) places building without penalty (HP stays at max_hp since no penalty)."""
        gs = GameState(GridMap(8, 8, default_tile=SAND))
        b = Building("Barracks", "Atreides", 2, 2)
        result = gs.place_building(b)
        # On SAND, no penalty is applied, so HP stays at max_hp (400)
        self.assertEqual(result.hp, result.max_hp)
        self.assertIn(result, gs.buildings)

    def test_place_building_return_value(self):
        """place_building returns the building it received."""
        gs = GameState(GridMap(8, 8))
        b = Building("Factory", "Harkonnen", 3, 3)
        result = gs.place_building(b)
        self.assertIs(result, b)

    def test_place_building_appended_to_buildings(self):
        """place_building appends the building to self.buildings."""
        gs = GameState(GridMap(8, 8))
        b1 = Building("Barracks", "Atreides", 1, 1)
        b2 = Building("Factory", "Harkonnen", 2, 2)
        gs.place_building(b1)
        gs.place_building(b2)
        self.assertEqual(len(gs.buildings), 2)
        self.assertIn(b1, gs.buildings)
        self.assertIn(b2, gs.buildings)

    def test_power_efficiency(self):
        """power_efficiency: 1.0 at normal power, 0.5 at deficit, 0.25 minimum clamp."""
        gs = GameState(GridMap(8, 8))
        # Normal power: no consumption -> full efficiency.
        self.assertEqual(gs.power_efficiency("Atreides"), 1.0)

        # Low power: produced half of consumed -> ratio 0.5.
        windtrap = Building("Windtrap", "Atreides", 1, 1, power_produced=50)
        gs.buildings.append(windtrap)
        refinery = Building("Refinery", "Atreides", 2, 2, power_consumed=100)
        gs.buildings.append(refinery)
        self.assertEqual(gs.power_efficiency("Atreides"), 0.5)

        # Minimum clamp: ratio below 0.25 is clamped up to 0.25.
        gs.buildings.append(Building("Factory", "Atreides", 3, 3, power_consumed=300))
        self.assertEqual(gs.power_efficiency("Atreides"), 0.25)

        # Rounding: 100/300 -> 0.3333 (4 decimal places).
        small = GameState(GridMap(8, 8))
        small.buildings.append(Building("Windtrap", "Harkonnen", 1, 1, power_produced=100))
        small.buildings.append(Building("Refinery", "Harkonnen", 2, 2, power_consumed=300))
        self.assertEqual(small.power_efficiency("Harkonnen"), 0.3333)


if __name__ == "__main__":
    unittest.main()
