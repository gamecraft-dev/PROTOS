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

### `prism-breaker/` — Prismbreak

A brick breaker where the colour *is* the number. A brick's hue is derived from
its hit points — `272 − (hp−1)·24.7`, clamped — so violet is a one-hitter, blue
is four, cyan five, green seven, orange eleven, red twelve, and anything tougher
holds at red and darkens toward crimson. A full board reads as a literal prism,
and you can see where the wall is hard without reading a single digit. The ball
is a photon: an additive light source that takes on the colour of whatever it
last broke, trailing a wake split into red, green and blue across the normal of
travel.

**Controls** — drag anywhere to move the paddle, tap to launch. `←`/`→` nudge
and `Space` launches on a desktop.

#### Endless

Rows push in from the top forever and step down toward you.

| | |
|---|---|
| Lives | 3. A ball falling past the paddle costs one |
| Breach | a brick touching the danger line ends the run on the spot — every life at once |
| Energy | every hit charges the bar; a kill pays roughly three to four times a chip |
| Draft | a full bar stops the clock and offers 3 of 16 powerups; take one you already hold and it levels up |
| Scope | powerups die with the run. Cores and Forge ranks do not |

The 16 powerups run from more balls (Fracture, Splitter) through raw damage
(Overcharge, Momentum, Velocity) to area effects (Shatter, Arc), saves
(Barrier, Second Wind) and economy (Resonance, Refraction).

#### The Forge

Three permanent tracks, bought with Cores and shared by both modes.

| Track | Ranks | Range | Cost |
|---|---|---|---|
| Paddle Size | 8 | 118 → 222 px | `40 × 1.55ⁿ` |
| Ball Power | 8 | 2 → 10 damage | `55 × 1.55ⁿ` |
| Fire Rate | 10 | one volley per 10.0 s → 3.0 s | `45 × 1.50ⁿ` |

Fire rate is deliberately the weakest thing you own for a long time: it starts
at one volley every ten seconds and bottoms out at three, and the run-scoped
Autocannon that multiplies it is floored at one second, so the paddle guns can
never become the primary weapon.

Classic mode is stubbed on the menu — no levels are built yet.

#### What actually makes a brick breaker work

Every number here came out of instrumented headless play rather than taste, and
the three findings that mattered were all surprises.

**The first build was mostly dead air.** Instrumented headless play measured
**0.26 damaging hits per second** — the ball touched a brick once every four
seconds and spent the rest of the run crossing 800 px of nothing. Four things
fixed it together: a wider, denser field (10 columns, fourteen starting rows,
so the wall is a wall), a much faster ball, the direction band below, and the
spawn rule below that.

**A ball that travels straight up is a stalled run.** The paddle bounce takes
its angle from where the ball lands on the paddle, so a player who tracks it
perfectly hits it dead centre and sends it vertically, where it oscillates in
one column touching nothing. The fix is to re-derive the velocity from its angle
every frame and clamp that angle into a diagonal band, 17°–70° off horizontal,
which guarantees the ball sweeps about five columns per length of the field. An
A/B on the finished build with powerups suppressed, so every counted hit is a
ball touching a brick: **1.44 hits/s with the band against 1.06 without**, and
the run that had it was still alive at wave 27 when the one that didn't had
already breached at wave 16.

**Difficulty cannot come from hit points here**, because hit points are the
colour language. Left to run, the hue wheel loops past red back toward violet
and a lethal wall starts looking like a harmless one — so the walk stops at red
and darkens instead, and hp climbs slowly enough that the spectrum is still
saying something useful deep into a run: hp reaches 12, the end of the ramp,
around wave 35. The pressure comes from cadence instead. A row costs
`cols × fill × avgHp` damage and arrives every `gap` seconds, so the wall demands
about `1.05 × wave` damage per second once the gap bottoms out at wave 26. That
line rises forever while ball damage and ball count both cap, which is what
makes an endless run finite however well it is played.

What that produces, from a headless auto-player on a fresh save: the opening
violet wall is stripped from 69 bricks to 22 inside the first minute, the board
is back to 71 bricks and ten rows deep by wave 40, 103 bricks and thirteen rows
by wave 60 — where the player first falls properly behind, landing 40 damage a
second against a wall demanding 64 — then claws it back to 26 bricks by wave 100
before it builds again. The ebb and flow is the point; earlier tunings held a
flat 20 bricks for twelve minutes and never threatened anything.

One honest limitation: that auto-player tracks the ball perfectly and so never
loses one, and dropping balls is the real failure mode. It survives past wave
200 under constant pressure rather than dying, and the only ways to kill it
would be to make hit points climb fast enough to burn through the spectrum in
twenty waves, or to cut the powerups back until the roguelite stops paying out.
Both cost more than they buy. A human dies in the wave 20–60 band, where the
wall first gets ahead.

**Out-clearing the spawn rate used to be punished with an empty screen.** A
strong player would strip the board and then stand there waiting for one row
every nine seconds — measured at 0 bricks on the field by wave 13. The fix is a
spawn clock that runs faster as the field empties, and the instructive part was
getting that wrong first. Set wide and strong — kicking in below twenty-five
bricks, up to 3.4× — it stops being a rescue and becomes the *equilibrium*: a
flawless run then sat pinned at 13–28 bricks parked near the top of the field
for twelve straight minutes, because every point of surplus damage was being
absorbed into the wave counter instead of into a wall. And since wave drives hit
points, the run inflated rather than ending: wave 214 on a fresh save, wave 287
with the Forge maxed. Narrowed to below sixteen bricks and 2.6×, it covers the
dead air and nothing else, and the cadence above does the work it was always
supposed to do.

The other thing holding the board flat was multiball. Fracture and Splitter
together were putting eight balls in play, measured at 8.6 brick contacts a
second — at which point the paddle stops mattering, because something is always
coming back whatever you do. Capping the field at seven balls took that to 5.0
and handed the wall its half of the fight back.

One more thing that only showed up in a screenshot: seeding the opening wall as
waves 1–14 and then winding the counter back to 1 runs the difficulty ramp
*twice*, so the board reads as two stacked spectra — violet, green, violet,
green. Since hue is hit points, that misreads the hardest part of the wall as
the softest. The seeded rows are generated flat instead, and the gradient stays
monotone for the whole run.
