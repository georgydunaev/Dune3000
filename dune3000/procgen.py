"""Algorithmic procedural graphics generator for Dune 3000.
Generates lightweight deterministic SVG/pixel representations for terrain tiles,
buildings, units, and sandworms without external image assets.
"""
from typing import Dict


HOUSE_COLORS: Dict[str, str] = {
    "Atreides": "#2563eb",
    "Harkonnen": "#dc2626",
    "Ordos": "#16a34a",
}


TERRAIN_COLORS: Dict[str, str] = {
    "SAND": "#e5c07b",
    "DUNES": "#d19a66",
    "ROCK": "#5c6370",
    "CONCRETE": "#9ca3af",
    "SPICE_THIN": "#e06c75",
    "SPICE_THICK": "#be5046",
}


def generate_terrain_svg(terrain_type: str, size: int = 32, seed: int = 0) -> str:
    """Generates a deterministic algorithmic SVG tile for a terrain type."""
    base_color = TERRAIN_COLORS.get(terrain_type, "#e5c07b")
    cx = (seed * 7 + 11) % (size - 8) + 4
    cy = (seed * 13 + 5) % (size - 8) + 4
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="{base_color}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="2" fill="rgba(0,0,0,0.18)"/>'
        f'</svg>'
    )


def generate_building_svg(building_type: str, house: str, size: int = 32) -> str:
    """Generates a deterministic algorithmic SVG string for a building type.

    Args:
        building_type: One of "WindTrap", "Refinery", "ConstructionYard", "Silo".
        house: The house color key (e.g., "Atreides").
        size: SVG size in pixels (default 32).

    Returns:
        A valid SVG string.
    """
    color = HOUSE_COLORS.get(house, "#2563eb")
    half = size // 2
    quarter = size // 4

    if building_type == "WindTrap":
        # Diamond shape for WindTrap
        points = f"{half},{quarter} {size - quarter},{half} {half},{size - quarter} {quarter},{half}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{points}" fill="{color}"/>'
            f'</svg>'
        )
    elif building_type == "Refinery":
        # Rectangle with a cross pattern for Refinery
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{color}"/>'
            f'<rect x="0" y="0" width="{size}" height="{size}" fill="none" stroke="{color}" stroke-width="2"/>'
            f'</svg>'
        )
    elif building_type == "ConstructionYard":
        # Larger rectangle with internal pattern for ConstructionYard
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" height="{size - 2 * quarter}" fill="{color}"/>'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" height="{size - 2 * quarter}" fill="none" stroke="{color}" stroke-width="3"/>'
            f'</svg>'
        )
    elif building_type == "Silo":
        # Tall rectangle with a cap for Silo
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" height="{size - 3 * quarter}" fill="{color}"/>'
            f'<rect x="{half - 4}" y="{quarter}" width="8" height="{size - 3 * quarter}" fill="#1c1c1c"/>'
            f'</svg>'
        )
    else:
        # Default: rectangle for unknown building types
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" fill="{color}"/>'
            f'</svg>'
        )


def generate_unit_svg(unit_type: str, house: str, size: int = 32) -> str:
    """Generates an SVG string for a unit type with house color and geometric shape.

    Args:
        unit_type: One of "Harvester", "Trike", "CombatTank".
        house: The house color key (e.g., "Atreides").
        size: SVG size in pixels (default 32).

    Returns:
        A valid SVG string.
    """
    color = HOUSE_COLORS.get(house, "#2563eb")
    half = size // 2
    quarter = size // 4

    if unit_type == "Harvester":
        # Diamond shape for Harvester
        points = f"{half},{quarter} {size - quarter},{half} {half},{size - quarter} {quarter},{half}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{points}" fill="{color}"/>'
            f'</svg>'
        )
    elif unit_type == "Trike":
        # Triangle shape for Trike (pointing right)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{half},{quarter} {quarter},{half} {half},{size - quarter}" fill="{color}"/>'
            f'</svg>'
        )
    elif unit_type == "CombatTank":
        # Rectangle shape for CombatTank
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" height="{size - 2 * quarter}" fill="{color}"/>'
            f'</svg>'
        )
    else:
        # Default: diamond shape for unknown unit types
        points = f"{half},{quarter} {size - quarter},{half} {half},{size - quarter} {quarter},{half}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{points}" fill="{color}"/>'
            f'</svg>'
        )