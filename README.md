# Team15_SE_Project
A simple Snake game. This repo holds the SE documents for it.

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
