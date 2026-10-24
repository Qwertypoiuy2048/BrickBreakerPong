"""Brick layout loading, creation, and drawing."""

import json
from pathlib import Path

import pygame

from settings import (
    BRICK_COLORS,
    CENTER_GAP,
    BRICK_GAP,
    BRICK_HEIGHT,
    BRICK_WIDTH,
    HEIGHT,
    WIDTH,
)

LAYOUT_FILE = Path(__file__).with_name("layouts.json")


class Brick:
    """A brick with a position and a number of hits remaining."""

    def __init__(self, rectangle, health):
        """Store the brick rectangle and its remaining hit points."""
        self.rect = rectangle
        self.health = health

    def hit(self):
        """Remove one hit point from the brick."""
        self.health -= 1

    @property
    def destroyed(self):
        """Return whether the brick has no hit points remaining."""
        return self.health <= 0


def load_layouts():
    """Load and validate the mirrored half-layouts from layouts.json."""
    with LAYOUT_FILE.open(encoding="utf-8") as file:
        data = json.load(file)

    layouts = data.get("layouts", [])
    if not layouts:
        raise ValueError("layouts.json must contain at least one layout")

    for layout in layouts:
        pattern = layout.get("pattern", [])
        if not pattern or any(not isinstance(row, str) or not row for row in pattern):
            raise ValueError("Every layout needs a non-empty string pattern")
        width = len(pattern[0])
        if any(len(row) != width for row in pattern):
            raise ValueError("Every row in a layout must have the same width")

    return layouts


def make_bricks(layout_index=0):
    """Create a layout and its horizontal mirror around the center."""
    layouts = load_layouts()
    layout = layouts[layout_index % len(layouts)]
    pattern = layout["pattern"]
    rows = len(pattern)
    columns = len(pattern[0])

    formation_width = columns * BRICK_WIDTH + (columns - 1) * BRICK_GAP
    formation_height = rows * BRICK_HEIGHT + (rows - 1) * BRICK_GAP
    left_start_x = WIDTH // 2 - CENTER_GAP // 2 - formation_width
    right_start_x = WIDTH // 2 + CENTER_GAP // 2
    start_y = (HEIGHT - formation_height) // 2
    bricks = []

    for row, pattern_row in enumerate(pattern):
        for column, cell in enumerate(pattern_row):
            if cell not in ("0", "."):
                health = int(cell)
                if health < 1:
                    continue
                x = left_start_x + column * (BRICK_WIDTH + BRICK_GAP)
                y = start_y + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append(Brick(pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT), health))

                mirror_column = columns - 1 - column
                mirror_x = right_start_x + mirror_column * (BRICK_WIDTH + BRICK_GAP)
                bricks.append(Brick(pygame.Rect(mirror_x, y, BRICK_WIDTH, BRICK_HEIGHT), health))

    return bricks


def layout_name(layout_index=0):
    """Return the display name for a layout index."""
    layouts = load_layouts()
    return layouts[layout_index % len(layouts)].get("name", f"Layout {layout_index + 1}")


def layout_count():
    """Return the number of layouts currently available in the JSON file."""
    return len(load_layouts())


def draw_bricks(screen, brick_list):
    """Draw each brick using a color based on its remaining health."""
    for brick in brick_list:
        color_index = min(brick.health, len(BRICK_COLORS)) - 1
        pygame.draw.rect(screen, BRICK_COLORS[color_index], brick.rect, border_radius=4)
