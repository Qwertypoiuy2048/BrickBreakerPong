"""Two-player Brick Breaker Pong prototype."""

import random
import sys

import pygame

from ball import bounce_off_brick
from bricks import draw_bricks, layout_count, layout_name, make_bricks
from settings import *  # noqa: F403 - game constants are kept in one place.



def draw_text(screen, font, message, position, color=WHITE, center=False):
    surface = font.render(message, True, color)
    rectangle = surface.get_rect()
    if center:
        rectangle.center = position
    else:
        rectangle.topleft = position
    screen.blit(surface, rectangle)


def create_paddles():
    left = pygame.Rect(35, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right = pygame.Rect(
        WIDTH - 35 - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )
    return left, right


def attach_ball_to_paddle(ball, paddle, player):
    """Keep a stationary serve just inside the selected player's paddle."""
    ball.centery = paddle.centery
    if player == 0:
        ball.left = paddle.right + 2
    else:
        ball.right = paddle.left - 2


def prepare_serve(scores, left_paddle, right_paddle):
    """Choose the lower-scoring player to receive the next serve."""
    server = 0 if scores[0] <= scores[1] else 1
    ball = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    paddle = left_paddle if server == 0 else right_paddle
    attach_ball_to_paddle(ball, paddle, server)
    return ball, pygame.Vector2(0, 0), server


def move_paddles(left_paddle, right_paddle, keys, dt, one_player):
    left_direction = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    left_paddle.y += round(left_direction * PADDLE_SPEED * dt)

    if not one_player:
        right_direction = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        right_paddle.y += round(right_direction * PADDLE_SPEED * dt)

    bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
    left_paddle.clamp_ip(bounds)
    right_paddle.clamp_ip(bounds)


def move_ai(right_paddle, ball, dt):
    if right_paddle.centery < ball.centery:
        right_paddle.y += round(PADDLE_SPEED * AI_SPEED_FACTOR * dt)
    elif right_paddle.centery > ball.centery:
        right_paddle.y -= round(PADDLE_SPEED * 0.72 * dt)
    right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))


def draw_game(
    screen,
    score_font,
    ui_font,
    title_font,
    left_paddle,
    right_paddle,
    ball,
    bricks,
    scores,
    round_wins,
    round_number,
    last_hit,
    mode,
    server,
    current_layout,
):
    screen.fill(BACKGROUND)
    pygame.draw.line(screen, (45, 50, 78), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
    pygame.draw.rect(screen, PLAYER_ONE_COLOR, left_paddle, border_radius=5)
    pygame.draw.rect(screen, PLAYER_TWO_COLOR, right_paddle, border_radius=5)
    pygame.draw.ellipse(screen, WHITE, ball)
    draw_bricks(screen, bricks)

    draw_text(screen, score_font, str(scores[0]), (WIDTH // 4, 18), PLAYER_ONE_COLOR, center=True)
    draw_text(screen, score_font, str(scores[1]), (WIDTH * 3 // 4, 18), PLAYER_TWO_COLOR, center=True)
    draw_text(screen, ui_font, f"Round {round_number}  |  Wins {round_wins[0]} - {round_wins[1]}", (WIDTH // 2, 18), MUTED, center=True)
    draw_text(screen, ui_font, f"Layout: {layout_name(current_layout)}", (WIDTH // 2, 48), MUTED, center=True)
    draw_text(screen, ui_font, "P1: W/S", (25, HEIGHT - 35), PLAYER_ONE_COLOR)
    draw_text(screen, ui_font, "P2: Arrow Keys", (WIDTH - 155, HEIGHT - 35), PLAYER_TWO_COLOR)
    draw_text(screen, ui_font, f"Last hit: {last_hit}", (WIDTH // 2, HEIGHT - 35), MUTED, center=True)

    if mode == SERVE:
        pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        receiver = "P1" if server == 0 else "P2"
        draw_text(screen, title_font, f"{receiver} SERVES", (WIDTH // 2, HEIGHT // 2 - 35), center=True)
        draw_text(screen, ui_font, "Press SPACE or ENTER to launch", (WIDTH // 2, HEIGHT // 2 + 25), MUTED, center=True)
    elif mode == MATCH_OVER:
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
        winner = "P1" if round_wins[0] > round_wins[1] else "P2"
        draw_text(screen, title_font, f"{winner} WINS THE MATCH", (WIDTH // 2, HEIGHT // 2 - 35), center=True)
        draw_text(screen, ui_font, "Press SPACE, ENTER, or R for the menu", (WIDTH // 2, HEIGHT // 2 + 25), MUTED, center=True)


def draw_menu(screen, title_font, ui_font):
    screen.fill(BACKGROUND)
    draw_text(screen, title_font, "BRICK BREAKER PONG", (WIDTH // 2, 150), center=True)
    draw_text(screen, ui_font, "Choose a game mode", (WIDTH // 2, 260), MUTED, center=True)
    draw_text(screen, ui_font, "1  -  One Player", (WIDTH // 2, 330), PLAYER_ONE_COLOR, center=True)
    draw_text(screen, ui_font, "2  -  Two Players", (WIDTH // 2, 380), PLAYER_TWO_COLOR, center=True)
    draw_text(screen, ui_font, f"First to {ROUNDS_TO_WIN} rounds wins  |  {layout_count()} layouts available", (WIDTH // 2, 450), MUTED, center=True)
    draw_text(screen, ui_font, "P1: W/S     P2: Arrow Keys     Esc: Quit", (WIDTH // 2, 525), MUTED, center=True)


def main():
    pygame.init()
    pygame.display.set_caption("Brick Breaker Pong")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score_font = pygame.font.Font(None, 48)
    ui_font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 64)

    left_paddle, right_paddle = create_paddles()
    scores = [0, 0]
    round_wins = [0, 0]
    round_number = 1
    current_layout = 0
    bricks = make_bricks(current_layout)
    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
    last_hit = "START"
    mode = MENU
    one_player = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif mode == MENU and event.key in (pygame.K_1, pygame.K_KP1, pygame.K_2, pygame.K_KP2):
                    one_player = event.key in (pygame.K_1, pygame.K_KP1)
                    left_paddle, right_paddle = create_paddles()
                    scores = [0, 0]
                    round_wins = [0, 0]
                    round_number = 1
                    current_layout = 0
                    bricks = make_bricks(current_layout)
                    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                    last_hit = "START"
                    mode = SERVE
                elif mode == SERVE and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    ball_velocity.x = BALL_SPEED if server == 0 else -BALL_SPEED
                    ball_velocity.y = random.choice((-1, 1)) * BALL_SPEED * 0.65
                    mode = PLAYING
                elif mode == MATCH_OVER and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                    mode = MENU
                elif mode in (SERVE, PLAYING) and event.key == pygame.K_r:
                    mode = MENU

        keys = pygame.key.get_pressed()

        if mode in (SERVE, PLAYING):
            move_paddles(left_paddle, right_paddle, keys, dt, one_player)
            if one_player:
                move_ai(right_paddle, ball, dt)

            if mode == SERVE:
                attach_ball_to_paddle(ball, left_paddle if server == 0 else right_paddle, server)

            if mode == PLAYING:
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
                    if ball.colliderect(brick.rect):
                        bounce_off_brick(ball, ball_velocity, brick.rect, previous_ball)
                        if last_hit != "START":
                            brick.hit()
                            if brick.destroyed:
                                bricks.remove(brick)
                                scores[0 if last_hit == "P1" else 1] += ROUND_BRICK_POINTS
                        break

                if ball.right < 0:
                    scores[1] += MISS_POINTS
                    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                    last_hit = "START"
                    mode = SERVE
                elif ball.left > WIDTH:
                    scores[0] += MISS_POINTS
                    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                    last_hit = "START"
                    mode = SERVE

                if not bricks:
                    round_winner = 0 if last_hit == "P1" else 1
                    round_wins[round_winner] += 1
                    if round_wins[round_winner] >= ROUNDS_TO_WIN:
                        mode = MATCH_OVER
                    else:
                        round_number += 1
                        current_layout = (current_layout + 1) % layout_count()
                        scores = [0, 0]
                        left_paddle, right_paddle = create_paddles()
                        bricks = make_bricks(current_layout)
                        ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                        last_hit = "START"
                        mode = SERVE

        if mode == MENU:
            draw_menu(screen, title_font, ui_font)
        else:
            draw_game(screen, score_font, ui_font, title_font, left_paddle, right_paddle, ball, bricks, scores, round_wins, round_number, last_hit, mode, server, current_layout)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
