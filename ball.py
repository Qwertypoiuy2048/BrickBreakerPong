"""Ball creation and collision helpers."""

import random
import pygame

from settings import BALL_SIZE, BALL_SPEED, HEIGHT, WIDTH


def reset_ball(direction=None):
    """Return a centered ball and velocity aimed toward a random player."""
    if direction is None:
        direction = random.choice((-1, 1))

    ball = pygame.Rect(
        WIDTH // 2 - BALL_SIZE // 2,
        HEIGHT // 2 - BALL_SIZE // 2,
        BALL_SIZE,
        BALL_SIZE,
    )
    velocity = pygame.Vector2(
        direction * BALL_SPEED,
        random.choice((-1, 1)) * BALL_SPEED * 0.65,
    )
    return ball, velocity


def bounce_off_brick(ball, velocity, brick, previous_ball):
    """Bounce from the first side of a brick that the ball entered."""
    hit_from_top_or_bottom = (
        previous_ball.bottom <= brick.top or previous_ball.top >= brick.bottom
    )

    if hit_from_top_or_bottom:
        velocity.y *= -1
        if previous_ball.bottom <= brick.top:
            ball.bottom = brick.top
        else:
            ball.top = brick.bottom
    else:
        velocity.x *= -1
        if previous_ball.right <= brick.left:
            ball.right = brick.left
        else:
            ball.left = brick.right
