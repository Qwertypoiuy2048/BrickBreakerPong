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


def draw_option(screen, font, message, y, selected, color=MUTED):
    """Draw a centered menu option with a pointer when selected."""
    prefix = "> " if selected else "  "
    draw_text(screen, font, prefix + message, (WIDTH // 2, y), color, center=True)


def navigation_delta(key):
    if key in (pygame.K_UP, pygame.K_w):
        return -1
    if key in (pygame.K_DOWN, pygame.K_s):
        return 1
    return 0


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


def shuffled_layout_order(previous_layout=None):
    """Return a randomized layout order, avoiding an immediate repeat."""
    order = list(range(layout_count()))
    random.shuffle(order)
    if previous_layout is not None and len(order) > 1 and order[0] == previous_layout:
        order[0], order[1] = order[1], order[0]
    return order


def move_paddles(left_paddle, right_paddle, keys, dt, one_player):
    previous_left_y = left_paddle.y
    previous_right_y = right_paddle.y
    left_direction = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    left_paddle.y += round(left_direction * PADDLE_SPEED * dt)

    if not one_player:
        right_direction = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        right_paddle.y += round(right_direction * PADDLE_SPEED * dt)

    bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
    left_paddle.clamp_ip(bounds)
    right_paddle.clamp_ip(bounds)
    seconds = max(dt, 0.0001)
    return (
        (left_paddle.y - previous_left_y) / seconds,
        (right_paddle.y - previous_right_y) / seconds,
    )


def move_ai(right_paddle, ball, dt):
    previous_y = right_paddle.y
    if right_paddle.centery < ball.centery:
        right_paddle.y += round(PADDLE_SPEED * AI_SPEED_FACTOR * dt)
    elif right_paddle.centery > ball.centery:
        right_paddle.y -= round(PADDLE_SPEED * AI_SPEED_FACTOR * dt)
    right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
    return (right_paddle.y - previous_y) / max(dt, 0.0001)


def bounce_off_paddle(ball, ball_velocity, paddle, paddle_velocity_y, ball_spin, direction):
    """Apply hit-position bounce, paddle movement, and transferable spin."""
    if direction > 0:
        ball.left = paddle.right
        ball_velocity.x = abs(ball_velocity.x)
    else:
        ball.right = paddle.left
        ball_velocity.x = -abs(ball_velocity.x)

    hit_offset = ball.centery - paddle.centery
    ball_spin += paddle_velocity_y * SPIN_TRANSFER
    ball_spin = max(-MAX_SPIN, min(MAX_SPIN, ball_spin))
    ball_velocity.y = (
        hit_offset * 5
        + paddle_velocity_y * PADDLE_BOUNCE_INFLUENCE
        + ball_spin * SPIN_BOUNCE_INFLUENCE
    )
    ball_velocity.y = max(-MAX_VERTICAL_SPEED, min(MAX_VERTICAL_SPEED, ball_velocity.y))
    return ball_spin


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
    round_winner,
    menu_selection,
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
        draw_text(screen, title_font, f"ROUND {round_number}: {receiver} SERVES", (WIDTH // 2, HEIGHT // 2 - 55), center=True)
        draw_text(screen, ui_font, f"Layout: {layout_name(current_layout)}", (WIDTH // 2, HEIGHT // 2), MUTED, center=True)
        draw_text(screen, ui_font, "Press SPACE or ENTER to launch", (WIDTH // 2, HEIGHT // 2 + 40), MUTED, center=True)
    elif mode == PAUSED:
        pygame.draw.rect(screen, (0, 0, 0, 175), (0, 0, WIDTH, HEIGHT))
        draw_text(screen, title_font, "PAUSED", (WIDTH // 2, HEIGHT // 2 - 65), center=True)
        draw_option(screen, ui_font, "Resume", HEIGHT // 2, menu_selection == 0, WHITE)
        draw_option(screen, ui_font, "Restart round", HEIGHT // 2 + 38, menu_selection == 1)
        draw_option(screen, ui_font, "Main menu", HEIGHT // 2 + 76, menu_selection == 2)
        draw_text(screen, ui_font, "Arrow keys / W A S D to move   Space to select", (WIDTH // 2, HEIGHT // 2 + 125), MUTED, center=True)
    elif mode == ROUND_OVER:
        pygame.draw.rect(screen, (0, 0, 0, 175), (0, 0, WIDTH, HEIGHT))
        winner = "P1" if round_winner == 0 else "P2"
        draw_text(screen, title_font, f"{winner} WINS ROUND {round_number}", (WIDTH // 2, HEIGHT // 2 - 60), center=True)
        draw_text(screen, ui_font, f"Round score: P1 {scores[0]}  -  P2 {scores[1]}", (WIDTH // 2, HEIGHT // 2), MUTED, center=True)
        draw_option(screen, ui_font, "Continue to next round", HEIGHT // 2 + 45, True, WHITE)
        draw_text(screen, ui_font, "Press SPACE to select", (WIDTH // 2, HEIGHT // 2 + 85), MUTED, center=True)
    elif mode == MATCH_OVER:
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, WIDTH, HEIGHT))
        winner = "P1" if round_wins[0] > round_wins[1] else "P2"
        draw_text(screen, title_font, f"{winner} WINS THE MATCH", (WIDTH // 2, HEIGHT // 2 - 35), center=True)
        draw_text(screen, ui_font, f"Round tally: P1 {round_wins[0]}  -  P2 {round_wins[1]}", (WIDTH // 2, HEIGHT // 2 + 5), MUTED, center=True)
        draw_option(screen, ui_font, "Rematch", HEIGHT // 2 + 55, menu_selection == 0, WHITE)
        draw_option(screen, ui_font, "Main menu", HEIGHT // 2 + 93, menu_selection == 1)
        draw_text(screen, ui_font, "Arrow keys / W A S D to move   Space to select", (WIDTH // 2, HEIGHT // 2 + 135), MUTED, center=True)


def draw_menu(screen, title_font, ui_font, menu_selection, menu_notice):
    screen.fill(BACKGROUND)
    draw_text(screen, title_font, "BRICK BREAKER PONG", (WIDTH // 2, 150), center=True)
    draw_text(screen, ui_font, "Choose an option", (WIDTH // 2, 245), MUTED, center=True)
    draw_option(screen, ui_font, "One Player", 295, menu_selection == 0, PLAYER_ONE_COLOR)
    draw_option(screen, ui_font, "Two Players", 335, menu_selection == 1, PLAYER_TWO_COLOR)
    draw_option(screen, ui_font, "Settings", 375, menu_selection == 2, WHITE)
    draw_option(screen, ui_font, "Controls", 415, menu_selection == 3, WHITE)
    draw_text(screen, ui_font, f"First to {ROUNDS_TO_WIN} rounds  |  {layout_count()} randomized layouts", (WIDTH // 2, 475), MUTED, center=True)
    if menu_notice:
        draw_text(screen, ui_font, menu_notice, (WIDTH // 2, 510), PLAYER_TWO_COLOR, center=True)
    draw_text(screen, ui_font, "Arrow keys / W A S D to move   Space to select", (WIDTH // 2, 565), MUTED, center=True)
    draw_text(screen, ui_font, "Escape: quit", (WIDTH // 2, 600), MUTED, center=True)


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
    layout_order = shuffled_layout_order()
    layout_position = 0
    current_layout = layout_order[layout_position]
    bricks = make_bricks(current_layout)
    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
    ball_spin = 0
    last_hit = "START"
    round_winner = None
    mode = MENU
    one_player = False
    menu_selection = 0
    menu_notice = ""
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if mode == MENU:
                        running = False
                    else:
                        mode = MENU
                        menu_selection = 0
                        menu_notice = ""
                elif mode == MENU and navigation_delta(event.key):
                    menu_selection = (menu_selection + navigation_delta(event.key)) % 4
                    menu_notice = ""
                elif mode == MENU and event.key == pygame.K_SPACE:
                    if menu_selection in (0, 1):
                        one_player = menu_selection == 0
                        left_paddle, right_paddle = create_paddles()
                        scores = [0, 0]
                        round_wins = [0, 0]
                        round_number = 1
                        layout_order = shuffled_layout_order()
                        layout_position = 0
                        current_layout = layout_order[layout_position]
                        bricks = make_bricks(current_layout)
                        ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                        last_hit = "START"
                        round_winner = None
                        mode = SERVE
                        menu_selection = 0
                        menu_notice = ""
                    elif menu_selection == 2:
                        menu_notice = "Settings will be available in a future update."
                    else:
                        menu_notice = "Controls will be available in a future update."
                elif mode == SERVE and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    ball_velocity.x = BALL_SPEED if server == 0 else -BALL_SPEED
                    ball_velocity.y = random.choice((-1, 1)) * BALL_SPEED * 0.65
                    ball_spin = 0
                    mode = PLAYING
                elif mode == PLAYING and event.key == pygame.K_p:
                    mode = PAUSED
                    menu_selection = 0
                elif mode == PAUSED:
                    if navigation_delta(event.key):
                        menu_selection = (menu_selection + navigation_delta(event.key)) % 3
                    elif event.key == pygame.K_SPACE:
                        if menu_selection == 0:
                            mode = PLAYING
                        elif menu_selection == 1:
                            scores = [0, 0]
                            left_paddle, right_paddle = create_paddles()
                            bricks = make_bricks(current_layout)
                            ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                            ball_spin = 0
                            last_hit = "START"
                            mode = SERVE
                        else:
                            mode = MENU
                            menu_selection = 0
                            menu_notice = ""
                    elif event.key == pygame.K_p:
                        mode = PLAYING
                elif mode == ROUND_OVER and event.key == pygame.K_SPACE:
                    if round_winner is not None and round_wins[round_winner] >= ROUNDS_TO_WIN:
                        mode = MATCH_OVER
                        menu_selection = 0
                    else:
                        round_number += 1
                        layout_position += 1
                        if layout_position >= len(layout_order):
                            layout_order = shuffled_layout_order(current_layout)
                            layout_position = 0
                        current_layout = layout_order[layout_position]
                        scores = [0, 0]
                        left_paddle, right_paddle = create_paddles()
                        bricks = make_bricks(current_layout)
                        ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                        ball_spin = 0
                        last_hit = "START"
                        round_winner = None
                        mode = SERVE
                elif mode == MATCH_OVER:
                    if navigation_delta(event.key):
                        menu_selection = (menu_selection + navigation_delta(event.key)) % 2
                    elif event.key == pygame.K_SPACE and menu_selection == 0:
                        scores = [0, 0]
                        round_wins = [0, 0]
                        round_number = 1
                        layout_order = shuffled_layout_order()
                        layout_position = 0
                        current_layout = layout_order[layout_position]
                        left_paddle, right_paddle = create_paddles()
                        bricks = make_bricks(current_layout)
                        ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                        ball_spin = 0
                        last_hit = "START"
                        round_winner = None
                        mode = SERVE
                        menu_selection = 0
                    elif event.key == pygame.K_SPACE and menu_selection == 1:
                        mode = MENU
                        menu_selection = 0
                        menu_notice = ""

        keys = pygame.key.get_pressed()

        if mode in (SERVE, PLAYING):
            left_paddle_velocity_y, right_paddle_velocity_y = move_paddles(
                left_paddle, right_paddle, keys, dt, one_player
            )
            if one_player:
                right_paddle_velocity_y = move_ai(right_paddle, ball, dt)

            if mode == SERVE:
                attach_ball_to_paddle(ball, left_paddle if server == 0 else right_paddle, server)

            if mode == PLAYING:
                previous_ball = ball.copy()
                ball.x += round(ball_velocity.x * dt)
                ball.y += round(ball_velocity.y * dt)
                ball_spin *= SPIN_DECAY ** (dt * FPS)
                ball_velocity.y += ball_spin * SPIN_ACCELERATION * dt
                ball_velocity.y = max(-MAX_VERTICAL_SPEED, min(MAX_VERTICAL_SPEED, ball_velocity.y))

                if ball.top <= 0 or ball.bottom >= HEIGHT:
                    ball_velocity.y *= -1
                    ball.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

                if ball_velocity.x < 0 and ball.colliderect(left_paddle):
                    ball_spin = bounce_off_paddle(
                        ball, ball_velocity, left_paddle, left_paddle_velocity_y, ball_spin, 1
                    )
                    last_hit = "P1"
                elif ball_velocity.x > 0 and ball.colliderect(right_paddle):
                    ball_spin = bounce_off_paddle(
                        ball, ball_velocity, right_paddle, right_paddle_velocity_y, ball_spin, -1
                    )
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
                    ball_spin = 0
                    last_hit = "START"
                    mode = SERVE
                elif ball.left > WIDTH:
                    scores[0] += MISS_POINTS
                    ball, ball_velocity, server = prepare_serve(scores, left_paddle, right_paddle)
                    ball_spin = 0
                    last_hit = "START"
                    mode = SERVE

                if not bricks:
                    round_winner = 0 if scores[0] >= scores[1] else 1
                    round_wins[round_winner] += 1
                    mode = ROUND_OVER

        if mode == MENU:
            draw_menu(screen, title_font, ui_font, menu_selection, menu_notice)
        else:
            draw_game(screen, score_font, ui_font, title_font, left_paddle, right_paddle, ball, bricks, scores, round_wins, round_number, last_hit, mode, server, current_layout, round_winner, menu_selection)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
