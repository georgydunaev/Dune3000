"""
Algorithmic procedural graphics generator for Dune 3000.
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
