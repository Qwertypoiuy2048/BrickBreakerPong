"""Brick wall creation and drawing."""

import pygame

from settings import (
    BRICK_COLORS,
    BRICK_COLUMNS,
    BRICK_GAP,
    BRICK_HEIGHT,
    BRICK_ROWS,
    BRICK_WIDTH,
    WIDTH,
)


def make_bricks():
    """Create a centered brick wall with one hit point per brick."""
    wall_width = BRICK_COLUMNS * BRICK_WIDTH + (BRICK_COLUMNS - 1) * BRICK_GAP
    start_x = (WIDTH - wall_width) // 2
    start_y = 75
    bricks = []

    for row in range(BRICK_ROWS):
        for column in range(BRICK_COLUMNS):
            x = start_x + column * (BRICK_WIDTH + BRICK_GAP)
            y = start_y + row * (BRICK_HEIGHT + BRICK_GAP)
            bricks.append(pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT))
    return bricks


def draw_bricks(screen, brick_list):
    for index, brick in enumerate(brick_list):
        pygame.draw.rect(screen, BRICK_COLORS[index // BRICK_COLUMNS], brick, border_radius=4)
