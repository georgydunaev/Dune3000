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
