"""Two-player Brick Breaker Pong prototype.

Player 1: W / S
Player 2: Up / Down
Space: pause or resume
R: restart
Escape: quit
"""

import random
import sys

import pygame


# Window and timing
WIDTH, HEIGHT = 900, 650
FPS = 60

# Colors
BACKGROUND = (15, 18, 35)
WHITE = (242, 245, 255)
MUTED = (150, 160, 190)
PLAYER_ONE_COLOR = (85, 190, 255)
PLAYER_TWO_COLOR = (255, 120, 170)
BRICK_COLORS = [(255, 100, 110), (255, 175, 80), (255, 220, 90)]

# Game objects
PADDLE_WIDTH, PADDLE_HEIGHT = 18, 110
PADDLE_SPEED = 430
BALL_SIZE = 16
BALL_SPEED = 360
BRICK_WIDTH, BRICK_HEIGHT = 72, 24
BRICK_GAP = 8
BRICK_ROWS, BRICK_COLUMNS = 3, 8


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


def reset_ball(direction=None):
    """Return a ball rectangle and velocity, aimed toward a random player."""
    if direction is None:
        direction = random.choice((-1, 1))
    ball = pygame.Rect(
        WIDTH // 2 - BALL_SIZE // 2,
        HEIGHT // 2 - BALL_SIZE // 2,
        BALL_SIZE,
        BALL_SIZE,
    )
    velocity = pygame.Vector2(direction * BALL_SPEED, random.choice((-1, 1)) * BALL_SPEED * 0.65)
    return ball, velocity


def reset_game():
    left = pygame.Rect(35, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right = pygame.Rect(
        WIDTH - 35 - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )
    ball, velocity = reset_ball()
    return left, right, ball, velocity, make_bricks(), [0, 0]


def draw_text(screen, font, message, position, color=WHITE, center=False):
    surface = font.render(message, True, color)
    rectangle = surface.get_rect()
    if center:
        rectangle.center = position
    else:
        rectangle.topleft = position
    screen.blit(surface, rectangle)


def main():
    pygame.init()
    pygame.display.set_caption("Brick Breaker Pong")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score_font = pygame.font.Font(None, 48)
    ui_font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 64)

    left_paddle, right_paddle, ball, ball_velocity, bricks, scores = reset_game()
    paused = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    left_paddle, right_paddle, ball, ball_velocity, bricks, scores = reset_game()
                    paused = False

        keys = pygame.key.get_pressed()

        if not paused:
            # Move paddles using frame-rate-independent movement.
            left_direction = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            right_direction = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            left_paddle.y += round(left_direction * PADDLE_SPEED * dt)
            right_paddle.y += round(right_direction * PADDLE_SPEED * dt)
            left_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
            right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            # Move the ball and bounce off the top and bottom walls.
            ball.x += round(ball_velocity.x * dt)
            ball.y += round(ball_velocity.y * dt)
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_velocity.y *= -1
                ball.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            # Paddle collisions slightly change the vertical angle based on hit position.
            if ball_velocity.x < 0 and ball.colliderect(left_paddle):
                ball.left = left_paddle.right
                ball_velocity.x = abs(ball_velocity.x)
                ball_velocity.y = (ball.centery - left_paddle.centery) * 5
            elif ball_velocity.x > 0 and ball.colliderect(right_paddle):
                ball.right = right_paddle.left
                ball_velocity.x = -abs(ball_velocity.x)
                ball_velocity.y = (ball.centery - right_paddle.centery) * 5

            # A brick disappears when the ball hits it.
            for brick in bricks[:]:
                if ball.colliderect(brick):
                    bricks.remove(brick)
                    scores[0 if ball_velocity.x < 0 else 1] += 10
                    ball_velocity.y *= -1
                    break

            # Missing the ball awards the point to the other player and serves again.
            if ball.right < 0:
                scores[1] += 25
                ball, ball_velocity = reset_ball(1)
            elif ball.left > WIDTH:
                scores[0] += 25
                ball, ball_velocity = reset_ball(-1)

            if not bricks:
                bricks = make_bricks()
                ball, ball_velocity = reset_ball()

        # Draw the current frame.
        screen.fill(BACKGROUND)
        pygame.draw.line(screen, (45, 50, 78), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        pygame.draw.rect(screen, PLAYER_ONE_COLOR, left_paddle, border_radius=5)
        pygame.draw.rect(screen, PLAYER_TWO_COLOR, right_paddle, border_radius=5)
        pygame.draw.ellipse(screen, WHITE, ball)

        for index, brick in enumerate(bricks):
            pygame.draw.rect(screen, BRICK_COLORS[index // BRICK_COLUMNS], brick, border_radius=4)

        draw_text(screen, score_font, str(scores[0]), (WIDTH // 4, 18), PLAYER_ONE_COLOR, center=True)
        draw_text(screen, score_font, str(scores[1]), (WIDTH * 3 // 4, 18), PLAYER_TWO_COLOR, center=True)
        draw_text(screen, ui_font, "P1: W/S", (25, HEIGHT - 35), PLAYER_ONE_COLOR)
        draw_text(screen, ui_font, "P2: Arrow Keys", (WIDTH - 155, HEIGHT - 35), PLAYER_TWO_COLOR)

        if paused:
            pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
            draw_text(screen, title_font, "PAUSED", (WIDTH // 2, HEIGHT // 2 - 25), center=True)
            draw_text(screen, ui_font, "Press SPACE to resume", (WIDTH // 2, HEIGHT // 2 + 30), MUTED, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
