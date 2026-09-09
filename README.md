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
| Keyboard | `←`/`→` or `A`/`D` to roll, `Space` to fire, `1`–`4` to buy upgrades, `T` for the tuner |

**Upgrades** — spend scrap on damage, fire rate, barrels (up to 5) and shields
(absorb one landing, max 3).

#### Physics tuner

**Tune** in the top bar opens three live dials, applied mid-run and saved per
browser:

| Dial | Range | Effect |
|---|---|---|
| Fall speed | 0.35–1.50× | Gravity. Sets the *tempo* of a bounce only |
| Bounce | 0.50–1.40× | How high orbs reach |
| Drift | 0.30–1.80× | Sideways speed |

Fall speed and bounce are independent because apex height is defined as a
fraction of the field: bounce velocity is derived as `√(2·g·apex)`, so the `g`
in the launch cancels the `g` in the fall. Halving gravity makes an orb take
`1/√0.5` ≈ 1.41× as long to complete a bounce while still reaching exactly the
same height. Bounce period works out to `2·√(2·apex·refHeight / g)` — no screen
dimension in it, which is why the game plays identically at any window size and
why opening the tuner mid-run (which shrinks the field) doesn't disturb the
timing you are tuning.

#### Balance model

The numbers are not eyeballed; they come out of a simulation of ~34 waves
(`sim.js` in the design notes below) built around two rules:

- **Every upgrade track is priced off its own level alone**, so buying one never
  moves another's price: damage `560 × current damage`, rate `5 × current
  shots/sec`, barrels `120 × 3^(n−1)`, shields `70 × 1.26^(wave−1)`. Pricing off
  total DPS instead is tempting — it makes clear time self-correcting — but DPS is
  `damage × rate × barrels`, so a barrel purchase doubles it and every other price
  with it. The damage ladder's shape is then forced: since rate and barrels cap,
  late waves are damage-only, and cumulative spend has to stay proportional to
  damage value or clear time either diverges or collapses to seconds.
- **Wave size is a budget measured in total damage**, and that budget is a
  multiple of one top-tier orb's full cost (the orb plus everything it splits
  into). Sizing the budget this way guarantees the biggest orbs are always
  affordable, so "how many heavies" becomes the difficulty dial and the waves
  that introduce a new orb size don't spike.

Orb HP grows 1.26× per wave, so the top size passes 10,000 HP around wave 22 and
180,000 by wave 34. Damage per bullet passes 200 around upgrade level 30.

#### Documents

| File | Contents |
|---|---|
| [`UNITY_PORT_SPEC.md`](neon-cannon/UNITY_PORT_SPEC.md) | Full implementation spec for rebuilding this game in Unity — coordinate model, every constant, all algorithms, code hierarchy, class reference, test plan. Includes one addition to the design: a Level Cleared panel between waves. |
| [`UNITY_ART_ASSETS.md`](neon-cannon/UNITY_ART_ASSETS.md) | What art the Unity port needs sourced versus what can be generated in-engine. The HTML build ships zero image files, so the list is short. |
