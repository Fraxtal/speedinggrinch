# Speeding Grinch
A 2D side-scrolling platformer built in Python with Pygame, demonstrating movement inspired by SpeedRunners. 

# Narrative
You play as a toy assembly elf attempting to escape Santa's factory before you become the next missing worker. Avoid management, jump over obstacles, and reach the goal at the end of each level.

==============================================================================================

## Requirements
- Python 3.10+
- pygame-ce

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to run the game
Navigate into the `src/` directory and run `main.py` directly:

```bash
cd src
python main.py
```

## Controls
Controls can be modified through settings from the main menu or the pause menu.

|   Action    | Default Key            |
|-------------|------------------------|
| Move Left   | A / Left Arrow         |
| Move Right  | D / Right Arrow        |
| Jump        | Space                  |
| Double Jump | Space (while airborne) |
| Dash        | Shift                  |
| Pause       | Escape                 |

## Gameplay
**Movement** — Run, jump, and double jump across platforms. The player sprite animates across idle, run, jump, fall, dash, and hurt states.

**Dash** — Triggers a short burst of speed with a brief cooldown. The stamina bar in the HUD shows when the dash is ready. While dashing, the player's hitbox narrows and enemy detection is bypassed.

**HP** — The player has 100 HP displayed in the top-left HUD. Taking damage from hazards reduces HP by 10. A smooth animation trails behind the bar to show recent damage. Reaching 0 HP ends the run.

**Hazards** — Present boxes stun the player on contact, dealing damage and knocking them back. Spikes deal damage on touch. Both have a cooldown so the player cannot be chain-damaged immediately.

**Enemies** — Patrol elves walk back and forth on their platform. Each has a visible detection cone in front of them. Walking into the cone ends the run with a "Caught" screen. Dashing through the cone makes you invisible to detection.

## Levels
**Level 1 — The Factory**
The starting level set inside Santa's industrial factory. Introduces walls, floating platforms, present box hazards, and patrolling enemies. Ends at a glowing goal portal on the right side of the 7000px world.

**Level 2 — The Snow Fields**
An outdoor winter environment with a snow-covered tileset, a pixel art mountain background, and falling snow particles. Features wider platform gaps, spike hazards on floating platforms, and a higher enemy density than Level 1. Set across an 8000px world.

Completing Level 1 automatically transitions into Level 2 via a continuation story screen.

## Menus & Screens
**Main Menu** — Displays a live scrolling preview of Level 1 in the background. Buttons for Start, Settings, and Quit with hover sound effects.

**Story Scroll** — A parchment-style narrative screen shown before each level. Fades in and can be dismissed early with any key or mouse click.

**Pause Menu** — Accessible mid-game with Escape. Options to resume, open settings, or quit to the main menu.

**Settings Screen** — Remap jump and dash keys and adjust music volume. Accessible from both the main menu and the pause menu.

**Victory Screen** — Plays after completing the final level, with a dedicated animation and sound effect.

**Overlay Screens** — "You Died", "Caught!", and "You Win" overlays shown on the relevant game-ending events, each returning to the menu after a short hold.

## Credits

Built with [pygame-ce](https://pyga.me). Sprite assets from the Forest Ranger character pack. Background and tile assets sourced from itch.io and craftpix.net.