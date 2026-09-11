# Backfire

A bouncing-ball breaker with one change: every block hangs from the ceiling, and
anything you cut loose **falls, flips, and slams back up** — each block dealing
its own number as damage to whatever was above it.

Break the block holding a slab up and the slab becomes your weapon.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait.

Why this design, what it fixes in the genre, and the measured balance data:
**[DESIGN.md](DESIGN.md)**.

---

## How to play

Drag anywhere to aim, release to fire. Your whole stream of balls goes out along
that line and bounces off the walls and off the blocks.

- The number on a block is how many hits it has left. Each ball takes off your
  **damage**; at zero it shatters and drops coins.
- Green `+1` orbs are a permanent extra ball for the run. Balls pass through them.
- A new row arrives after every shot and pushes everything down. If a block
  reaches the dashed line at your cannon, the run ends.
- Between shots, spend coins on **+1 Ball** or **+1 Damage**.

### The part that matters

Everything is held up by the ceiling, directly or through its neighbours. Break
the one block holding a group and the whole group comes loose, drops, flips, and
rockets back up — each block dealing its own number as damage, piercing upward
until that damage is spent.

If a backfire knocks out another support, it happens again. That is a **chain**,
and chains score far more than careful chipping ever will. A 200-HP block is
worth more dropped than broken.

## What's in the build

- 5-step tutorial on a hand-built board with one unmistakable load-bearing pillar
- One-time cards for ammo orbs, the damage wall, the danger line, and chains
- Pause, game over with a mocked rewarded-ad rescue, Workshop, how-to-play, settings
- Bouncing ball physics with sub-stepping, anti-stall, hurry-up and vacuum timers
- Recursive collapse waves with a chain multiplier
- Permanent meta progression (cores → starting balls, starting damage, coin rate)
- Particles, shards, impact rings, thruster trails, screen shake, floating damage,
  banners, synthesised audio, haptics
- Light and dark themes, reduced-effects mode, progress saved to localStorage

## Files

```
index.html     the game — open this
src/app.html   source (no <html>/<head>/<body>; the artifact host supplies those)
build.sh       wraps src/app.html into the standalone index.html
DESIGN.md      the rationale, the numbers, the measured balance, the risks
```

Edit `src/app.html`, then run `./build.sh`.

## Tuning knobs

Top of the script in `src/app.html`:

- `MAX_BALLS` — the ball cap. With `COST_BALL` and the HP exponent, this is the
  whole difficulty curve.
- `COST_BALL` / `COST_DMG` — both geometric on purpose; see DESIGN.md §5 for what
  happens when ball cost is linear.
- `mkBlock()` — the `Math.pow(L, 1.35)` exponent is the wall's growth rate.
- `makeRow()` — density and the three row shapes (scatter / bridge / pillars).
  Row shape is what decides how often interesting overhangs appear.
- `smash()` — backfire damage and how it pierces.

## Headless hooks

`window.__bf` exposes `fireAt(deg)`, `stats()`, `deepest()`, `totalHp()`,
`buyBall()`, `buyDmg()`, `reset()` and `turbo(n)` (runs the simulation up to 24×
real time). The balance numbers in DESIGN.md were measured through these with
Playwright — worth keeping if you change the curves.
