# Team15_SE_Project
A desktop Snake game built with Python and Pygame, alongside its SE documents.

## Team Members

| Name                | SRN            |
|---------------------|----------------|
| Akshatha P          | PES2UG24CS048  |
| Aditya Shrivastav   | PES2UG24CS036  |
| Ananya Ratnaparkhi  | PES2UG24CS058  |
| Alakh Gupta         | PES2UG24CS051  |



## Movement speed (SNK-F-018)

The initial movement interval is 150 ms. At scores 50, 100, 150, 200,
and 250 it drops to 130, 110, 90, 70, and 50 ms respectively. The interval
stays at 50 ms above 250 points. These fixed defaults resolve the thresholds
left open in the design document; they live in `snake_game/difficulty.py`.
Resetting the engine resets the score and restores 150 ms. Rendering continues
to use the existing 60 FPS clock independently of movement speed.

## Run on Windows, macOS, or Linux (SNK-NF-004)

Use Python 3.12 or 3.13 and run these commands from the repository root.
No source changes are needed between desktop platforms.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m snake_game
```

macOS / Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m snake_game
```

`python main.py` is also supported when using your environment's Python.
Use arrow keys or WASD to steer, P to pause/resume, and close the window to exit.
A normal desktop session with a display is required for interactive play.
This is the desktop build; browser delivery is outside this change.

### Platform validation

CI installs Pygame, compiles the sources, and runs the complete suite on Windows,
macOS, and Linux with Python 3.12 and 3.13. It uses SDL's dummy video/audio drivers
for deterministic headless checks. Launcher tests start a fresh process, render
frames, exercise direction and pause controls, and close the window cleanly.
These checks do not establish native window/input behavior or interactive performance.

For a manual acceptance pass on each OS: launch the game, check the visible board
and centred three-segment snake, steer with arrows/WASD, press P twice to verify
pause/resume, play to a wall or self collision, and close the window. Record the
OS, Python/Pygame versions, and observed result in the test execution log.
Windows and macOS results depend on their CI jobs and manual desktop checks;
local Linux headless results alone are not evidence of those platforms passing.
