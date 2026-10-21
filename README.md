# BrickBreakerPong

A two-player brick-breaker/Pong prototype built with Pygame.

The project is split into `main.py` for the game loop, `ball.py` for ball
movement/collisions, `bricks.py` for the mirrored brick formations, and
`settings.py` for shared constants. Brick formations and their health values
are defined in `layouts.json`.

## Run it

Install Pygame:

```bash
python -m pip install pygame
```

Start the game:

```bash
python main.py
```

## Controls

- Menu: `1` for one player, `2` for two players
- Player 1: `W` / `S`
- Player 2: Arrow `Up` / `Down` (two-player mode)
- `Space` or `Enter`: launch the ball from the serve
- `R`: return to the menu
- `Escape`: quit

The game starts at a mode-selection menu. In one-player mode, Player 2 is
controlled by a simple computer opponent. Each serve places the ball on the
paddle of the player with fewer points; ties go to Player 1. The ball waits
there until `Space` or `Enter` is pressed.

Each match is first to two round wins. Clearing a layout wins the round and
loads the next layout from `layouts.json`. To add a layout, add another object
with a `name` and a rectangular `pattern`; `1` creates a brick and `0` or `.`
leaves a space. Higher values such as `2` or `3` give a brick more health and
change its color. The current layouts use `1`, so all bricks are red. The
pattern is automatically mirrored for the other side.

The visible player scores reset when a new round begins. The round-win tally
shown at the top continues across the match.

The last player to hit the ball is shown at the bottom. Only that player can
destroy bricks and receive their points. A ball served from a paddle is marked
`START`, so its first brick collision bounces without destroying the brick or
awarding points.
