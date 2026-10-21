"""Two-player Brick Breaker Pong prototype."""

import sys

import pygame

from ball import bounce_off_brick, reset_ball
from bricks import draw_bricks, make_bricks
from settings import *  # noqa: F403 - game constants are kept in one place.


def draw_text(screen, font, message, position, color=WHITE, center=False):
    surface = font.render(message, True, color)
    rectangle = surface.get_rect()
    if center:
        rectangle.center = position
    else:
        rectangle.topleft = position
    screen.blit(surface, rectangle)


def reset_game():
    left = pygame.Rect(35, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right = pygame.Rect(
        WIDTH - 35 - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )
    ball, velocity = reset_ball()
    return left, right, ball, velocity, make_bricks(), [0, 0], "START"


def main():
    pygame.init()
    pygame.display.set_caption("Brick Breaker Pong")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score_font = pygame.font.Font(None, 48)
    ui_font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 64)

    left_paddle, right_paddle, ball, ball_velocity, bricks, scores, last_hit = reset_game()
    paused = True
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
                    left_paddle, right_paddle, ball, ball_velocity, bricks, scores, last_hit = reset_game()
                    paused = True

        keys = pygame.key.get_pressed()

        if not paused:
            left_direction = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
            right_direction = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
            left_paddle.y += round(left_direction * PADDLE_SPEED * dt)
            right_paddle.y += round(right_direction * PADDLE_SPEED * dt)
            left_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
            right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            previous_ball = ball.copy()
            ball.x += round(ball_velocity.x * dt)
            ball.y += round(ball_velocity.y * dt)

            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_velocity.y *= -1
                ball.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

            if ball_velocity.x < 0 and ball.colliderect(left_paddle):
                ball.left = left_paddle.right
                ball_velocity.x = abs(ball_velocity.x)
                ball_velocity.y = (ball.centery - left_paddle.centery) * 5
                last_hit = "P1"
            elif ball_velocity.x > 0 and ball.colliderect(right_paddle):
                ball.right = right_paddle.left
                ball_velocity.x = -abs(ball_velocity.x)
                ball_velocity.y = (ball.centery - right_paddle.centery) * 5
                last_hit = "P2"

            for brick in bricks[:]:
                if ball.colliderect(brick):
                    bounce_off_brick(ball, ball_velocity, brick, previous_ball)
                    if last_hit != "START":
                        bricks.remove(brick)
                        scores[0 if last_hit == "P1" else 1] += 10
                    break

            if ball.right < 0:
                scores[1] += 25
                ball, ball_velocity = reset_ball(1)
                last_hit = "START"
            elif ball.left > WIDTH:
                scores[0] += 25
                ball, ball_velocity = reset_ball(-1)
                last_hit = "START"

            if not bricks:
                bricks = make_bricks()
                ball, ball_velocity = reset_ball()
                last_hit = "START"

        screen.fill(BACKGROUND)
        pygame.draw.line(screen, (45, 50, 78), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        pygame.draw.rect(screen, PLAYER_ONE_COLOR, left_paddle, border_radius=5)
        pygame.draw.rect(screen, PLAYER_TWO_COLOR, right_paddle, border_radius=5)
        pygame.draw.ellipse(screen, WHITE, ball)
        draw_bricks(screen, bricks)

        draw_text(screen, score_font, str(scores[0]), (WIDTH // 4, 18), PLAYER_ONE_COLOR, center=True)
        draw_text(screen, score_font, str(scores[1]), (WIDTH * 3 // 4, 18), PLAYER_TWO_COLOR, center=True)
        draw_text(screen, ui_font, "P1: W/S", (25, HEIGHT - 35), PLAYER_ONE_COLOR)
        draw_text(screen, ui_font, "P2: Arrow Keys", (WIDTH - 155, HEIGHT - 35), PLAYER_TWO_COLOR)
        draw_text(screen, ui_font, f"Last hit: {last_hit}", (WIDTH // 2, HEIGHT - 35), MUTED, center=True)

        if paused:
            pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
            draw_text(screen, title_font, "PAUSED", (WIDTH // 2, HEIGHT // 2 - 25), center=True)
            draw_text(screen, ui_font, "Press SPACE to start", (WIDTH // 2, HEIGHT // 2 + 30), MUTED, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
