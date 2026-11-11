import unittest
from dune3000.engine import (
    BUILDING_COSTS,
    CONCRETE,
    DUNES,
    HOUSE_SPECIAL_UNITS,
    ROCK,
    SAND,
    SPICE_THICK,
    SPICE_THIN,
    SPECIAL_UNIT_COST,
    Building,
    GameState,
    GridMap,
    Sandworm,
    Unit,
    compute_damage,
)
from dune3000.procgen import (
    generate_building_svg,
    generate_explosion_svg,
    generate_minimap_svg,
    generate_sandworm_svg,
    generate_terrain_svg,
    generate_unit_svg,
)


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

    def test_sandworm_step_and_devour(self):
        """Test Sandworm.step: move towards target and devour when adjacent."""
        gm = GridMap(8, 8)
        # Sandworm at (0, 0), target Trike at (3, 3) on SAFE tile (should be ignored for nearest)
        # Actually find_nearest_target skips safe tiles, so let's place target on non-safe tile
        gm.set_tile(3, 3, SAND)  # SAND is not safe (not ROCK/CONCRETE)
        target = Unit("Trike", "Harkonnen", 3, 3)
        worm = Sandworm(0, 0)
        gs = GameState(gm)
        gs.units.append(target)

        # Step 1: move towards target (x < target.x => x += 1)
        result = worm.step(gs)
        self.assertIsNone(result)
        self.assertEqual(worm.x, 1)
        self.assertEqual(worm.y, 0)

        # Step 2: move closer (now at x=1, still x < 3)
        result = worm.step(gs)
        self.assertIsNone(result)
        self.assertEqual(worm.x, 2)
        self.assertEqual(worm.y, 0)

        # Step 3: move closer (now at x=2, still x < 3)
        result = worm.step(gs)
        self.assertIsNone(result)
        self.assertEqual(worm.x, 3)
        self.assertEqual(worm.y, 0)

        # Step 4: now at (3, 0), same x as target (3, 3), y < target.y => y += 1
        result = worm.step(gs)
        self.assertIsNone(result)
        self.assertEqual(worm.x, 3)
        self.assertEqual(worm.y, 1)

        # Step 5: y < target.y => y += 1
        result = worm.step(gs)
        self.assertIsNone(result)
        self.assertEqual(worm.x, 3)
        self.assertEqual(worm.y, 2)

        # Step 6: y < target.y => y += 1, now at (3, 3) == target position => devour!
        result = worm.step(gs)
        self.assertIsNotNone(result)
        self.assertEqual(result, target)
        self.assertEqual(target.hp, 0)
        self.assertNotIn(target, gs.units)

        # After devour, no more targets should exist
        result2 = worm.step(gs)
        self.assertIsNone(result2)

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

    def test_unit_move_towards(self):
        # Test moving towards a target with x > self.x (move right)
        gm = GridMap(8, 8)
        unit = Unit("TestUnit", "Atreides", 2, 2)
        unit.move_towards(5, 2, gm)
        self.assertEqual(unit.x, 3)
        self.assertEqual(unit.y, 2)

        # Test moving towards a target with x < self.x (move left)
        unit = Unit("TestUnit", "Atreides", 5, 2)
        unit.move_towards(2, 2, gm)
        self.assertEqual(unit.x, 4)
        self.assertEqual(unit.y, 2)

        # Test moving towards a target with same x, y > self.y (move down)
        unit = Unit("TestUnit", "Atreides", 3, 2)
        unit.move_towards(3, 5, gm)
        self.assertEqual(unit.x, 3)
        self.assertEqual(unit.y, 3)

        # Test moving towards a target with same x, y < self.y (move up)
        unit = Unit("TestUnit", "Atreides", 3, 5)
        unit.move_towards(3, 2, gm)
        self.assertEqual(unit.x, 3)
        self.assertEqual(unit.y, 4)

        # Test clamping at map bounds (can't go beyond width-1)
        unit = Unit("TestUnit", "Atreides", 7, 4)
        unit.move_towards(100, 4, gm)  # target far to the right
        self.assertEqual(unit.x, 7)  # clamped to width-1=7
        self.assertEqual(unit.y, 4)

        # Test clamping at map bounds (can't go below 0)
        unit = Unit("TestUnit", "Atreides", 0, 4)
        unit.move_towards(-100, 4, gm)  # target far to the left
        self.assertEqual(unit.x, 0)  # clamped to 0
        self.assertEqual(unit.y, 4)

        # Test moving diagonally: x changes first, then y
        unit = Unit("TestUnit", "Atreides", 2, 2)
        unit.move_towards(5, 5, gm)
        self.assertEqual(unit.x, 3)
        self.assertEqual(unit.y, 2)  # only x moved because x changed

        # Test target is same position (no movement)
        unit = Unit("TestUnit", "Atreides", 3, 3)
        unit.move_towards(3, 3, gm)
        self.assertEqual(unit.x, 3)
        self.assertEqual(unit.y, 3)

    def test_max_spice_capacity(self):
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

    def test_compute_visibility(self):
        """test_compute_visibility: sight radius reveal for alive units/buildings,
        and that dead (hp == 0) or enemy entities do not reveal tiles for house."""
        gs = GameState(GridMap(16, 16))

        # Place an alive Atreides building at (5, 5)
        b_atr = Building("WindTrap", "Atreides", 5, 5)
        gs.buildings.append(b_atr)

        # Place a dead Atreides building at (5, 5) with hp=0 (should NOT reveal)
        dead_b = Building("WindTrap", "Atreides", 5, 5, hp=0)
        gs.buildings.append(dead_b)

        # Place an alive Harkonnen unit (enemy, should NOT reveal for Atreides)
        u_hkn = Unit("Trike", "Harkonnen", 3, 3)
        gs.units.append(u_hkn)

        # Place an alive Ordos unit at (2, 2) (enemy, should NOT reveal for Atreides)
        u_ord = Unit("CombatTank", "Ordos", 2, 2)
        gs.units.append(u_ord)

        # Place an alive Atreides unit at (10, 10) (should reveal radius 3, far from building)
        u_atr = Unit("Trike", "Atreides", 10, 10)
        gs.units.append(u_atr)

        vis = gs.compute_visibility("Atreides")

        # The alive Atreides building at (5, 5) reveals tiles with Manhattan distance <= 4
        # Check that (5, 5) itself is visible
        self.assertIn((5, 5), vis)

        # Check tiles within radius 4 of the building at (5, 5)
        # (5, 5) + (0, 1) = (5, 6) distance 1
        self.assertIn((5, 6), vis)
        # (5, 5) + (0, 4) = (5, 9) distance 4
        self.assertIn((5, 9), vis)
        # (5, 5) + (0, 5) = (5, 10) distance 5 - should NOT be visible
        self.assertNotIn((5, 10), vis)

        # The alive Atreides unit at (10, 10) reveals tiles with Manhattan distance <= 3
        # (10, 10) itself - far from the building at (5,5), dist = |10-5|+|10-5| = 10 > 4
        self.assertIn((10, 10), vis)
        # (10, 10) + (0, 3) = (10, 13) distance 3 from unit, far from building
        self.assertIn((10, 13), vis)
        # (10, 10) + (0, 4) = (10, 14) distance 4 from unit - should NOT be visible from unit
        self.assertNotIn((10, 14), vis)

        # Dead building should not reveal any tiles on its own
        # (5, 5) is still visible because the ALIVE building at (5, 5) reveals it
        self.assertIn((5, 5), vis)

        # Enemy units should not reveal tiles for Atreides
        # Harkonnen Trike at (3, 3): (3, 0) has dist 3 from enemy, but dist |5-3|+|5-0|=7 from building
        self.assertNotIn((3, 0), vis)

        # Ordos unit at (2, 2): (2, 0) has dist 2 from enemy, but dist |5-2|+|5-0|=8 from building
        self.assertNotIn((2, 0), vis)

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

    def test_unit_move_towards(self):
        """test_unit_move_towards: Unit.move_towards basic movement and bounds clamping."""
        # Test 1: Move right (x increases)
        gs = GameState(GridMap(8, 8))
        harv = Unit("Harvester", "Atreides", 2, 2)
        gs.units.append(harv)
        result = harv.move_towards(5, 2, gs.game_map)
        self.assertEqual(result, (3, 2))
        self.assertEqual(harv.x, 3)
        self.assertEqual(harv.y, 2)

        # Test 2: Move left (x decreases)
        gs2 = GameState(GridMap(8, 8))
        harv2 = Unit("Harvester", "Harkonnen", 5, 4)
        gs2.units.append(harv2)
        result = harv2.move_towards(1, 4, gs2.game_map)
        self.assertEqual(result, (4, 4))
        self.assertEqual(harv2.x, 4)
        self.assertEqual(harv2.y, 4)

        # Test 3: Target same x, move y (diagonal not allowed - move x first, then y)
        gs3 = GameState(GridMap(8, 8))
        harv3 = Unit("Harvester", "Ordos", 3, 3)
        gs3.units.append(harv3)
        result = harv3.move_towards(3, 6, gs3.game_map)
        self.assertEqual(result, (3, 4))
        self.assertEqual(harv3.x, 3)
        self.assertEqual(harv3.y, 4)

        # Test 4: Target same position (no movement needed)
        gs4 = GameState(GridMap(8, 8))
        harv4 = Unit("Harvester", "Atreides", 4, 4)
        gs4.units.append(harv4)
        result = harv4.move_towards(4, 4, gs4.game_map)
        self.assertEqual(result, (4, 4))
        self.assertEqual(harv4.x, 4)
        self.assertEqual(harv4.y, 4)

        # Test 5: Bounds clamping - move right beyond map width
        gs5 = GameState(GridMap(5, 5))
        harv5 = Unit("Harvester", "Atreides", 3, 3)
        gs5.units.append(harv5)
        result = harv5.move_towards(100, 100, gs5.game_map)
        self.assertEqual(result, (4, 3))  # nx clamped to width-1=4, ny stays at 3 (x changed so no y move)
        self.assertEqual(harv5.x, 4)
        self.assertEqual(harv5.y, 3)

        # Test 6: Bounds clamping - move down beyond map height
        gs6 = GameState(GridMap(5, 5))
        harv6 = Unit("Harvester", "Atreides", 3, 3)
        gs6.units.append(harv6)
        result = harv6.move_towards(3, 100, gs6.game_map)
        self.assertEqual(result, (3, 4))  # nx stays 3 (no x change), ny clamped to height-1=4
        self.assertEqual(harv6.x, 3)
        self.assertEqual(harv6.y, 4)

        # Test 7: Move towards target where x doesn't change, then y moves
        gs7 = GameState(GridMap(8, 8))
        harv7 = Unit("Harvester", "Atreides", 5, 5)
        gs7.units.append(harv7)
        result = harv7.move_towards(5, 1, gs7.game_map)
        self.assertEqual(result, (5, 4))
        self.assertEqual(harv7.x, 5)
        self.assertEqual(harv7.y, 4)

        # Test 8: Move towards target where x doesn't change, y decreases
        gs8 = GameState(GridMap(8, 8))
        harv8 = Unit("Harvester", "Atreides", 5, 5)
        gs8.units.append(harv8)
        result = harv8.move_towards(5, 1, gs8.game_map)
        self.assertEqual(result, (5, 4))


    def test_unit_attack(self):
        """test_unit_attack: in-range damage, out-of-range (0), and HP clamping at 0."""
        # Test 1: In-range attack damages target (bullet vs heavy: 20 * 0.25 = 5)
        gs = GameState(GridMap(8, 8))
        attacker = Unit("CombatUnit", "Atreides", 2, 2, hp=50)
        target = Unit("TargetUnit", "Harkonnen", 2, 3, hp=50)  # dist = 1, within range 3
        gs.units.append(attacker)
        gs.units.append(target)
        dmg = attacker.attack(target)
        self.assertEqual(dmg, 5)  # compute_damage("bullet", "heavy", 20) = 5
        self.assertEqual(target.hp, 45)  # 50 - 5 = 45

        # Test 2: Out-of-range attack returns 0
        gs2 = GameState(GridMap(8, 8))
        attacker2 = Unit("Sniper", "Atreides", 1, 1, hp=50, attack_range=3)
        target2 = Unit("TargetUnit", "Harkonnen", 5, 1, hp=50)  # dist = 4, > range 3
        gs2.units.append(attacker2)
        gs2.units.append(target2)
        dmg2 = attacker2.attack(target2)
        self.assertEqual(dmg2, 0)
        self.assertEqual(target2.hp, 50)  # HP unchanged

        # Test 3: HP clamped at 0 when damage exceeds HP
        gs3 = GameState(GridMap(8, 8))
        attacker3 = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
        target3 = Unit("WeakUnit", "Harkonnen", 1, 2, hp=5)  # dist = 1, within range
        gs3.units.append(attacker3)
        gs3.units.append(target3)
        dmg3 = attacker3.attack(target3)
        self.assertEqual(dmg3, 5)
        self.assertEqual(target3.hp, 0)  # clamped at 0, not negative

        # Test 4: Dead attacker returns 0
        gs4 = GameState(GridMap(8, 8))
        attacker4 = Unit("CombatUnit", "Atreides", 1, 1, hp=0)  # dead
        target4 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
        gs4.units.append(attacker4)
        gs4.units.append(target4)
        dmg4 = attacker4.attack(target4)
        self.assertEqual(dmg4, 0)

        # Test 5: Dead target returns 0
        gs5 = GameState(GridMap(8, 8))
        attacker5 = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
        target5 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=0)  # dead
        gs5.units.append(attacker5)
        gs5.units.append(target5)
        dmg5 = attacker5.attack(target5)
        self.assertEqual(dmg5, 0)

        # Test 6: Default weapon vs default armor (bullet vs heavy)
        gs6 = GameState(GridMap(8, 8))
        attacker6 = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
        target6 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=100)
        gs6.units.append(attacker6)
        gs6.units.append(target6)
        dmg6 = attacker6.attack(target6)
        # compute_damage("bullet", "heavy", 20) = max(1, int(20 * 0.25 + 0.5)) = max(1, 5) = 5
        self.assertEqual(dmg6, 5)
        self.assertEqual(target6.hp, 95)

    def test_unit_xp_from_attack(self):
        """test_unit_xp_from_attack: verify XP gain from combat, HP decrease, and rank promotion.

        - When a unit damages an enemy target, its xp increases by the amount of damage dealt.
        - When a unit damages an enemy target, the target's hp decreases and the attacker's xp increases accordingly.
        - XP gain is 0 when the attack misses (target out of range or attacker/target dead).
        - XP gain works correctly with the existing rank promotion thresholds (rank 1 at xp >= 100, rank 2 at xp >= 250).
        """
        # Test 1: In-range attack grants XP equal to damage dealt
        gs = GameState(GridMap(8, 8))
        attacker = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
        target = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
        gs.units.append(attacker)
        gs.units.append(target)
        dmg = attacker.attack(target)
        self.assertEqual(dmg, 5)  # compute_damage("bullet", "heavy", 20) = 5
        self.assertEqual(target.hp, 45)  # 50 - 5 = 45
        self.assertEqual(attacker.xp, 5)  # gained 5 XP equal to damage

        # Test 2: XP gain works correctly with rank promotion thresholds
        gs2 = GameState(GridMap(8, 8))
        attacker2 = Unit("CombatUnit", "Atreides", 1, 1, hp=50, xp=90)
        target2 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
        gs2.units.append(attacker2)
        gs2.units.append(target2)
        # Attack 5 damage: xp goes from 90 to 95 (still rank 0)
        dmg2 = attacker2.attack(target2)
        self.assertEqual(dmg2, 5)
        self.assertEqual(attacker2.xp, 95)
        self.assertEqual(attacker2.rank, 0)  # still rank 0, need 5 more XP for rank 1

        # Three more attacks of 5 dmg each = 15 XP, total 95 + 15 = 110 >= 100 => rank 1
        for _ in range(3):
            dmg2 = attacker2.attack(target2)
            self.assertEqual(dmg2, 5)
        self.assertEqual(attacker2.xp, 110)
        self.assertEqual(attacker2.rank, 1)  # promoted to rank 1
        self.assertEqual(attacker2.attack_damage, 25)  # base 20 + 5 from rank 1

        # Test 3: XP gain is 0 when attack misses (target out of range)
        gs3 = GameState(GridMap(8, 8))
        attacker3 = Unit("Sniper", "Atreides", 1, 1, hp=50, attack_range=3)
        target3 = Unit("TargetUnit", "Harkonnen", 5, 1, hp=50)  # dist = 4, > range 3
        gs3.units.append(attacker3)
        gs3.units.append(target3)
        dmg3 = attacker3.attack(target3)
        self.assertEqual(dmg3, 0)
        self.assertEqual(attacker3.xp, 0)  # no XP gained on miss

        # Test 4: XP gain is 0 when attacker is dead
        gs4 = GameState(GridMap(8, 8))
        attacker4 = Unit("CombatUnit", "Atreides", 1, 1, hp=0)  # dead
        target4 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
        gs4.units.append(attacker4)
        gs4.units.append(target4)
        dmg4 = attacker4.attack(target4)
        self.assertEqual(dmg4, 0)
        self.assertEqual(attacker4.xp, 0)  # no XP gained when dead

        # Test 5: XP gain is 0 when target is dead
        gs5 = GameState(GridMap(8, 8))
        attacker5 = Unit("CombatUnit", "Atreides", 1, 1, hp=50)
        target5 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=0)  # dead
        gs5.units.append(attacker5)
        gs5.units.append(target5)
        dmg5 = attacker5.attack(target5)
        self.assertEqual(dmg5, 0)
        self.assertEqual(attacker5.xp, 0)  # no XP gained when target dead

        # Test 6: Rank promotion to rank 2 at xp >= 250
        gs6 = GameState(GridMap(8, 8))
        attacker6 = Unit("CombatUnit", "Atreides", 1, 1, hp=50, xp=200)
        target6 = Unit("TargetUnit", "Harkonnen", 1, 2, hp=50)
        gs6.units.append(attacker6)
        gs6.units.append(target6)
        # Need 50 more XP to reach 250 for rank 2
        for _ in range(10):
            dmg6 = attacker6.attack(target6)
            self.assertEqual(dmg6, 5)
        self.assertEqual(attacker6.xp, 250)
        self.assertEqual(attacker6.rank, 2)  # promoted to rank 2
        self.assertEqual(attacker6.attack_damage, 30)  # base 20 + 5 (rank 1) + 5 (rank 2)
        """test_train_unit: successful training with credit deduction and unit creation,
        and insufficient credits returning None."""
        # Test 1: Successful training - Trike costs 150
        gs = GameState(GridMap(8, 8))
        result = gs.train_unit("Atreides", "Trike", 3, 3)
        self.assertIsNotNone(result)
        self.assertEqual(result.unit_type, "Trike")
        self.assertEqual(result.house, "Atreides")
        self.assertEqual(result.x, 3)
        self.assertEqual(result.y, 3)
        self.assertIn(result, gs.units)
        self.assertEqual(gs.credits["Atreides"], 850)  # 1000 - 150

        # Test 2: Successful training - CombatTank costs 300
        gs2 = GameState(GridMap(8, 8))
        result2 = gs2.train_unit("Harkonnen", "CombatTank", 5, 5)
        self.assertIsNotNone(result2)
        self.assertEqual(result2.unit_type, "CombatTank")
        self.assertEqual(result2.house, "Harkonnen")
        self.assertEqual(result2.x, 5)
        self.assertEqual(result2.y, 5)
        self.assertIn(result2, gs2.units)
        self.assertEqual(gs2.credits["Harkonnen"], 700)  # 1000 - 300

        # Test 3: Successful training - Harvester costs 400
        gs3 = GameState(GridMap(8, 8))
        result3 = gs3.train_unit("Ordos", "Harvester", 2, 2)
        self.assertIsNotNone(result3)
        self.assertEqual(result3.unit_type, "Harvester")
        self.assertEqual(result3.house, "Ordos")
        self.assertEqual(result3.x, 2)
        self.assertEqual(result3.y, 2)
        self.assertIn(result3, gs3.units)
        self.assertEqual(gs3.credits["Ordos"], 600)  # 1000 - 400

        # Test 4: Insufficient credits returns None
        gs4 = GameState(GridMap(8, 8))
        result4 = gs4.train_unit("Atreides", "CombatTank", 1, 1)  # costs 300, but credits = 1000 initially
        # Actually with 1000 credits this should succeed, let's test with a unit type that costs more than 1000
        # or test with insufficient initial credits by modifying credits first
        # Let's test with a custom credit situation
        gs4 = GameState(GridMap(8, 8))
        gs4.credits["Atreides"] = 100  # set low credits
        result4 = gs4.train_unit("Atreides", "CombatTank", 1, 1)  # costs 300
        self.assertIsNone(result4)
        self.assertEqual(gs4.credits["Atreides"], 100)  # credits should remain unchanged

        # Test 5: Unknown unit type defaults to cost 200
        gs5 = GameState(GridMap(8, 8))
        result5 = gs5.train_unit("Atreides", "UnknownUnit", 1, 1)
        self.assertIsNotNone(result5)  # 1000 >= 200
        self.assertEqual(gs5.credits["Atreides"], 800)  # 1000 - 200


    def test_spawn_special_unit(self):
        """test_spawn_special_unit: verify stats, credit deduction, and failure cases
        for all three houses plus insufficient credits and unknown house."""
        expected_types = {
            "Atreides": "SonicTank",
            "Harkonnen": "Devastator",
            "Ordos": "Deviator",
        }
        for i, house in enumerate(["Atreides", "Harkonnen", "Ordos"]):
            gs = GameState(GridMap(8, 8))
            gs.credits[house] = 1000
            result = gs.spawn_special_unit(house, 2 + i, 3 + i)
            self.assertIsNotNone(result)
            spec = HOUSE_SPECIAL_UNITS[house]
            # Unit type and house
            self.assertEqual(result.unit_type, expected_types[house])
            self.assertEqual(result.house, house)
            # Position
            self.assertEqual(result.x, 2 + i)
            self.assertEqual(result.y, 3 + i)
            # Configured stats
            self.assertEqual(result.hp, spec["hp"])
            self.assertEqual(result.max_hp, spec["max_hp"])
            self.assertEqual(result.attack_damage, spec["attack_damage"])
            self.assertEqual(result.attack_range, spec["attack_range"])
            self.assertEqual(result.weapon_type, spec["weapon_type"])
            self.assertEqual(result.armor_type, spec["armor_type"])
            # Appended to units, credits deducted by 300
            self.assertIn(result, gs.units)
            self.assertEqual(gs.credits[house], 1000 - SPECIAL_UNIT_COST)

        # Exact stat spot checks from the ticket
        self.assertEqual(HOUSE_SPECIAL_UNITS["Atreides"],
                         {"unit_type": "SonicTank", "hp": 130, "max_hp": 130,
                          "attack_damage": 45, "attack_range": 4,
                          "weapon_type": "shell", "armor_type": "heavy"})
        self.assertEqual(HOUSE_SPECIAL_UNITS["Harkonnen"],
                         {"unit_type": "Devastator", "hp": 220, "max_hp": 220,
                          "attack_damage": 55, "attack_range": 3,
                          "weapon_type": "shell", "armor_type": "heavy"})
        self.assertEqual(HOUSE_SPECIAL_UNITS["Ordos"],
                         {"unit_type": "Deviator", "hp": 110, "max_hp": 110,
                          "attack_damage": 35, "attack_range": 4,
                          "weapon_type": "missile", "armor_type": "heavy"})

        # Insufficient credits: returns None, credits unchanged, no unit appended
        gs2 = GameState(GridMap(8, 8))
        gs2.credits["Atreides"] = SPECIAL_UNIT_COST - 1  # 299 < 300
        result2 = gs2.spawn_special_unit("Atreides", 1, 1)
        self.assertIsNone(result2)
        self.assertEqual(gs2.credits["Atreides"], SPECIAL_UNIT_COST - 1)
        self.assertEqual(len(gs2.units), 0)

        # Unknown house: returns None even with enough credits
        gs3 = GameState(GridMap(8, 8))
        gs3.credits["Corrino"] = 5000
        result3 = gs3.spawn_special_unit("Corrino", 1, 1)
        self.assertIsNone(result3)
        self.assertEqual(gs3.credits["Corrino"], 5000)
        self.assertEqual(len(gs3.units), 0)

        # Known house absent from credits dict (get() defaults to 0): returns None
        gs4 = GameState(GridMap(8, 8))
        del gs4.credits["Atreides"]
        result4 = gs4.spawn_special_unit("Atreides", 1, 1)
        self.assertIsNone(result4)
        self.assertNotIn("Atreides", gs4.credits)
        self.assertEqual(len(gs4.units), 0)

    def test_construct_building(self):
        gs = GameState(GridMap(8, 8))
        result = gs.construct_building("Atreides", "WindTrap", 2, 2)
        self.assertIsNotNone(result)
        self.assertEqual(result.building_type, "WindTrap")
        self.assertEqual(result.house, "Atreides")
        self.assertEqual(result.x, 2)
        self.assertEqual(result.y, 2)
        self.assertEqual(result.power_produced, 100)
        self.assertEqual(result.power_consumed, 0)
        self.assertEqual(gs.credits["Atreides"], 800)
        self.assertIn(result, gs.buildings)

        gs5 = GameState(GridMap(8, 8))
        gs5.credits["Atreides"] = 100
        self.assertIsNone(gs5.construct_building("Atreides", "WindTrap", 1, 1))
        self.assertEqual(gs5.credits["Atreides"], 100)

    def test_check_winner(self):
        gs = GameState(GridMap(8, 8))
        gs.units.extend([Unit("Trike", "Atreides", 2, 2, hp=50), Unit("Trike", "Harkonnen", 4, 4, hp=50)])
        self.assertIsNone(gs.check_winner())

        gs2 = GameState(GridMap(8, 8))
        gs2.units.append(Unit("Trike", "Atreides", 2, 2, hp=50))
        self.assertEqual(gs2.check_winner(), "Atreides")

        gs3 = GameState(GridMap(8, 8))
        gs3.units.append(Unit("Trike", "Atreides", 2, 2, hp=0))
        self.assertEqual(gs3.check_winner(), "Draw")


    def test_game_state_to_dict(self):
        """test_game_state_to_dict: verify GameState.to_dict serializes correctly."""
        gs = GameState(GridMap(10, 10))
        gs.tick_count = 42
        gs.credits = {"Atreides": 1500, "Harkonnen": 800, "Ordos": 600}
        
        # Add a building
        b = Building("Refinery", "Atreides", 3, 3, hp=350, max_hp=400)
        gs.buildings.append(b)
        
        # Add a unit
        u = Unit("Trike", "Harkonnen", 5, 5, hp=80, max_hp=100, spice_carried=200)
        gs.units.append(u)
        
        # Add a sandworm
        ws = Sandworm(7, 8)
        gs.sandworms.append(ws)
        
        d = gs.to_dict()
        
        # Check basic fields
        self.assertEqual(d["width"], 10)
        self.assertEqual(d["height"], 10)
        self.assertEqual(d["tiles"], [["SAND"] * 10 for _ in range(10)])
        self.assertEqual(d["credits"], {"Atreides": 1500, "Harkonnen": 800, "Ordos": 600})
        
        # Check building dict
        building_dict = d["buildings"][0]
        self.assertEqual(building_dict["building_type"], "Refinery")
        self.assertEqual(building_dict["house"], "Atreides")
        self.assertEqual(building_dict["x"], 3)
        self.assertEqual(building_dict["y"], 3)
        self.assertEqual(building_dict["hp"], 350)
        self.assertEqual(building_dict["max_hp"], 400)
        
        # Check unit dict
        unit_dict = d["units"][0]
        self.assertEqual(unit_dict["unit_type"], "Trike")
        self.assertEqual(unit_dict["house"], "Harkonnen")
        self.assertEqual(unit_dict["x"], 5)
        self.assertEqual(unit_dict["y"], 5)
        self.assertEqual(unit_dict["hp"], 80)
        self.assertEqual(unit_dict["max_hp"], 100)
        self.assertEqual(unit_dict["spice_carried"], 200)
        
        # Check sandworm dict
        sandworm_dict = d["sandworms"][0]
        self.assertEqual(sandworm_dict["x"], 7)
        self.assertEqual(sandworm_dict["y"], 8)

    def test_generate_sandworm_and_explosion_svg(self):
        """Verify generate_sandworm_svg and generate_explosion_svg produce valid multi-layer SVGs."""
        worm_svg = generate_sandworm_svg(size=32)
        self.assertIn("<svg", worm_svg)
        self.assertIn("<circle", worm_svg)
        self.assertIn("width=\"32\"", worm_svg)

        exp0 = generate_explosion_svg(size=32, frame=0)
        exp1 = generate_explosion_svg(size=32, frame=1)
        self.assertIn("<svg", exp0)
        self.assertIn("#ff4500", exp0)
        self.assertNotEqual(exp0, exp1)

    def test_repair_building(self):
        """test_repair_building: verify normal repair, credit deduction, clamping at max_hp, and dead building rejection."""
        # Test 1: Normal repair - missing=50, cost=(50+1)//2=25, 25 credits restore 50 HP
        gs = GameState(GridMap(8, 8))
        b = Building("Barracks", "Atreides", 2, 2, hp=350, max_hp=400)
        gs.buildings.append(b)
        gs.credits["Atreides"] = 25
        result = gs.repair_building(b, max_hp_to_restore=50)
        self.assertEqual(result, 50)
        self.assertEqual(b.hp, 400)  # clamped to max_hp
        self.assertEqual(gs.credits["Atreides"], 0)

        # Test 2: Repair with one extra credit (26 credits for 50 HP repair, leaves 1 credit)
        gs2 = GameState(GridMap(8, 8))
        b2 = Building("Barracks", "Harkonnen", 3, 3, hp=350, max_hp=400)
        gs2.buildings.append(b2)
        gs2.credits["Harkonnen"] = 26
        result = gs2.repair_building(b2, max_hp_to_restore=50)
        self.assertEqual(result, 50)
        self.assertEqual(b2.hp, 400)
        self.assertEqual(gs2.credits["Harkonnen"], 1)

        # Test 3: Repair with insufficient credits (13 credits restores 26 HP)
        gs3 = GameState(GridMap(8, 8))
        b3 = Building("Barracks", "Ordos", 4, 4, hp=350, max_hp=400)
        gs3.buildings.append(b3)
        gs3.credits["Ordos"] = 13
        result = gs3.repair_building(b3, max_hp_to_restore=50)
        # missing = min(400-350, 50) = 50, cost = 26
        # With 13 credits: actual_restore = min(13*2, 50) = 26, actual_cost = 13
        self.assertEqual(result, 26)
        self.assertEqual(b3.hp, 376)  # 350 + 26 = 376
        self.assertEqual(gs3.credits["Ordos"], 0)

        # Test 4: Clamping at max_hp with partial credits
        gs4 = GameState(GridMap(8, 8))
        b4 = Building("Barracks", "Atreides", 1, 1, hp=390, max_hp=400)
        gs4.buildings.append(b4)
        gs4.credits["Atreides"] = 5  # 5 credits = 10 HP restores exactly the 10 missing
        result = gs4.repair_building(b4, max_hp_to_restore=50)
        # missing = min(400-390, 50) = 10, cost = (10+1)//2 = 5
        # With 5 credits: actual_restore = min(10, 10) = 10, actual_cost = 5
        self.assertEqual(result, 10)
        self.assertEqual(b4.hp, 400)  # clamped to max_hp
        self.assertEqual(gs4.credits["Atreides"], 0)

        # Test 5: Dead building (hp == 0) rejection
        gs5 = GameState(GridMap(8, 8))
        b5 = Building("Barracks", "Atreides", 1, 1, hp=0, max_hp=400)
        gs5.buildings.append(b5)
        gs5.credits["Atreides"] = 100
        result = gs5.repair_building(b5, max_hp_to_restore=50)
        self.assertEqual(result, 0)
        self.assertEqual(b5.hp, 0)  # unchanged

        # Test 6: Already full HP building returns 0
        gs6 = GameState(GridMap(8, 8))
        b6 = Building("Barracks", "Harkonnen", 2, 2, hp=400, max_hp=400)
        gs6.buildings.append(b6)
        gs6.credits["Harkonnen"] = 100
        result = gs6.repair_building(b6, max_hp_to_restore=50)
        self.assertEqual(result, 0)

        # Test 7: max_hp_to_restore <= 0 returns 0
        gs7 = GameState(GridMap(8, 8))
        b7 = Building("Barracks", "Ordos", 3, 3, hp=300, max_hp=400)
        gs7.buildings.append(b7)
        gs7.credits["Ordos"] = 50
        result = gs7.repair_building(b7, max_hp_to_restore=0)
        self.assertEqual(result, 0)

        # Test 8: max_hp_to_restore negative returns 0
        result = gs7.repair_building(b7, max_hp_to_restore=-10)
        self.assertEqual(result, 0)

        # Test 9: House with no credits (credits dict doesn't have the house)
        gs8 = GameState(GridMap(8, 8))
        b8 = Building("Barracks", "UnknownHouse", 1, 1, hp=300, max_hp=400)
        gs8.buildings.append(b8)
        # "UnknownHouse" not in default credits, get() returns 0
        result = gs8.repair_building(b8, max_hp_to_restore=50)
        self.assertEqual(result, 0)
        self.assertEqual(b8.hp, 300)  # unchanged

    def test_detonate_spice_bloom(self):
        """Spice bloom converts center to SPICE_THICK and orthogonal SAND/DUNES to SPICE_THIN."""
        gs = GameState(GridMap(8, 8))
        # Corner-shaped terrain layout around the detonation point (3, 3):
        # two orthogonal neighbors preserved as ROCK/CONCRETE, plus DUNES/SAND neighbors.
        gs.game_map.set_tile(4, 3, ROCK)
        gs.game_map.set_tile(2, 3, CONCRETE)
        gs.game_map.set_tile(3, 4, DUNES)

        count = gs.detonate_spice_bloom(3, 3)

        # Center + 2 terrain neighbors ((3, 2) default SAND and (3, 4) DUNES) = 3 modified tiles.
        self.assertEqual(count, 3)
        self.assertEqual(gs.game_map.get_tile(3, 3), SPICE_THICK)
        self.assertEqual(gs.game_map.get_tile(3, 2), SPICE_THIN)
        self.assertEqual(gs.game_map.get_tile(3, 4), SPICE_THIN)
        # ROCK/CONCRETE neighbors are preserved.
        self.assertEqual(gs.game_map.get_tile(4, 3), ROCK)
        self.assertEqual(gs.game_map.get_tile(2, 3), CONCRETE)

        # Out-of-bounds detonation modifies nothing and returns 0.
        self.assertEqual(gs.detonate_spice_bloom(-1, 3), 0)
        self.assertEqual(gs.detonate_spice_bloom(8, 3), 0)
        self.assertEqual(gs.game_map.get_tile(3, 3), SPICE_THICK)

    def test_generate_minimap_svg(self):
        """Verify generate_minimap_svg renders valid SVG containing terrain, house, and sandworm colors."""
        gs = GameState(GridMap(8, 8))
        gs.game_map.set_tile(1, 1, ROCK)
        gs.buildings.append(Building("Barracks", "Atreides", 2, 2))
        gs.units.append(Unit("Trooper", "Harkonnen", 3, 3))
        gs.sandworms.append(Sandworm(4, 4))
        
        svg = generate_minimap_svg(gs.to_dict(), pixel_size=4)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn('width="32"', svg)
        self.assertIn('height="32"', svg)
        # Rock color
        self.assertIn("#5c6370", svg)
        # Atreides color
        self.assertIn("#2563eb", svg)
        # Harkonnen color
        self.assertIn("#dc2626", svg)
        # Sandworm color
        self.assertIn("#b45309", svg)


    def test_step_ai_commander(self):
        """test_step_ai_commander: verify AI commander spawns tank or moves/idles."""
        # Test 1: Spawn CombatTank when enough credits and alive building exists
        gs = GameState(GridMap(8, 8))
        gs.credits["Atreides"] = 500
        b = Building("Barracks", "Atreides", 3, 3)
        gs.buildings.append(b)
        result = gs.step_ai_commander("Atreides")
        self.assertEqual(result, "spawned_tank")
        self.assertEqual(gs.credits["Atreides"], 300)  # 500 - 200
        tank = gs.units[-1]
        self.assertEqual(tank.unit_type, "CombatTank")
        self.assertEqual(tank.house, "Atreides")
        self.assertEqual(tank.x, 3)
        self.assertEqual(tank.y, 3)
        self.assertEqual(tank.hp, 120)
        self.assertEqual(tank.max_hp, 120)
        self.assertEqual(tank.weapon_type, "shell")
        self.assertEqual(tank.armor_type, "heavy")
        self.assertEqual(tank.attack_damage, 25)
        self.assertEqual(tank.attack_range, 3)

        # Test 2: Insufficient credits -> advance units instead
        gs2 = GameState(GridMap(8, 8))
        gs2.credits["Atreides"] = 100
        u = Unit("Trike", "Atreides", 2, 2)
        gs2.units.append(u)
        enemy_building = Building("Barracks", "Harkonnen", 5, 5)
        gs2.buildings.append(enemy_building)
        result = gs2.step_ai_commander("Atreides")
        self.assertEqual(result, "advanced_units")
        self.assertEqual(u.x, 3)
        self.assertEqual(u.y, 2)

        # Test 3: No alive buildings -> advance units
        gs3 = GameState(GridMap(8, 8))
        gs3.credits["Atreides"] = 500
        u3 = Unit("Trike", "Atreides", 2, 2)
        gs3.units.append(u3)
        result = gs3.step_ai_commander("Atreides")
        self.assertEqual(result, "idle")

        # Test 4: No combat units (only harvesters) -> idle
        gs4 = GameState(GridMap(8, 8))
        gs4.credits["Atreides"] = 100
        harv = Unit("Harvester", "Atreides", 2, 2)
        gs4.units.append(harv)
        result = gs4.step_ai_commander("Atreides")
        self.assertEqual(result, "idle")

        # Test 5: Enough credits but no alive buildings -> advance units
        gs5 = GameState(GridMap(8, 8))
        gs5.credits["Atreides"] = 500
        dead_b = Building("Barracks", "Atreides", 3, 3, hp=0)
        gs5.buildings.append(dead_b)
        u5 = Unit("Trike", "Atreides", 2, 2)
        gs5.units.append(u5)
        result = gs5.step_ai_commander("Atreides")
        self.assertEqual(result, "idle")

        # Test 6: Basic advance towards enemy
        gs6 = GameState(GridMap(8, 8))
        gs6.credits["Atreides"] = 100
        u6 = Unit("Trike", "Atreides", 2, 2, hp=50)
        gs6.units.append(u6)
        enemy6 = Unit("Trike", "Harkonnen", 5, 5, hp=50)
        gs6.units.append(enemy6)
        result = gs6.step_ai_commander("Atreides")
        self.assertEqual(result, "advanced_units")
        self.assertEqual(u6.x, 3)
        self.assertEqual(u6.y, 2)

        # Test 7: No enemies nearby -> idle
        gs7 = GameState(GridMap(8, 8))
        gs7.credits["Atreides"] = 100
        u7 = Unit("Trike", "Atreides", 4, 4, hp=50)
        gs7.units.append(u7)
        result = gs7.step_ai_commander("Atreides")
        self.assertEqual(result, "idle")

    def test_step_carryall_rescue(self):
        # Setup game state with Refinery and Harvester
        gm = GridMap(10, 10)
        gs = GameState(gm)
        refinery = Building("Refinery", "Atreides", 1, 1, hp=400)
        gs.buildings.append(refinery)

        # Harvester in danger (distance <= 2 from sandworm)
        harvester = Unit("Harvester", "Atreides", 5, 5, hp=100)
        gs.units.append(harvester)
        worm = Sandworm(5, 6)  # distance = 1
        gs.sandworms.append(worm)

        # Carryall should airlift harvester back to refinery
        rescued = gs.step_carryall_rescue("Atreides")
        self.assertEqual(rescued, 1)
        self.assertEqual(harvester.x, 1)
        self.assertEqual(harvester.y, 1)

        # Harvester already at refinery is skipped
        rescued2 = gs.step_carryall_rescue("Atreides")
        self.assertEqual(rescued2, 0)

        # No rescue if power efficiency is below 0.5
        harvester2 = Unit("Harvester", "Atreides", 6, 6, hp=100)
        gs.units.append(harvester2)
        power_drain = Building("Barracks", "Atreides", 2, 2, power_produced=0, power_consumed=100)
        gs.buildings.append(power_drain)
        self.assertLess(gs.power_efficiency("Atreides"), 0.5)
        rescued3 = gs.step_carryall_rescue("Atreides")
        self.assertEqual(rescued3, 0)
        self.assertEqual(harvester2.x, 6)

        # No rescue if no alive refinery exists
        refinery.hp = 0
        gs.buildings.remove(power_drain)
        rescued4 = gs.step_carryall_rescue("Atreides")
        self.assertEqual(rescued4, 0)

    def test_order_starport_unit(self):
        gm = GridMap(10, 10)
        gs = GameState(gm)
        gs.credits["Atreides"] = 1000

        # Ordering without Starport returns None
        unit = gs.order_starport_unit("Atreides", "CombatTank", 2, 2)
        self.assertIsNone(unit)

        # Build alive Starport
        starport = Building("Starport", "Atreides", 1, 1, hp=500)
        gs.buildings.append(starport)

        # Even tick: 20% discount on CombatTank (base=300 -> 300 * 0.8 = 240)
        gs.tick_count = 0
        unit_even = gs.order_starport_unit("Atreides", "CombatTank", 3, 3)
        self.assertIsNotNone(unit_even)
        self.assertEqual(unit_even.unit_type, "CombatTank")
        self.assertEqual(unit_even.x, 3)
        self.assertEqual(unit_even.y, 3)
        self.assertEqual(gs.credits["Atreides"], 760)

        # Odd tick: 20% surge on Trike (base=150 -> 150 * 1.2 = 180)
        gs.tick_count = 1
        unit_odd = gs.order_starport_unit("Atreides", "Trike", 4, 4)
        self.assertIsNotNone(unit_odd)
        self.assertEqual(unit_odd.unit_type, "Trike")
        self.assertEqual(gs.credits["Atreides"], 760 - 180)

        # Insufficient credits returns None
        gs.credits["Atreides"] = 50
        unit_fail = gs.order_starport_unit("Atreides", "CombatTank", 5, 5)
        self.assertIsNone(unit_fail)


    def test_fire_death_hand(self):
        """test_fire_death_hand: Palace required, splash damage at dist 0/1, friendlies unharmed."""
        # Test 1: Without a Palace, fire_death_hand returns 0 and deals no damage.
        gs = GameState(GridMap(8, 8))
        enemy = Unit("Trike", "Harkonnen", 4, 4, hp=100)
        gs.units.append(enemy)
        result = gs.fire_death_hand("Atreides", 4, 4)
        self.assertEqual(result, 0)
        self.assertEqual(enemy.hp, 100)

        # Dead Palace does not count.
        gs2 = GameState(GridMap(8, 8))
        gs2.buildings.append(Building("Palace", "Atreides", 0, 0, hp=0))
        enemy2 = Unit("Trike", "Harkonnen", 4, 4, hp=100)
        gs2.units.append(enemy2)
        result2 = gs2.fire_death_hand("Atreides", 4, 4)
        self.assertEqual(result2, 0)
        self.assertEqual(enemy2.hp, 100)

        # Test 2: With an alive Palace, dist 0 -> 150, dist 1 -> 75, friendlies unharmed.
        gs3 = GameState(GridMap(8, 8))
        gs3.buildings.append(Building("Palace", "Atreides", 0, 0))
        enemy_center = Unit("Trike", "Harkonnen", 4, 4, hp=200)
        enemy_adjacent = Unit("Trike", "Ordos", 5, 4, hp=200)
        enemy_far = Unit("Trike", "Harkonnen", 6, 4, hp=200)
        friendly = Unit("Trike", "Atreides", 4, 4, hp=100)
        enemy_building_center = Building("Barracks", "Harkonnen", 4, 4, hp=400, max_hp=400)
        gs3.units.extend([enemy_center, enemy_adjacent, enemy_far, friendly])
        gs3.buildings.append(enemy_building_center)

        result3 = gs3.fire_death_hand("Atreides", 4, 4)
        # dist 0: enemy_center 150 + friendly excluded + enemy_building_center 150 = 300
        # dist 1: enemy_adjacent 75 = 75; enemy_far at dist 2: unaffected
        self.assertEqual(result3, 375)
        self.assertEqual(enemy_center.hp, 50)      # 200 - 150
        self.assertEqual(enemy_adjacent.hp, 125)   # 200 - 75
        self.assertEqual(enemy_far.hp, 200)        # dist 2, unaffected
        self.assertEqual(friendly.hp, 100)         # friendly, unharmed
        self.assertEqual(enemy_building_center.hp, 250)  # 400 - 150

        # Test 3: Damage is clamped to target's current HP.
        gs4 = GameState(GridMap(8, 8))
        gs4.buildings.append(Building("Palace", "Harkonnen", 0, 0))
        weak = Unit("Trike", "Atreides", 3, 3, hp=30)
        gs4.units.append(weak)
        result4 = gs4.fire_death_hand("Harkonnen", 3, 3)
        self.assertEqual(result4, 30)  # min(30, 150)
        self.assertEqual(weak.hp, 0)

        # Test 4: BUILDING_COSTS includes Palace at 600.
        self.assertEqual(BUILDING_COSTS.get("Palace"), 600)

    def test_step_turrets(self):
        """test_step_turrets: GunTurret auto-fire (rng 3, dmg 30), RocketTurret (rng 5, dmg 45, power >= 1.0)."""
        self.assertEqual(BUILDING_COSTS.get("GunTurret"), 250)
        self.assertEqual(BUILDING_COSTS.get("RocketTurret"), 350)

        # 1. GunTurret damages enemy within range 3 even without power generator
        gs = GameState(GridMap(10, 10))
        gun = Building("GunTurret", "Atreides", 2, 2, hp=250)
        gs.buildings.append(gun)
        enemy = Unit("Trike", "Harkonnen", 4, 3, hp=50)  # dist = |4-2| + |3-2| = 3
        gs.units.append(enemy)

        dmg = gs.step_turrets()
        self.assertEqual(dmg, 30)
        self.assertEqual(enemy.hp, 20)

        # 2. RocketTurret with power >= 1.0 fires at range 5
        gs2 = GameState(GridMap(10, 10))
        rocket = Building("RocketTurret", "Atreides", 1, 1, hp=350)
        gs2.buildings.append(rocket)
        # power balance is 0/0 -> efficiency 1.0
        enemy2 = Unit("CombatTank", "Harkonnen", 5, 2, hp=100)  # dist = |5-1| + |2-1| = 5
        gs2.units.append(enemy2)

        dmg2 = gs2.step_turrets()
        self.assertEqual(dmg2, 45)
        self.assertEqual(enemy2.hp, 55)

        # 3. RocketTurret under low power (< 1.0) cannot fire
        gs3 = GameState(GridMap(10, 10))
        rocket3 = Building("RocketTurret", "Atreides", 1, 1, hp=350)
        drain = Building("Factory", "Atreides", 0, 0, power_produced=0, power_consumed=100)
        gs3.buildings.extend([rocket3, drain])
        self.assertLess(gs3.power_efficiency("Atreides"), 1.0)
        enemy3 = Unit("Trike", "Harkonnen", 3, 2, hp=50)
        gs3.units.append(enemy3)

        dmg3 = gs3.step_turrets()
        self.assertEqual(dmg3, 0)
        self.assertEqual(enemy3.hp, 50)

    def test_sell_building(self):
        """test_sell_building: 50% proportional HP refund, removal from buildings list."""
        gm = GridMap(10, 10)
        gs = GameState(gm)
        gs.credits["Atreides"] = 500

        # 1. Full HP Refinery (cost=400, max_hp=400, hp=400) -> refund 200
        refinery = Building("Refinery", "Atreides", 2, 2, hp=400, max_hp=400)
        gs.buildings.append(refinery)
        refund1 = gs.sell_building(refinery)
        self.assertEqual(refund1, 200)
        self.assertEqual(refinery.hp, 0)
        self.assertNotIn(refinery, gs.buildings)
        self.assertEqual(gs.credits["Atreides"], 700)

        # 2. Half HP Refinery (hp=200/400) -> refund 100
        refinery_half = Building("Refinery", "Atreides", 3, 3, hp=200, max_hp=400)
        gs.buildings.append(refinery_half)
        refund2 = gs.sell_building(refinery_half)
        self.assertEqual(refund2, 100)
        self.assertEqual(refinery_half.hp, 0)
        self.assertNotIn(refinery_half, gs.buildings)
        self.assertEqual(gs.credits["Atreides"], 800)

        # 3. Selling a building not in gs.buildings returns 0
        unplaced = Building("Barracks", "Atreides", 4, 4, hp=250, max_hp=250)
        refund3 = gs.sell_building(unplaced)
        self.assertEqual(refund3, 0)
        self.assertEqual(gs.credits["Atreides"], 800)

    def test_capture_building(self):
        """test_capture_building: Engineer captures adjacent enemy building, heals up to 100 HP, consumed."""
        from dune3000.engine import UNIT_COSTS
        self.assertEqual(UNIT_COSTS.get("Engineer"), 200)

        gm = GridMap(10, 10)
        gs = GameState(gm)

        # 1. Adjacent enemy building capture
        target_b = Building("Refinery", "Harkonnen", 3, 3, hp=150, max_hp=400)
        engineer = Unit("Engineer", "Atreides", 3, 2, hp=50)  # adjacent dist=1
        gs.buildings.append(target_b)
        gs.units.append(engineer)

        success = gs.capture_building(engineer, target_b)
        self.assertTrue(success)
        self.assertEqual(target_b.house, "Atreides")
        self.assertEqual(target_b.hp, 250)  # 150 + 100
        self.assertEqual(engineer.hp, 0)
        self.assertNotIn(engineer, gs.units)

        # 2. Non-engineer cannot capture
        tank = Unit("CombatTank", "Atreides", 3, 4, hp=100)
        enemy_b = Building("Barracks", "Harkonnen", 3, 3, hp=200, max_hp=250)
        gs.buildings.append(enemy_b)
        gs.units.append(tank)
        self.assertFalse(gs.capture_building(tank, enemy_b))
        self.assertEqual(enemy_b.house, "Harkonnen")

        # 3. Out-of-range engineer (dist > 1) cannot capture
        far_eng = Unit("Engineer", "Atreides", 5, 5, hp=50)
        gs.units.append(far_eng)
        self.assertFalse(gs.capture_building(far_eng, enemy_b))
        self.assertEqual(enemy_b.house, "Harkonnen")
        self.assertEqual(far_eng.hp, 50)

        # 4. Same house building cannot be captured
        friendly_b = Building("Silo", "Atreides", 5, 4, hp=100, max_hp=150)
        gs.buildings.append(friendly_b)
        self.assertFalse(gs.capture_building(far_eng, friendly_b))

    def test_apply_sandstorm(self):
        """test_apply_sandstorm: 15 damage to exposed units on SAND/SPICE within radius, sheltered on ROCK/CONCRETE."""
        from dune3000.engine import SPICE_THICK, ROCK, CONCRETE
        gm = GridMap(10, 10)
        gm.set_tile(5, 5, SPICE_THICK)
        gm.set_tile(4, 5, ROCK)
        gm.set_tile(5, 6, CONCRETE)
        gs = GameState(gm)

        # Unit 1: on SAND at (5, 4), dist=1 <= 2 -> takes 15 dmg
        u_sand = Unit("Trike", "Atreides", 5, 4, hp=100)
        # Unit 2: on SPICE_THICK at (5, 5), dist=0 <= 2 -> takes 15 dmg
        u_spice = Unit("Harvester", "Atreides", 5, 5, hp=100)
        # Unit 3: on ROCK at (4, 5), dist=1 <= 2 -> sheltered, 0 dmg
        u_rock = Unit("CombatTank", "Atreides", 4, 5, hp=100)
        # Unit 4: on CONCRETE at (5, 6), dist=1 <= 2 -> sheltered, 0 dmg
        u_concrete = Unit("CombatTank", "Harkonnen", 5, 6, hp=100)
        # Unit 5: on SAND at (9, 9), dist=8 > 2 -> out of range, 0 dmg
        u_far = Unit("Trike", "Harkonnen", 9, 9, hp=100)

        gs.units.extend([u_sand, u_spice, u_rock, u_concrete, u_far])

        damaged = gs.apply_sandstorm(5, 5, radius=2)
        self.assertEqual(damaged, 2)
        self.assertEqual(u_sand.hp, 85)
        self.assertEqual(u_spice.hp, 85)
        self.assertEqual(u_rock.hp, 100)
        self.assertEqual(u_concrete.hp, 100)
        self.assertEqual(u_far.hp, 100)

    def test_saboteur(self):
        """test_saboteur: fast 2-step movement, worm ignore, instant demolition of building & death."""
        from dune3000.engine import UNIT_COSTS
        self.assertEqual(UNIT_COSTS.get("Saboteur"), 250)

        gm = GridMap(10, 10)
        gs = GameState(gm)

        # 1. Saboteur stats and 2-step movement with bounds clamping
        sab = Unit("Saboteur", "Ordos", 0, 0)
        self.assertEqual(sab.hp, 45)
        self.assertEqual(sab.max_hp, 45)
        self.assertEqual(sab.move_steps, 2)
        self.assertEqual(sab.attack_damage, 0)
        self.assertEqual(sab.attack_range, 0)
        self.assertEqual(sab.armor_type, "infantry")

        # Move towards (5, 0): moves 2 tiles along X
        sab.move_towards(5, 0, gm)
        self.assertEqual((sab.x, sab.y), (2, 0))

        # Clamp against map bounds: move towards (-10, 0)
        sab.move_towards(-10, 0, gm)
        self.assertEqual((sab.x, sab.y), (0, 0))

        # Cannot attack directly (returns 0)
        dummy_enemy = Unit("Trike", "Atreides", 0, 1, hp=100)
        self.assertEqual(sab.attack(dummy_enemy), 0)
        self.assertEqual(dummy_enemy.hp, 100)

        # 2. Sandworm ignores Saboteur
        worm = Sandworm(1, 0)
        gs.units.append(sab)
        # Even though sab is on SAND and adjacent to worm, worm ignores sab
        target = worm.find_nearest_target(gs.units, gm)
        self.assertIsNone(target)

        # 3. Successful sabotage: adjacent enemy building (dist <= 1)
        target_b = Building("WindTrap", "Atreides", 1, 0, hp=400, max_hp=400)
        gs.buildings.append(target_b)
        res = gs.sabotage(sab, target_b)
        self.assertTrue(res)
        self.assertEqual(target_b.hp, 0)
        self.assertEqual(sab.hp, 0)

        # 4. Dead saboteur rejection
        res_dead_sab = gs.sabotage(sab, target_b)
        self.assertFalse(res_dead_sab)

        # 5. Same-house sabotage rejection
        sab2 = Unit("Saboteur", "Atreides", 2, 2)
        friendly_b = Building("Barracks", "Atreides", 2, 3, hp=250)
        self.assertFalse(gs.sabotage(sab2, friendly_b))
        self.assertEqual(friendly_b.hp, 250)
        self.assertEqual(sab2.hp, 45)

        # 6. Out-of-range sabotage rejection (dist > 1)
        enemy_far_b = Building("Barracks", "Harkonnen", 5, 5, hp=250)
        self.assertFalse(gs.sabotage(sab2, enemy_far_b))
        self.assertEqual(enemy_far_b.hp, 250)
        self.assertEqual(sab2.hp, 45)

        # 7. Dead-target rejection
        enemy_dead_b = Building("Barracks", "Harkonnen", 2, 1, hp=0)
        self.assertFalse(gs.sabotage(sab2, enemy_dead_b))
        self.assertEqual(sab2.hp, 45)

    def test_unit_xp_from_attack(self):
        """test_unit_xp_from_attack: attacker gains XP equal to dmg, rank promotion at thresholds."""
        gs = GameState(GridMap(8, 8))
        attacker = Unit("Trike", "Atreides", 1, 1, hp=50)
        target = Unit("Trike", "Harkonnen", 1, 2, hp=50)
        gs.units.extend([attacker, target])

        # Attack with bullet vs heavy: 20 * 0.25 = 5 damage
        dmg = attacker.attack(target)
        self.assertEqual(dmg, 5)
        self.assertEqual(target.hp, 45)
        self.assertEqual(attacker.xp, 5)

        # Out-of-range attack gains 0 XP
        far_target = Unit("Trike", "Harkonnen", 7, 7, hp=50)
        gs.units.append(far_target)
        dmg_miss = attacker.attack(far_target)
        self.assertEqual(dmg_miss, 0)
        self.assertEqual(attacker.xp, 5)

        # Rank promotion via combat XP: give attacker 95 XP, next hit gives 5 XP -> total 105 -> rank 1
        attacker.xp = 95
        dmg2 = attacker.attack(target)
        self.assertEqual(dmg2, 5)
        self.assertEqual(attacker.xp, 100)
        self.assertEqual(attacker.rank, 1)

    def test_trade_spice(self):
        """test_trade_spice: buy/sell spice at 2/3 credits rate, capacity checks, multi-house."""
        gs = GameState(GridMap(8, 8))

        # 1. Buy 50 spice for Atreides: cost = 50 * 2 = 100 credits
        harv = Unit("Harvester", "Atreides", 1, 1)
        gs.units.append(harv)
        res_buy = gs.trade_spice("Atreides", 50, buy=True)
        self.assertEqual(res_buy, 50)
        self.assertEqual(gs.credits["Atreides"], 900)  # 1000 - 100
        self.assertEqual(gs.spice_carried["Atreides"], 50)
        self.assertEqual(harv.spice_carried, 50)

        # 2. Sell 30 spice for Atreides: gain = 30 * 3 = 90 credits
        res_sell = gs.trade_spice("Atreides", 30, buy=False)
        self.assertEqual(res_sell, 30)
        self.assertEqual(gs.credits["Atreides"], 990)  # 900 + 90
        self.assertEqual(gs.spice_carried["Atreides"], 20)
        self.assertEqual(harv.spice_carried, 20)

        # 3. Insufficient spice to sell -> returns 0, state unchanged
        res_fail_sell = gs.trade_spice("Atreides", 100, buy=False)
        self.assertEqual(res_fail_sell, 0)
        self.assertEqual(gs.credits["Atreides"], 990)
        self.assertEqual(gs.spice_carried["Atreides"], 20)

        # 4. Insufficient credits to buy -> returns 0, state unchanged
        gs.credits["Atreides"] = 10
        res_fail_buy = gs.trade_spice("Atreides", 50, buy=True)
        self.assertEqual(res_fail_buy, 0)
        self.assertEqual(gs.credits["Atreides"], 10)
        self.assertEqual(gs.spice_carried["Atreides"], 20)

        # 5. Exceeding max_spice_capacity (base=1000) -> returns 0, state unchanged
        gs.credits["Harkonnen"] = 5000
        res_cap = gs.trade_spice("Harkonnen", 1001, buy=True)
        self.assertEqual(res_cap, 0)
        self.assertEqual(gs.credits["Harkonnen"], 5000)
        self.assertEqual(gs.spice_carried["Harkonnen"], 0)

        # 6. Works for Ordos
        res_ordos = gs.trade_spice("Ordos", 100, buy=True)
        self.assertEqual(res_ordos, 100)
        self.assertEqual(gs.credits["Ordos"], 800)
        self.assertEqual(gs.spice_carried["Ordos"], 100)

        # 7. Unknown house returns 0 without modifying state
        res_unknown = gs.trade_spice("Corrino", 50, buy=True)
        self.assertEqual(res_unknown, 0)


if __name__ == "__main__":
    unittest.main()
