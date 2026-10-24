# BrickBreakerPong

A two-player brick-breaker/Pong prototype built with Pygame.

The project is split into `main.py` for the game loop, `ball.py` for ball
movement/collisions, `bricks.py` for the mirrored brick formations, and
`settings.py` for shared constants. Brick formations and their health values
are defined in `layouts.json`.

## Instructions for Build and Use

### Run it

Install Pygame:

```bash
python -m pip install pygame
```

Start the game:

```bash
python main.py
```

### Controls

- Menus: Arrow keys or `WASD` move the pointer, `Space` selects
- Settings: use Left/Right or `A/D` to change the selected value; `Space` activates buttons
- Player 1: `W` / `S`
- Player 2: Arrow `Up` / `Down` (two-player mode)
- `Space` or `Enter`: launch the ball from the serve
- `P`: pause during gameplay
- `Escape`: quit

Pressing `Escape` during gameplay or on an overlay returns to the main menu.
Pressing it on the main menu exits the game.

Current settings include rounds to win (`1`, `2`, `3`, `4`, `5`, or `10`), five
ball-speed levels, and bounce style. `Position` uses only the paddle hit
location, `Spin` ignores hit location and uses paddle movement plus transferable
spin, and `Both` combines position, movement, and spin.

The game starts at a mode-selection menu. In one-player mode, Player 2 is
controlled by a simple computer opponent. 

To add a layout, add another object with a `name` and a rectangular `pattern`; `1`  `2` or `3` creates a brick and `0` or `.` leaves a space. 

Paddle movement affects the bounce angle. Moving into the ball transfers spin,
which gradually fades and is clamped so the ball remains controllable. Spin
and bounce tuning values are in `settings.py`.

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [realpython.com](realpython.com)
* [arcade.academy](arcade.academy)
