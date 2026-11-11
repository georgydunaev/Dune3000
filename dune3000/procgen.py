"""Algorithmic procedural graphics generator for Dune 3000.
Generates lightweight deterministic SVG/pixel representations for terrain tiles,
buildings, units, and sandworms without external image assets.
"""
import math
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


def generate_explosion_svg(size: int = 32, frame: int = 0) -> str:
    """Generates a multi-layer combat explosion/fireball SVG.

    Args:
        size: SVG size in pixels (default 32).
        frame: Animation frame for deterministic radius variation.

    Returns:
        A valid SVG string depicting a multi-layer explosion.
    """
    # Explosion color palette
    core_color = "#ff4500"  # red-orange core
    mid_color = "#f59e0b"   # orange mid-layer
    outer_color = "#fef08a" # yellow outer layer

    # Deterministic radius variation based on frame
    # Core radius oscillates, mid and outer expand gradually
    core_radius = 8 + (frame % 4) * 2      # 8, 10, 12, 10, 8, ...
    mid_radius = 14 + (frame % 3) * 3      # 14, 17, 20, 14, 17, 20, ...
    outer_radius = 20 + (frame % 5) * 2    # 20, 22, 24, 26, 28, 20, ...

    # Offset based on frame for animation effect
    offset = (frame * 3) % size

    half = size // 2
    quarter = size // 4

    # Layered circles: outer first (draw order bottom to top)
    parts = [
        # Outer layer - largest, most transparent
        f'<circle cx="{half + offset}" cy="{half + offset}" r="{outer_radius}" '
        f'fill="{outer_color}" opacity="0.4"/>',
        # Mid layer
        f'<circle cx="{half + offset}" cy="{half + offset}" r="{mid_radius}" '
        f'fill="{mid_color}" opacity="0.6"/>',
        # Core layer - brightest
        f'<circle cx="{half + offset}" cy="{half + offset}" r="{core_radius}" '
        f'fill="{core_color}" opacity="0.8"/>',
        # Additional spark particles
    ]
    # Add concentric smaller circles for spark effect
    for i in range(1, (frame % 4) + 2):
        spark_r = 2 + i
        spark_x = half + offset + (i * 3 + frame) % (size - 8) - 3
        spark_y = half + offset + (i * 5 + frame * 2) % (size - 8) - 3
        parts.append(
            f'<circle cx="{spark_x}" cy="{spark_y}" r="{spark_r}" '
            f'fill="{core_color}" opacity="0.9"/>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'{ "".join(parts) }'
        f'</svg>'
    )


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


def _unit_shadow_svg(size: int) -> str:
    """Helper: drop shadow polygon/rect for units."""
    half = size // 2
    quarter = size // 4
    return (
        f'<polygon points="{half},{half + quarter} {size - quarter},{half + quarter} '
        f'{size - quarter + 2},{half + quarter - 4} {half + 2},{half + quarter - 8} '
        f'fill="rgba(0,0,0,0.15)"/>'
    )


def _unit_metallic_gradient_base(unit_type: str, size: int, color: str) -> str:
    """Helper: metallic base shine for units."""
    half = size // 2
    quarter = size // 4
    if unit_type == "Harvester":
        # Diamond with top highlight
        return (
            f'<polygon points="{half},{quarter} {size - quarter},{half} '
            f'{half},{size - quarter} {quarter},{half}" '
            f'fill="{color}" fill-opacity="0.8"/>'
            f'<polygon points="{half - 2},{quarter + 2} {size - quarter - 2},{half + 2} '
            f'{half - 2},{size - quarter - 2} {quarter + 2},{half + 2}" '
            f'fill="white" fill-opacity="0.3"/>'
        )
    elif unit_type == "Trike":
        # Triangle with side highlight
        return (
            f'<polygon points="{half},{quarter} {quarter},{half} {half},{size - quarter}" '
            f'fill="{color}" fill-opacity="0.8"/>'
            f'<polygon points="{half - 3},{quarter + 3} {quarter - 3},{half - 3} '
            f'{half + 3},{size - quarter - 3}" fill="white" fill-opacity="0.2"/>'
        )
    elif unit_type == "CombatTank":
        # Rectangle with top highlight strip
        return (
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" '
            f'height="{size - 2 * quarter}" fill="{color}" fill-opacity="0.8"/>'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" '
            f'height="4" fill="white" fill-opacity="0.3"/>'
        )
    else:
        return (
            f'<polygon points="{half},{quarter} {size - quarter},{half} '
            f'{half},{size - quarter} {quarter},{half}" fill="{color}" fill-opacity="0.8"/>'
        )


def generate_sandworm_svg(size: int = 32) -> str:
    """Generate an SVG string for an Arrakis sandworm mouth sprite.

    The sprite is fully geometric and algorithmic: a dark sandy outer mandible
    (the sandworm's open mouth cross-section) with a near-black inner maw,
    surrounded by a gold tooth ring of radial spikes, and a metallic sandworm
    texture base for depth. No assets are loaded.

    Args:
        size: SVG size in pixels (default 32).

    Returns:
        A valid multi-layer SVG string with ``width="{size}"`` and
        ``height="{size}"``.

    generated-by: groq/qwen/qwen3.8-27b (Tier 1)
    """
    half = size // 2
    quarter = size // 4

    # Large outer mandible: the sandworm's open mouth cross-section.
    mandible = (
        f'<circle cx="{half}" cy="{half}" r="{half - 1}" '
        f'fill="#5c4027" stroke="#1a130b" stroke-width="1"/>'
    )
    # Inner maw: the dark throat the prey is swallowed into.
    maw = (
        f'<circle cx="{half}" cy="{half}" r="{quarter}" '
        f'fill="#140802" stroke="#3d2b16" stroke-width="1"/>'
    )
    # Teeth ring: a full 360-degree band of radial spikes between the
    # maw (inner radius) and the mandible (outer radius).
    def _px(size_, cx, r, angle):
        return round(cx + r * math.cos(math.radians(angle)), 2)

    def _py(size_, cy, r, angle):
        return round(cy + r * math.sin(math.radians(angle)), 2)

    teeth = []
    for i in range(8):
        angle = i * 45
        x2 = _px(size, half, quarter, angle)
        y2 = _py(size, half, quarter, angle)
        x1 = _px(size, half, half - 1, angle)
        y1 = _py(size, half, half - 1, angle)
        teeth.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                     f'stroke="#e6c88c" stroke-width="2"/>')
    teeth_ring = "".join(teeth)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'{_unit_metallic_gradient_base("Sandworm", size, "#5c4027")}'
        f'{mandible}'
        f'{teeth_ring}'
        f'{maw}'
        f'{_unit_shadow_svg(size)}'
        f'</svg>'
    )


def generate_unit_svg(unit_type: str, house: str, size: int = 32) -> str:
    """Generates an SVG string for a unit type with house color and geometric shape.

    Args:
        unit_type: One of "Harvester", "Trike", "CombatTank".
        house: The house color key (e.g., "Atreides").
        size: SVG size in pixels (default 32).

    Returns:
        A valid SVG string with multi-layer design.
    """
    color = HOUSE_COLORS.get(house, "#2563eb")
    half = size // 2
    quarter = size // 4

    if unit_type == "Harvester":
        # Diamond shape for Harvester with multi-layer sub-elements
        points = f"{half},{quarter} {size - quarter},{half} {half},{size - quarter} {quarter},{half}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{points}" fill="{color}" fill-opacity="0.9"/>'
            f'{_unit_shadow_svg(size)}'
            f'{_unit_metallic_gradient_base("Harvester", size, color)}'
            f'</svg>'
        )
    elif unit_type == "Trike":
        # Triangle shape for Trike (pointing right) with multi-layer sub-elements
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{half},{quarter} {quarter},{half} {half},{size - quarter}" '
            f'fill="{color}" fill-opacity="0.9"/>'
            f'{_unit_shadow_svg(size)}'
            f'{_unit_metallic_gradient_base("Trike", size, color)}'
            f'</svg>'
        )
    elif unit_type == "CombatTank":
        # Rectangle shape for CombatTank with multi-layer sub-elements
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'{_unit_metallic_gradient_base("CombatTank", size, color)}'
            f'<rect x="{quarter}" y="{quarter}" width="{size - 2 * quarter}" '
            f'height="{size - 2 * quarter}" fill="{color}"/>'
            f'{_unit_shadow_svg(size)}'
            f'</svg>'
        )
    else:
        # Default: diamond shape for unknown unit types
        points = f"{half},{quarter} {size - quarter},{half} {half},{size - quarter} {quarter},{half}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<polygon points="{points}" fill="{color}" fill-opacity="0.9"/>'
            f'</svg>'
        )


def generate_minimap_svg(state_dict: dict, pixel_size: int = 4) -> str:
    """Renders a tactical overhead minimap SVG from a GameState dictionary.

    Args:
        state_dict: Serialized game state dictionary (width, height, tiles, buildings, units, sandworms).
        pixel_size: Pixel dimensions per tile cell (default 4).

    Returns:
        Complete SVG string displaying terrain, buildings, units, and sandworms.
    """
    width = state_dict.get("width", 16)
    height = state_dict.get("height", 16)
    tiles = state_dict.get("tiles", [])
    w_px = width * pixel_size
    h_px = height * pixel_size

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_px}" height="{h_px}" viewBox="0 0 {w_px} {h_px}">'
    ]

    # Render terrain cells
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            color = TERRAIN_COLORS.get(tile, "#e5c07b")
            parts.append(
                f'<rect x="{x * pixel_size}" y="{y * pixel_size}" width="{pixel_size}" height="{pixel_size}" fill="{color}"/>'
            )

    # Render buildings
    b_size = max(2, pixel_size)
    for b in state_dict.get("buildings", []):
        bx = b.get("x", 0) * pixel_size
        by = b.get("y", 0) * pixel_size
        bcolor = HOUSE_COLORS.get(b.get("house", "Atreides"), "#2563eb")
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{b_size}" height="{b_size}" fill="{bcolor}" stroke="#ffffff" stroke-width="0.5"/>'
        )

    # Render units
    u_rad = max(1.5, pixel_size / 2)
    half_px = pixel_size // 2
    for u in state_dict.get("units", []):
        ux = u.get("x", 0) * pixel_size + half_px
        uy = u.get("y", 0) * pixel_size + half_px
        ucolor = HOUSE_COLORS.get(u.get("house", "Atreides"), "#2563eb")
        parts.append(
            f'<circle cx="{ux}" cy="{uy}" r="{u_rad}" fill="{ucolor}"/>'
        )

    # Render sandworms
    w_rad = max(2.0, pixel_size * 0.75)
    for w in state_dict.get("sandworms", []):
        wx = w.get("x", 0) * pixel_size + half_px
        wy = w.get("y", 0) * pixel_size + half_px
        parts.append(
            f'<circle cx="{wx}" cy="{wy}" r="{w_rad}" fill="#b45309" stroke="#78350f" stroke-width="0.5"/>'
        )

    parts.append("</svg>")
    return "".join(parts)
