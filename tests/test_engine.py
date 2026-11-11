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
from dune3000.procgen import generate_building_svg, generate_terrain_svg, generate_unit_svg


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

    def test_train_unit(self):
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


if __name__ == "__main__":
    unittest.main()
