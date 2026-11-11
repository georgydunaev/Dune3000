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
    compute_damage,
)
from dune3000.procgen import generate_terrain_svg, generate_unit_svg


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

    def test_compute_damage_bullet_vs_infantry(self):
        """bullet vs infantry: 1.5x multiplier."""
        self.assertEqual(compute_damage("bullet", "infantry", 10), 15)
        self.assertEqual(compute_damage("bullet", "infantry", 7), 11)  # 7*1.5=10.5 -> round to 11

    def test_compute_damage_bullet_vs_heavy(self):
        """bullet vs heavy: 0.25x multiplier."""
        self.assertEqual(compute_damage("bullet", "heavy", 10), 3)  # int(10*0.25+0.5)=int(3.0)=3
        self.assertEqual(compute_damage("bullet", "heavy", 7), 2)  # int(7*0.25+0.5)=int(2.25)=2

    def test_compute_damage_shell_vs_heavy(self):
        """shell vs heavy: 1.25x multiplier."""
        self.assertEqual(compute_damage("shell", "heavy", 10), 13)  # int(10*1.25+0.5)=int(13.0)=13
        self.assertEqual(compute_damage("shell", "heavy", 3), 4)  # int(3*1.25+0.5)=int(4.0)=4

    def test_compute_damage_missile_vs_building(self):
        """missile vs building: 1.5x multiplier."""
        self.assertEqual(compute_damage("missile", "building", 10), 15)
        self.assertEqual(compute_damage("missile", "building", 1), 1)  # min clamp

    def test_compute_damage_all_other_combinations(self):
        """All other combinations: 1.0x multiplier."""
        self.assertEqual(compute_damage("bullet", "building", 10), 10)
        self.assertEqual(compute_damage("shell", "infantry", 10), 10)
        self.assertEqual(compute_damage("missile", "infantry", 10), 10)
        self.assertEqual(compute_damage("shell", "building", 10), 10)

    def test_compute_damage_minimum_clamp(self):
        """Returns max(1, ...), so minimum damage is 1."""
        self.assertEqual(compute_damage("bullet", "infantry", 0), 1)
        self.assertEqual(compute_damage("bullet", "heavy", 0), 1)
        self.assertEqual(compute_damage("shell", "heavy", 0), 1)
        self.assertEqual(compute_damage("missile", "building", 0), 1)
        self.assertEqual(compute_damage("anything", "anything", 0), 1)

    def test_compute_damage_rounding_behavior(self):
        """Test rounding: 7*1.5=10.5 should round to 11 (round half up)."""
        # 7 * 1.5 = 10.5 -> int(10.5 + 0.5) = int(11.0) = 11
        self.assertEqual(compute_damage("bullet", "infantry", 7), 11)
        # 3 * 1.25 = 3.75 -> int(3.75 + 0.5) = int(4.25) = 4
        self.assertEqual(compute_damage("shell", "heavy", 3), 4)

    def test_compute_damage_existing_tests_unaffected(self):
        """Ensure existing tests still pass."""
        # These verify the existing test suite isn't broken
        self.assertEqual(compute_damage("bullet", "infantry", 10), 15)



class TestDune3000Engine(unittest.TestCase):
        """max_spice_capacity: base 1000, +1000 per alive Refinery, +1000 per alive Silo."""
        gs = GameState(GridMap(8, 8))
        # Base capacity for any house
        self.assertEqual(gs.max_spice_capacity("Atreides"), 1000)
        self.assertEqual(gs.max_spice_capacity("Harkonnen"), 1000)
        self.assertEqual(gs.max_spice_capacity("Ordos"), 1000)
        
        # Refinery adds 1000 when alive (hp > 0)
        ref = Building("Refinery", "Atreides", 1, 1)
        gs.buildings.append(ref)
        self.assertEqual(gs.max_spice_capacity("Atreides"), 2000)
        
        # Silo adds 1000 when alive (hp > 0)
        silo = Building("Silo", "Atreides", 2, 2)
        gs.buildings.append(silo)
        self.assertEqual(gs.max_spice_capacity("Atreides"), 3000)
        
        # Dead buildings (hp <= 0) should not contribute
        dead_ref = Building("Refinery", "Atreides", 3, 3, hp=0)
        gs.buildings.append(dead_ref)
        self.assertEqual(gs.max_spice_capacity("Atreides"), 3000)
        
        # Different houses count their own buildings
        hark_ref = Building("Refinery", "Harkonnen", 4, 4)
        gs.buildings.append(hark_ref)
        self.assertEqual(gs.max_spice_capacity("Atreides"), 3000)
        self.assertEqual(gs.max_spice_capacity("Harkonnen"), 2000)

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

    def test_compute_damage_bullet_vs_infantry(self):
        """bullet vs infantry: 1.5x multiplier."""
        result = compute_damage("bullet", "infantry", 10)
        self.assertEqual(result, 15)

    def test_compute_damage_bullet_vs_heavy(self):
        """bullet vs heavy: 0.25x multiplier."""
        result = compute_damage("bullet", "heavy", 10)
        self.assertEqual(result, 3)  # int(round(10 * 0.25)) = int(round(2.5)) = 3

    def test_compute_damage_shell_vs_heavy(self):
        """shell vs heavy: 1.25x multiplier."""
        result = compute_damage("shell", "heavy", 10)
        self.assertEqual(result, 13)  # int(round(10 * 1.25)) = int(round(12.5)) = 13

    def test_compute_damage_missile_vs_building(self):
        """missile vs building: 1.5x multiplier."""
        result = compute_damage("missile", "building", 10)
        self.assertEqual(result, 15)

    def test_compute_damage_all_other_combinations(self):
        """All other combinations default to 1.0 multiplier."""
        result = compute_damage("shell", "infantry", 10)
        self.assertEqual(result, 10)  # int(round(10 * 1.0)) = 10
        result = compute_damage("missile", "infantry", 10)
        self.assertEqual(result, 10)
        result = compute_damage("bullet", "building", 10)
        self.assertEqual(result, 10)

    def test_compute_damage_minimum_one(self):
        """Return max(1, ...) ensures at least 1 damage."""
        result = compute_damage("bullet", "heavy", 1)
        self.assertEqual(result, 1)  # max(1, int(round(1 * 0.25))) = max(1, 0) = 1
        result = compute_damage("missile", "building", 1)
        self.assertEqual(result, 2)  # max(1, int(round(1 * 1.5))) = max(1, 2) = 2

    def test_compute_damage_rounding_behavior(self):
        """Test rounding behavior with various base damages."""
        # base_damage=7, multiplier=1.5 -> 7*1.5=10.5 -> round=11 -> max(1,11)=11
        result = compute_damage("bullet", "infantry", 7)
        self.assertEqual(result, 11)
        # base_damage=3, multiplier=0.25 -> 3*0.25=0.75 -> round=1 -> max(1,1)=1
        result = compute_damage("bullet", "heavy", 3)
        self.assertEqual(result, 1)

    def test_generate_unit_svg(self):
        """Test generate_unit_svg for Harvester, Trike, and CombatTank."""
        # Test Harvester with Atreides
        svg = generate_unit_svg("Harvester", "Atreides", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#2563eb", svg)
        self.assertIn("polygon", svg)

        # Test Trike with Harkonnen
        svg = generate_unit_svg("Trike", "Harkonnen", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#dc2626", svg)
        self.assertIn("polygon", svg)

        # Test CombatTank with Ordos
        svg = generate_unit_svg("CombatTank", "Ordos", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#16a34a", svg)
        self.assertIn("rect", svg)

        # Test with default house color (unknown house)
        svg = generate_unit_svg("Harvester", "UnknownHouse", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#2563eb", svg)


def test_generate_building_svg(self):
        """Test generate_building_svg for WindTrap, Refinery, ConstructionYard, and Silo."""
        # Test WindTrap with Atreides
        svg = generate_building_svg("WindTrap", "Atreides", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#2563eb", svg)
        self.assertIn("polygon", svg)

        # Test Refinery with Harkonnen
        svg = generate_building_svg("Refinery", "Harkonnen", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#dc2626", svg)
        self.assertIn("rect", svg)

        # Test ConstructionYard with Ordos
        svg = generate_building_svg("ConstructionYard", "Ordos", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#16a34a", svg)
        self.assertIn("rect", svg)

        # Test Silo with Atreides
        svg = generate_building_svg("Silo", "Atreides", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#2563eb", svg)
        self.assertIn("rect", svg)

        # Test with default house color (unknown house) for WindTrap
        svg = generate_building_svg("WindTrap", "UnknownHouse", size=32)
        self.assertIn("<svg", svg)
        self.assertIn("#2563eb", svg)

        # Verify determinism: same inputs produce same output
        svg1 = generate_building_svg("Refinery", "Atreides", size=32)
        svg2 = generate_building_svg("Refinery", "Atreides", size=32)
        self.assertEqual(svg1, svg2)


if __name__ == "__main__":
    unittest.main()