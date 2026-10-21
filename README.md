# BrickBreakerPong

A two-player brick-breaker/Pong prototype built with Pygame.

The project is split into `main.py` for the game loop, `ball.py` for ball
movement/collisions, `bricks.py` for the brick wall, and `settings.py` for
shared constants.

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

- Player 1: `W` / `S`
- Player 2: Arrow `Up` / `Down`
- `Space`: pause/resume
- `R`: restart
- `Escape`: quit

The game starts paused. The last player to hit the ball is shown at the bottom.
Only that player can destroy bricks and receive their points. A ball served
from the center is marked `START`, so its first brick collision bounces without
destroying the brick or awarding points.
