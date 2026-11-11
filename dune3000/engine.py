"""
Core RTS mechanics for Dune 3000 (inspired by Dune 2000).
Designed for zero external dependencies and fast deterministic unit testing.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SAND = "SAND"
DUNES = "DUNES"
ROCK = "ROCK"
CONCRETE = "CONCRETE"
SPICE_THIN = "SPICE_THIN"
SPICE_THICK = "SPICE_THICK"

HOUSES = ("Atreides", "Harkonnen", "Ordos")

UNIT_COSTS: Dict[str, int] = {"Trike": 150, "CombatTank": 300, "Harvester": 400, "Engineer": 200}

BUILDING_COSTS: Dict[str, int] = {"WindTrap": 200, "Refinery": 400, "Barracks": 250, "Silo": 150, "Starport": 500, "Palace": 600, "GunTurret": 250, "RocketTurret": 350}

# Signature special vehicle of each Great House (spawned via GameState.spawn_special_unit).
HOUSE_SPECIAL_UNITS: Dict[str, Dict] = {
    "Atreides": {
        "unit_type": "SonicTank",
        "hp": 130,
        "max_hp": 130,
        "attack_damage": 45,
        "attack_range": 4,
        "weapon_type": "shell",
        "armor_type": "heavy",
    },
    "Harkonnen": {
        "unit_type": "Devastator",
        "hp": 220,
        "max_hp": 220,
        "attack_damage": 55,
        "attack_range": 3,
        "weapon_type": "shell",
        "armor_type": "heavy",
    },
    "Ordos": {
        "unit_type": "Deviator",
        "hp": 110,
        "max_hp": 110,
        "attack_damage": 35,
        "attack_range": 4,
        "weapon_type": "missile",
        "armor_type": "heavy",
    },
}

SPECIAL_UNIT_COST: int = 300


@dataclass
class Building:
    building_type: str
    house: str
    x: int
    y: int
    hp: int = 400
    max_hp: int = 400
    power_produced: int = 0
    power_consumed: int = 0


@dataclass
class Unit:
    unit_type: str
    house: str
    x: int
    y: int
    hp: int = 100
    max_hp: int = 100
    spice_carried: int = 0
    max_spice: int = 700
    weapon_type: str = "bullet"
    armor_type: str = "heavy"
    attack_damage: int = 20
    attack_range: int = 3
    xp: int = 0
    rank: int = 0

    def move_towards(self, target_x: int, target_y: int, game_map: "GridMap") -> Tuple[int, int]:
        """
        Move one step towards the target position.

        Movement order:
        1. Move along X axis towards target_x (1 tile step).
        2. If X didn't change, move along Y axis towards target_y (1 tile step).
        3. Clamp resulting coordinates to game_map bounds.
        4. Update self.x and self.y, return the new position.
        """
        # Step 1: Move along X axis
        if self.x < target_x:
            nx = self.x + 1
        elif self.x > target_x:
            nx = self.x - 1
        else:
            nx = self.x

        # Step 2: Move along Y axis only if X didn't change
        if nx != self.x:
            ny = self.y
        elif self.y < target_y:
            ny = self.y + 1
        elif self.y > target_y:
            ny = self.y - 1
        else:
            ny = self.y

        # Step 3: Clamp to game_map bounds
        nx = max(0, min(game_map.width - 1, nx))
        ny = max(0, min(game_map.height - 1, ny))

        # Step 4: Update and return
        self.x = nx
        self.y = ny
        return (self.x, self.y)

    def gain_xp(self, amount: int) -> int:
        """
        Gain experience and promote rank if thresholds met.

        - Increases self.xp by max(0, amount).
        - When self.xp >= 100 and self.rank < 1, promotes to rank 1 and increases attack_damage by 5.
        - When self.xp >= 250 and self.rank < 2, promotes to rank 2 and increases attack_damage by additional 5 (total +10 over base if jumping from rank 0 to rank 2).

        Returns self.rank.
        """
        self.xp += max(0, amount)
        if self.xp >= 250 and self.rank < 2:
            self.rank = 2
            self.attack_damage += 5
        if self.xp >= 100 and self.rank < 1:
            self.rank = 1
            self.attack_damage += 5
        return self.rank


    def step_harvest(self, game_map: "GridMap", refinery: Optional[Building], game_state: "GameState") -> int:
        """
        Harvests spice from the current tile or unloads at the refinery.
        Returns credits deposited on this step.
        """
        if refinery and (self.x, self.y) == (refinery.x, refinery.y) and self.spice_carried > 0:
            deposited = self.spice_carried
            self.spice_carried = 0
            game_state.add_credits(self.house, deposited)
            return deposited

        if self.spice_carried >= self.max_spice:
            return 0

        tile = game_map.get_tile(self.x, self.y)
        room = self.max_spice - self.spice_carried
        if tile == SPICE_THICK:
            extracted = min(100, room)
            self.spice_carried += extracted
            game_map.set_tile(self.x, self.y, SPICE_THIN)
        elif tile == SPICE_THIN:
            extracted = min(50, room)
            self.spice_carried += extracted
            game_map.set_tile(self.x, self.y, SAND)
        return 0

    def attack(self, target) -> int:
        """
        Attack the target unit.

        If attacker or target has hp <= 0, returns 0.
        If target is out of range (Manhattan distance > attack_range), returns 0.
        Otherwise, computes damage and reduces target's hp.
        """
        if self.hp <= 0 or target.hp <= 0:
            return 0

        dist = abs(self.x - target.x) + abs(self.y - target.y)
        if dist > self.attack_range:
            return 0

        target_armor = getattr(target, "armor_type", "building")
        dmg = compute_damage(self.weapon_type, target_armor, self.attack_damage)
        target.hp = max(0, target.hp - dmg)
        return dmg


@dataclass
class Sandworm:
    x: int
    y: int

    def find_nearest_target(self, units: List[Unit], game_map: "GridMap") -> Optional[Unit]:
        """Finds the nearest unit on sand/dunes/spice tiles (units on ROCK/CONCRETE are safe)."""
        safe_tiles = {ROCK, CONCRETE}
        best_unit: Optional[Unit] = None
        best_dist = 10**9
        for u in units:
            if u.hp <= 0:
                continue
            if game_map.get_tile(u.x, u.y) in safe_tiles:
                continue
            dist = abs(self.x - u.x) + abs(self.y - u.y)
            if dist < best_dist:
                best_dist = dist
                best_unit = u
        return best_unit

    def step(self, game_state: "GameState") -> Optional[Unit]:
        """Move towards the nearest vulnerable unit and devour if adjacent.

        1. Find the nearest vulnerable unit via find_nearest_target.
        2. If no target, return None.
        3. Move 1 step closer in X then Y direction.
        4. If adjacent after moving, devour the unit (set hp=0, remove from units, return target).
        5. Otherwise return None.
        """
        target = self.find_nearest_target(game_state.units, game_state.game_map)
        if target is None:
            return None

        # Move 1 step closer
        if self.x < target.x:
            self.x += 1
        elif self.x > target.x:
            self.x -= 1
        elif self.y < target.y:
            self.y += 1
        elif self.y > target.y:
            self.y -= 1

        # Devour if adjacent
        if (self.x, self.y) == (target.x, target.y):
            target.hp = 0
            if target in game_state.units:
                game_state.units.remove(target)
            return target

        return None


class GridMap:
    def __init__(self, width: int = 16, height: int = 16, default_tile: str = SAND):
        self.width = width
        self.height = height
        self.tiles: List[List[str]] = [
            [default_tile for _ in range(width)] for _ in range(height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> str:
        if not self.in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile_type: str) -> None:
        if not self.in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        self.tiles[y][x] = tile_type


@dataclass
class GameState:
    game_map: GridMap = field(default_factory=GridMap)
    tick_count: int = 0
    credits: Dict[str, int] = field(default_factory=lambda: {h: 1000 for h in HOUSES})
    buildings: List[Building] = field(default_factory=list)
    units: List[Unit] = field(default_factory=list)
    sandworms: List[Sandworm] = field(default_factory=list)

    def add_credits(self, house: str, amount: int) -> int:
        self.credits[house] = self.credits.get(house, 0) + int(amount)
        return self.credits[house]

    def power_balance(self, house: str) -> Tuple[int, int]:
        produced = sum(b.power_produced for b in self.buildings if b.house == house and b.hp > 0)
        consumed = sum(b.power_consumed for b in self.buildings if b.house == house and b.hp > 0)
        return produced, consumed

    def power_efficiency(self, house: str) -> float:
        produced, consumed = self.power_balance(house)
        if consumed <= 0 or produced >= consumed:
            return 1.0
        return max(0.25, round(produced / consumed, 4))

    def compute_visibility(self, house: str) -> set:
        """Compute the fog of war / sight radius visibility for a given house.

        Every alive (hp > 0) building owned by house reveals all in-bounds tiles
        (tx, ty) with Manhattan distance abs(b.x - tx) + abs(b.y - ty) <= 4.

        Every alive (hp > 0) unit owned by house reveals all in-bounds tiles
        (tx, ty) with Manhattan distance abs(u.x - tx) + abs(u.y - ty) <= 3.

        Returns a set of (x, y) integer coordinate tuples that are in bounds on
        self.game_map.
        """
        visible: set = set()
        for b in self.buildings:
            if b.house == house and b.hp > 0:
                for tx in range(self.game_map.width):
                    for ty in range(self.game_map.height):
                        if abs(b.x - tx) + abs(b.y - ty) <= 4 and self.game_map.in_bounds(tx, ty):
                            visible.add((tx, ty))
        for u in self.units:
            if u.house == house and u.hp > 0:
                for tx in range(self.game_map.width):
                    for ty in range(self.game_map.height):
                        if abs(u.x - tx) + abs(u.y - ty) <= 3 and self.game_map.in_bounds(tx, ty):
                            visible.add((tx, ty))
        return visible

    def spawn_special_unit(self, house: str, x: int, y: int) -> Optional[Unit]:
        """Spawn the house's signature special unit.

        Costs 300 credits. If the house has insufficient credits or is not in
        HOUSE_SPECIAL_UNITS, returns None.

        Otherwise deducts 300 credits, creates the special Unit at (x, y) with
        the house's configured stats, appends it to self.units, and returns it.
        """
        if self.credits.get(house, 0) < SPECIAL_UNIT_COST or house not in HOUSE_SPECIAL_UNITS:
            return None
        
        spec = HOUSE_SPECIAL_UNITS[house]
        unit = Unit(
            unit_type=spec["unit_type"],
            house=house,
            x=x,
            y=y,
            hp=spec["hp"],
            max_hp=spec["max_hp"],
            attack_damage=spec["attack_damage"],
            attack_range=spec["attack_range"],
            weapon_type=spec["weapon_type"],
            armor_type=spec["armor_type"],
        )
        self.credits[house] = self.credits.get(house, 0) - SPECIAL_UNIT_COST
        self.units.append(unit)
        return unit

    def check_winner(self) -> Optional[str]:
        """Check if the game has a winner or a draw.

        Returns:
            The name of the winning house if only one house has alive buildings/units,
            "Draw" if no houses have any alive buildings or units,
            None if two or more houses still have alive buildings/units.
        """
        active_houses: set[str] = set()
        for b in self.buildings:
            if b.hp > 0:
                active_houses.add(b.house)
        for u in self.units:
            if u.hp > 0:
                active_houses.add(u.house)

        if len(active_houses) == 1:
            return next(iter(active_houses))
        elif len(active_houses) == 0:
            return "Draw"
        else:
            return None

    def max_spice_capacity(self, house: str) -> int:
        """Calculate maximum spice capacity for a house.
        
        Base capacity is 1000.
        Each alive (hp > 0) Refinery owned by house adds 1000.
        Each alive (hp > 0) Silo owned by house adds 1000.
        """
        capacity = 1000
        for b in self.buildings:
            if b.house == house and b.hp > 0:
                if b.building_type == "Refinery":
                    capacity += 1000
                elif b.building_type == "Silo":
                    capacity += 1000
        return capacity

    def place_building(self, building: Building) -> Building:
        tile = self.game_map.get_tile(building.x, building.y)
        if tile == CONCRETE:
            building.hp = building.max_hp
        elif tile == ROCK:
            building.hp = max(1, building.max_hp // 2)
        self.buildings.append(building)
        return building

    def train_unit(self, house: str, unit_type: str, x: int, y: int) -> Optional[Unit]:
        cost = UNIT_COSTS.get(unit_type, 200)
        if self.credits.get(house, 0) < cost:
            return None
        self.credits[house] -= cost
        unit = Unit(unit_type=unit_type, house=house, x=x, y=y)
        self.units.append(unit)
        return unit

    def order_starport_unit(self, house: str, unit_type: str, x: int, y: int) -> Optional[Unit]:
        """Order a unit from the CHOAM Starport at dynamically fluctuating market prices.

        The price depends on the current game tick:
        - Even ticks: 20% discount (price = int(base * 0.8))
        - Odd ticks: 20% price surge (price = int(base * 1.2))

        Returns None if the house doesn't own a Starport, has insufficient credits,
        or the unit type is unknown.

        Otherwise deducts the price from self.credits[house], creates a Unit,
        appends it to self.units, and returns the created unit.
        """
        # Check if house owns at least one alive Starport building
        has_starport = any(
            b.building_type == "Starport" and b.house == house and b.hp > 0
            for b in self.buildings
        )
        if not has_starport:
            return None

        # Compute base cost and dynamic CHOAM price
        base = UNIT_COSTS.get(unit_type, 200)
        if self.tick_count % 2 == 0:
            price = int(base * 0.8)  # 20% discount on even ticks
        else:
            price = int(base * 1.2)  # 20% surge on odd ticks

        # Check if house has enough credits
        if self.credits.get(house, 0) < price:
            return None

        # Deduct price, create unit, append to units
        self.credits[house] -= price
        unit = Unit(unit_type=unit_type, house=house, x=x, y=y)
        self.units.append(unit)
        return unit

    def step_carryall_rescue(self, house: str) -> int:
        """Airlift spice harvesters in peril back to the nearest refinery.

        If no alive Refinery exists for house or power_efficiency(house) < 0.5,
        no rescue can be performed and 0 is returned.
        Otherwise, for each alive Harvester within Manhattan distance <= 2 of any
        sandworm, teleports/airlifts the Harvester to the Refinery's tile.
        """
        refinery: Optional[Building] = None
        for b in self.buildings:
            if b.house == house and b.building_type == "Refinery" and b.hp > 0:
                refinery = b
                break

        if refinery is None or self.power_efficiency(house) < 0.5:
            return 0

        rescued = 0
        for u in self.units:
            if u.hp > 0 and u.house == house and u.unit_type == "Harvester":
                if (u.x, u.y) == (refinery.x, refinery.y):
                    continue
                in_danger = False
                for w in self.sandworms:
                    if abs(u.x - w.x) + abs(u.y - w.y) <= 2:
                        in_danger = True
                        break
                if in_danger:
                    u.x = refinery.x
                    u.y = refinery.y
                    rescued += 1

        return rescued

    def spawn_special_unit(self, house: str, x: int, y: int) -> Optional[Unit]:
        """Spawn the house's signature special unit for SPECIAL_UNIT_COST credits.

        Returns None (without spending credits) if the house is unknown to
        HOUSE_SPECIAL_UNITS or has fewer than SPECIAL_UNIT_COST credits.
        Otherwise deducts the cost, appends the configured Unit at (x, y) to
        self.units, and returns it.
        """
        spec = HOUSE_SPECIAL_UNITS.get(house)
        if spec is None or self.credits.get(house, 0) < SPECIAL_UNIT_COST:
            return None
        self.credits[house] -= SPECIAL_UNIT_COST
        unit = Unit(
            unit_type=spec["unit_type"],
            house=house,
            x=x,
            y=y,
            hp=spec["hp"],
            max_hp=spec["max_hp"],
            weapon_type=spec["weapon_type"],
            armor_type=spec["armor_type"],
            attack_damage=spec["attack_damage"],
            attack_range=spec["attack_range"],
        )
        self.units.append(unit)
        return unit

    def step_ai_commander(self, house: str) -> str:
        """AI commander step: spend excess credits to reinforce army or direct combat units.

        If the house has at least 200 credits and owns at least one alive building,
        deduct 200 credits, spawn a CombatTank at the first alive building's position,
        append it to self.units, and return "spawned_tank".

        Otherwise, find all alive combat units (unit_type != "Harvester") owned by house
        and move each one 1 step toward the nearest alive enemy unit or building.
        Return "advanced_units" if at least one unit moved, or "idle" otherwise.
        """
        # If house has enough credits and at least one alive building, spawn a tank
        if self.credits.get(house, 0) >= 200:
            alive_buildings = [b for b in self.buildings if b.house == house and b.hp > 0]
            if alive_buildings:
                b = alive_buildings[0]
                self.credits[house] = self.credits.get(house, 0) - 200
                tank = Unit(
                    unit_type="CombatTank",
                    house=house,
                    x=b.x,
                    y=b.y,
                    hp=120,
                    max_hp=120,
                    weapon_type="shell",
                    armor_type="heavy",
                    attack_damage=25,
                    attack_range=3,
                )
                self.units.append(tank)
                return "spawned_tank"

        # Otherwise: move combat units toward nearest enemy
        combat_units = [
            u for u in self.units
            if u.house == house and u.hp > 0 and u.unit_type != "Harvester"
        ]

        if not combat_units:
            return "idle"

        moved_any = False
        for unit in combat_units:
            # Save position before moving
            old_x, old_y = unit.x, unit.y

            # Find nearest alive enemy unit or building
            nearest_dist = 10**9
            nearest_target = None

            # Check enemy units
            for other in self.units:
                if other.house != house and other.hp > 0:
                    dist = abs(unit.x - other.x) + abs(unit.y - other.y)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_target = other

            # Check enemy buildings
            for b in self.buildings:
                if b.house != house and b.hp > 0:
                    dist = abs(unit.x - b.x) + abs(unit.y - b.y)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_target = b

            # Move toward the nearest target
            if nearest_target is not None:
                unit.move_towards(nearest_target.x, nearest_target.y, self.game_map)
                if unit.x != old_x or unit.y != old_y:
                    moved_any = True

        if moved_any:
            return "advanced_units"
        return "idle"

    def construct_building(self, house: str, building_type: str, x: int, y: int) -> Optional[Building]:
        cost = BUILDING_COSTS.get(building_type, 250)
        if self.credits.get(house, 0) < cost:
            return None
        self.credits[house] -= cost
        power_produced = 100 if building_type == "WindTrap" else 0
        power_consumed = 0 if building_type == "WindTrap" else 30
        b = Building(building_type=building_type, house=house, x=x, y=y, power_produced=power_produced, power_consumed=power_consumed)
        return self.place_building(b)

    def repair_building(self, building: Building, max_hp_to_restore: int = 50) -> int:
        """Repair a building by spending spice credits.

        Each 1 credit restores up to 2 HP.
        If the building's house has fewer credits than needed,
        only restore available_credits * 2 HP and spend available_credits.

        Args:
            building: The building to repair.
            max_hp_to_restore: Maximum HP to attempt to restore (default 50).

        Returns:
            The actual HP restored (int).
        """
        # Early return conditions
        if building.hp <= 0 or building.hp >= building.max_hp or max_hp_to_restore <= 0:
            return 0

        # Calculate missing HP (capped by max_hp_to_restore)
        missing = min(building.max_hp - building.hp, max_hp_to_restore)

        # Each 1 credit restores up to 2 HP
        cost = (missing + 1) // 2

        # Available credits for this house
        available_credits = self.credits.get(building.house, 0)

        if available_credits < cost:
            # Not enough credits for full repair: restore available_credits * 2 HP
            actual_restore = min(available_credits * 2, missing)
            actual_cost = available_credits
        else:
            # Full repair possible
            actual_restore = missing
            actual_cost = cost

        # Deduct credits
        self.credits[building.house] = available_credits - actual_cost

        # Increase HP, clamped to max_hp
        building.hp = min(building.max_hp, building.hp + actual_restore)

        return actual_restore

    def detonate_spice_bloom(self, x: int, y: int) -> int:
        """Detonate a spice bloom at tile (x, y).

        Converts the center tile to SPICE_THICK (unless it is ROCK or
        CONCRETE, which are left untouched) and every in-bounds orthogonal
        neighbor (4-directional) whose tile is SAND or DUNES to SPICE_THIN.

        Returns:
            The total number of tiles modified (int). Out-of-bounds
            detonations modify nothing and return 0.
        """
        if not self.game_map.in_bounds(x, y):
            return 0

        modified = 0

        center = self.game_map.get_tile(x, y)
        if center not in (ROCK, CONCRETE):
            self.game_map.set_tile(x, y, SPICE_THICK)
            modified += 1

        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not self.game_map.in_bounds(nx, ny):
                continue
            if self.game_map.get_tile(nx, ny) in (SAND, DUNES):
                self.game_map.set_tile(nx, ny, SPICE_THIN)
                modified += 1

        return modified

    def fire_death_hand(self, house: str, target_x: int, target_y: int) -> int:
        """Fire the Palace superweapon Death Hand missile at (target_x, target_y).

        Requires the house to own at least one alive (hp > 0) Palace building;
        otherwise nothing is fired and 0 is returned.

        Splash damage is applied to every alive enemy unit and building based on
        Manhattan distance from the impact point:
            dist == 0 -> 150 damage
            dist == 1 -> 75 damage

        Returns the total actual damage dealt across all hit enemy units and
        buildings (each hit's actual damage is min(target.hp, listed damage)).
        """
        has_palace = any(
            b.building_type == "Palace" and b.house == house and b.hp > 0
            for b in self.buildings
        )
        if not has_palace:
            return 0

        total_damage = 0
        for obj in self.units + self.buildings:
            if obj.house == house or obj.hp <= 0:
                continue
            dist = abs(obj.x - target_x) + abs(obj.y - target_y)
            if dist == 0:
                damage = 150
            elif dist == 1:
                damage = 75
            else:
                continue
            actual = min(obj.hp, damage)
            obj.hp -= actual
            total_damage += actual
        return total_damage

    def step_turrets(self) -> int:
        """Execute automated defensive fire for all alive GunTurret and RocketTurret buildings.

        - GunTurret: range 3, damage 30 (fires regardless of power level).
        - RocketTurret: range 5, damage 45 (requires full power_efficiency >= 1.0).

        For each turret, finds the first alive enemy unit within Manhattan distance <= rng,
        deals min(u.hp, dmg) damage, and returns the total damage dealt across all turrets.
        """
        total_damage = 0
        for b in self.buildings:
            if b.hp <= 0:
                continue
            if b.building_type == "GunTurret":
                rng = 3
                dmg = 30
            elif b.building_type == "RocketTurret":
                if self.power_efficiency(b.house) < 1.0:
                    continue
                rng = 5
                dmg = 45
            else:
                continue

            for u in self.units:
                if u.hp > 0 and u.house != b.house:
                    dist = abs(u.x - b.x) + abs(u.y - b.y)
                    if dist <= rng:
                        actual = min(u.hp, dmg)
                        u.hp -= actual
                        total_damage += actual
                        break

        return total_damage

    def sell_building(self, building: Building) -> int:
        """Sell a structure to recover up to 50% credit refund proportional to HP.

        If building not in self.buildings or building.hp <= 0, returns 0.
        Otherwise computes refund = max(1, int((cost * building.hp) // (2 * building.max_hp))),
        sets building.hp = 0, removes it from self.buildings, refunds credits via self.add_credits,
        and returns the refund amount.
        """
        if building not in self.buildings or building.hp <= 0:
            return 0
        cost = BUILDING_COSTS.get(building.building_type, 250)
        refund = max(1, int((cost * building.hp) // (2 * building.max_hp)))
        building.hp = 0
        self.buildings.remove(building)
        self.add_credits(building.house, refund)
        return refund

    def capture_building(self, unit: Unit, building: Building) -> bool:
        """Capture an adjacent enemy building using an Engineer infantry unit.

        Returns False if:
        - unit is not an Engineer
        - unit is dead (hp <= 0)
        - building is dead (hp <= 0)
        - unit and building belong to the same house
        - Manhattan distance between unit and building > 1

        Otherwise:
        - switches building.house to unit.house
        - heals building up to 100 HP (clamped at max_hp)
        - consumes the Engineer (sets unit.hp = 0, removes from self.units)
        - returns True
        """
        if (
            unit.unit_type != "Engineer"
            or unit.hp <= 0
            or building.hp <= 0
            or unit.house == building.house
            or abs(unit.x - building.x) + abs(unit.y - building.y) > 1
        ):
            return False

        building.house = unit.house
        building.hp = min(building.max_hp, building.hp + 100)
        unit.hp = 0
        if unit in self.units:
            self.units.remove(unit)
        return True

    def apply_sandstorm(self, center_x: int, center_y: int, radius: int = 2) -> int:
        """Simulate a Coriolis sandstorm centered at (center_x, center_y).

        Deals 15 damage to every alive unit within Manhattan distance <= radius
        located on exposed terrain (not on ROCK or CONCRETE).
        Returns the number of units damaged.
        """
        damaged_count = 0
        for u in self.units:
            if u.hp > 0:
                if abs(u.x - center_x) + abs(u.y - center_y) <= radius:
                    tile = self.game_map.get_tile(u.x, u.y)
                    if tile not in (ROCK, CONCRETE):
                        u.hp = max(0, u.hp - 15)
                        damaged_count += 1
        return damaged_count

    def to_dict(self) -> Dict:
        """Serialize the game state to a dictionary for JSON snapshot.
        
        Returns:
            Dict with keys: width, height, tiles, credits, buildings, units, sandworms.
        """
        return {
            "width": self.game_map.width,
            "height": self.game_map.height,
            "tiles": self.game_map.tiles,
            "credits": dict(self.credits),
            "buildings": [
                {
                    "building_type": b.building_type,
                    "house": b.house,
                    "x": b.x,
                    "y": b.y,
                    "hp": b.hp,
                    "max_hp": b.max_hp,
                }
                for b in self.buildings
            ],
            "units": [
                {
                    "unit_type": u.unit_type,
                    "house": u.house,
                    "x": u.x,
                    "y": u.y,
                    "hp": u.hp,
                    "max_hp": u.max_hp,
                    "spice_carried": u.spice_carried,
                }
                for u in self.units
            ],
            "sandworms": [
                {"x": w.x, "y": w.y}
                for w in self.sandworms
            ],
        }

    def step_tick(self) -> Dict[str, int]:
        """Execute one simulation tick step.
        
        - Increment tick counter.
        - Remove destroyed buildings and units.
        - Process harvester spice deposition at refineries.
        - Return tick state summary.
        """
        self.tick_count += 1
        
        # Remove destroyed buildings
        self.buildings = [b for b in self.buildings if b.hp > 0]
        
        # Remove destroyed units
        self.units = [u for u in self.units if u.hp > 0]
        
        # Process harvester spice deposition
        total_deposited = 0
        for u in self.units:
            if u.unit_type == "Harvester":
                # Find the first refinery matching the harvester's house
                refinery = None
                for b in self.buildings:
                    if b.house == u.house and b.building_type == "Refinery":
                        refinery = b
                        break
                # Call step_harvest and accumulate deposited spice
                if refinery is not None:
                    deposited = u.step_harvest(self.game_map, refinery, self)
                    total_deposited += deposited
        
        return {
            "tick": self.tick_count,
            "spice_deposited": total_deposited,
            "alive_units": len(self.units),
            "alive_buildings": len(self.buildings),
        }


def compute_damage(weapon_type: str, armor_type: str, base_damage: int) -> int:
    """Compute damage with Rock-Paper-Scissors weapon vs armor multipliers.

    Multipliers:
        bullet vs infantry: 1.5
        bullet vs heavy: 0.25
        shell vs heavy: 1.25
        missile vs building: 1.5
    All other combinations: 1.0

    Returns max(1, int(round(base_damage * multiplier))).
    Uses standard mathematical rounding (round half up).
    """
    multipliers = {
        ("bullet", "infantry"): 1.5,
        ("bullet", "heavy"): 0.25,
        ("shell", "heavy"): 1.25,
        ("missile", "building"): 1.5,
    }
    multiplier = multipliers.get((weapon_type, armor_type), 1.0)
    # Standard rounding: add 0.5 and truncate for positive values
    result = int(base_damage * multiplier + 0.5)
    return max(1, result)
