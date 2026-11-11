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

UNIT_COSTS: Dict[str, int] = {"Trike": 150, "CombatTank": 300, "Harvester": 400}

BUILDING_COSTS: Dict[str, int] = {"WindTrap": 200, "Refinery": 400, "Barracks": 250, "Silo": 150}


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

    def construct_building(self, house: str, building_type: str, x: int, y: int) -> Optional[Building]:
        cost = BUILDING_COSTS.get(building_type, 250)
        if self.credits.get(house, 0) < cost:
            return None
        self.credits[house] -= cost
        power_produced = 100 if building_type == "WindTrap" else 0
        power_consumed = 0 if building_type == "WindTrap" else 30
        b = Building(building_type=building_type, house=house, x=x, y=y, power_produced=power_produced, power_consumed=power_consumed)
        return self.place_building(b)

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
