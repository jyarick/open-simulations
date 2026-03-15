"""
Color palettes for each geological epoch.
"""

EPOCH_COLORS = {
    "formation": ((180, 60, 40), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 120, 80)),
    "moon_impact": ((200, 80, 50), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 100, 60)),
    "cooling": ((60, 45, 55), (0, 0, 0), (0, 0, 0), (0, 0, 0), (80, 70, 90)),
    "oceans": ((45, 55, 50), (30, 80, 120), (0, 0, 0), (0, 0, 0), (100, 130, 160)),
    "microbial_life": ((50, 60, 55), (35, 90, 130), (0, 0, 0), (40, 70, 50), (110, 140, 165)),
    "oxygenation": ((55, 65, 58), (40, 100, 145), (0, 0, 0), (55, 85, 60), (120, 155, 185)),
    "snowball_earth": ((50, 55, 60), (60, 100, 140), (220, 235, 245), (0, 0, 0), (200, 215, 230)),
    "complex_life": ((65, 75, 60), (45, 110, 150), (200, 220, 235), (70, 120, 75), (130, 170, 195)),
    "dinosaurs": ((75, 95, 70), (50, 115, 155), (210, 225, 238), (85, 140, 90), (140, 180, 200)),
    "kt_extinction": ((70, 80, 65), (45, 100, 130), (200, 210, 220), (60, 100, 65), (120, 100, 80)),
    "modern": ((80, 100, 75), (55, 120, 165), (230, 240, 250), (90, 150, 95), (150, 190, 220)),
}


def get_epoch_colors(epoch: str) -> tuple:
    """Return (base, ocean, ice, vegetation, atmosphere) for epoch."""
    return EPOCH_COLORS.get(epoch, EPOCH_COLORS["formation"])


def rgb_to_hex(rgb: tuple) -> str:
    """Convert (r, g, b) to hex string."""
    return "#{:02x}{:02x}{:02x}".format(
        min(255, max(0, int(rgb[0]))),
        min(255, max(0, int(rgb[1]))),
        min(255, max(0, int(rgb[2]))),
    )
