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


if __name__ == "__main__":
    unittest.main()
