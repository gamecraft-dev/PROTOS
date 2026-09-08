# PROTOS

Playable game prototypes. Each one is a self-contained HTML file — no build step,
no dependencies. Open the file in a browser, or serve the folder with any static
server.

## Prototypes

### `neon-cannon/` — Neon Cannon

A neon arcade defence game. A wheeled cannon holds the ground line while numbered
orbs drop in from both flanks and bounce. Hold to fire, drag to roll. Every hit
takes the orb's number down; at zero it detonates, and anything larger than the
smallest size splits into two halves first. Let one land on the cannon and the run
is over.

**Controls**

| | |
|---|---|
| Touch | Hold anywhere to fire, drag left/right to roll |
| Mouse | Hold to fire, drag to roll |
| Keyboard | `←`/`→` or `A`/`D` to roll, `Space` to fire, `1`–`4` to buy upgrades |

**Upgrades** — spend scrap on damage, fire rate, barrels (up to 5) and shields
(absorb one landing, max 3).

#### Balance model

The numbers are not eyeballed; they come out of a simulation of ~34 waves
(`sim.js` in the design notes below) built around two rules:

- **Upgrade price scales with current DPS**, not with upgrade level:
  `price = 33 × DPS × relative gain`. This makes clear time self-correcting — it
  converges on `K / (reward × h/(h−1))` ≈ 20–30s a wave no matter how far the run
  goes, instead of the player either stalling out or trivialising late waves.
- **Wave size is a budget measured in total damage**, and that budget is a
  multiple of one top-tier orb's full cost (the orb plus everything it splits
  into). Sizing the budget this way guarantees the biggest orbs are always
  affordable, so "how many heavies" becomes the difficulty dial and the waves
  that introduce a new orb size don't spike.

Orb HP grows 1.26× per wave, so the top size passes 10,000 HP around wave 22 and
180,000 by wave 34. Damage per bullet passes 200 around upgrade level 30.
