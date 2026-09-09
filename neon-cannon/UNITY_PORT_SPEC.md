# Neon Cannon — Unity Port Specification

A complete implementation spec for rebuilding `neon-cannon/index.html` in Unity as a
1:1 gameplay replica, plus one requested addition (a **Level Cleared** panel between
waves).

Every constant in this document is taken from the shipped HTML build. Where a value is
derived rather than literal, the derivation is shown. Where the Unity idiom should
differ from the JavaScript, the divergence is called out explicitly under
**Divergence** so nothing is changed silently.

**Source of truth:** `neon-cannon/index.html` (this repository). If the two ever
disagree, the HTML is correct for gameplay and this document is the bug.

---

## Table of contents

1. [Scope and definition of done](#1-scope-and-definition-of-done)
2. [Target configuration](#2-target-configuration)
3. [Coordinate system and the scaling model](#3-coordinate-system-and-the-scaling-model)
4. [Game state machine](#4-game-state-machine)
5. [Constant tables](#5-constant-tables)
6. [Orb physics](#6-orb-physics)
7. [Wave generation](#7-wave-generation)
8. [Spawning](#8-spawning)
9. [Cannon](#9-cannon)
10. [Input](#10-input)
11. [Bullets and collision](#11-bullets-and-collision)
12. [Destruction and splitting](#12-destruction-and-splitting)
13. [Economy and upgrades](#13-economy-and-upgrades)
14. [Shield and loss condition](#14-shield-and-loss-condition)
15. [Level Cleared panel (new)](#15-level-cleared-panel-new)
16. [Physics tuner](#16-physics-tuner)
17. [Presentation](#17-presentation)
18. [UI layout](#18-ui-layout)
19. [Persistence](#19-persistence)
20. [Number formatting](#20-number-formatting)
21. [Numeric types and rounding traps](#21-numeric-types-and-rounding-traps)
22. [Code hierarchy](#22-code-hierarchy)
23. [Class reference](#23-class-reference)
24. [Execution order and the frame](#24-execution-order-and-the-frame)
25. [Object pooling](#25-object-pooling)
26. [Test plan](#26-test-plan)
27. [Divergence register](#27-divergence-register)

---

## 1. Scope and definition of done

### 1.1 What the game is

A single-screen arcade defence game. A wheeled cannon sits on a ground line at the
bottom of a portrait playfield. Numbered orbs enter from the left and right edges,
fall under gravity, and bounce off the ground indefinitely. The player holds to fire
upward and drags left/right to roll the cannon. Each bullet subtracts its damage from
the orb's number; at zero the orb detonates, and every orb above the smallest size
splits into two half-strength orbs of the next size down before it dies. If any orb
touches the cannon the run ends, unless a shield charge absorbs it.

Between waves the player spends scrap on damage, fire rate, barrels and shields. Orb
HP grows exponentially per wave, so the run is a race between the upgrade curve and
the HP curve.

### 1.2 Definition of done

The port is complete when all of the following hold:

| # | Acceptance criterion | How to verify |
|---|---|---|
| A1 | A tier-4 orb's bounce period is 1.95 s ±0.05 at default tuning | `PhysicsParityTests.BouncePeriod` |
| A2 | Bounce apex is independent of the fall-speed dial to within 1% | `PhysicsParityTests.ApexInvariance` |
| A3 | Wave *n* orb composition matches the reference table in §7.5 exactly | `WaveBuilderTests` with a seeded RNG |
| A4 | Upgrade prices at any given upgrade state match §13 exactly | `EconomyParityTests` |
| A5 | The damage ladder matches the reference sequence in §5.4 for L = 1..60 | `EconomyParityTests.DamageLadder` |
| A6 | A tier-4 orb fully cleared yields exactly `maxHP × 5` total damage dealt | `WaveBuilderTests.SplitCost` |
| A7 | Bullets never tunnel through a tier-0 orb at 15 fps | `PhysicsParityTests.SweptCollision` |
| A8 | Sustained 60 fps on a 2019-class mid-range phone at 80 orbs + 120 bullets | Profiler capture |
| A9 | Level Cleared panel appears after every wave and gates progression | Manual |
| A10 | Tuner values survive an app restart | Manual |

---

## 2. Target configuration

| Item | Value | Note |
|---|---|---|
| Unity | 2022.3 LTS or 6000.0 LTS | Both verified idioms; 6 LTS preferred for new work |
| Render pipeline | **URP** with the **2D Renderer** | Bloom is mandatory for the neon look |
| Colour space | **Linear** | Gamma space makes additive bloom muddy |
| Packages | `com.unity.render-pipelines.universal`, `com.unity.inputsystem`, `com.unity.textmeshpro`, `com.unity.test-framework` | |
| Input | **Input System** (new) | Touch + mouse + keyboard through one action map |
| UI | **uGUI** (Canvas + TextMeshPro) | See §18.1 for why not UI Toolkit |
| Orientation | Portrait only | Landscape is out of scope, as in the HTML |
| Target frame rate | 60 (`Application.targetFrameRate = 60`) | Also set `QualitySettings.vSyncCount = 0` on mobile |
| Physics2D | **Disabled/unused** | See §6.1 |

**HDR and bloom.** The 2D Renderer asset must have HDR enabled. All neon colours are
authored as HDR colours with intensity above 1.0 so the bloom threshold catches them.
A Global Volume carries one Bloom override:

| Bloom parameter | Value |
|---|---|
| Threshold | 0.95 |
| Intensity | 1.15 |
| Scatter | 0.72 |
| Tint | white |
| High Quality Filtering | on (off on low-end tier) |

---

## 3. Coordinate system and the scaling model

This is the single most error-prone part of the port. Read it before writing any
gameplay code.

### 3.1 What the HTML does

The HTML canvas has its origin at the **top-left** with **y increasing downward**, and
its size in CSS pixels changes with the browser window. To stay consistent across
screen sizes, every physics constant is authored in *reference pixels* against a
reference field height of 780, and multiplied at use time by a scale factor:

```
S        = canvasHeight / 780
groundY  = canvasHeight - 30 * S
```

### 3.2 What Unity should do instead

In Unity an orthographic camera performs that scaling for free. **Fix the world size
and let the camera handle resolution.** The scale factor `S` therefore becomes a
compile-time constant of 1, and disappears from all gameplay code.

```
UNITS_PER_REF_PX = 0.01          // every reference-pixel constant ÷ 100
FIELD_HEIGHT     = 7.80          // world units  (780 ref px)
GROUND_STRIP     = 0.30          // world units  (30 ref px)
FIELD_TOP        = 7.50          // world units above the ground line
Camera.orthographicSize = 3.90   // = FIELD_HEIGHT / 2
```

**Origin:** world **y = 0 is the ground line**, +y is up. World **x = 0 is the
horizontal centre** of the playfield.

### 3.3 Conversion reference

| Quantity | HTML | Unity world |
|---|---|---|
| Ground line | `groundY = H - 30·S` | `y = 0` |
| Canvas top | `y = 0` | `y = +7.50` |
| Canvas bottom | `y = H` | `y = -0.30` |
| Left edge | `x = 0` | `x = -playWidth/2` |
| Any HTML y | `yHtml` | `yWorld = 7.50 - yHtml·0.01` |
| Any HTML x | `xHtml` | `xWorld = (xHtml - W/2)·0.01` |
| Any speed / accel | `v·S` | `v · 0.01` |

> **Watch the two different heights.** Bounce apex is a fraction of the **full field
> height 7.80**, not of the 7.50 above the ground line. A tier-4 apex is
> `0.58 × 7.80 = 4.524` units above the ground, not `0.58 × 7.50`. Getting this wrong
> shortens every bounce by 4%.

### 3.4 Playfield width and aspect

Orthographic size fixes the *vertical* extent; width follows the aspect ratio. The
HTML clamps its cabinet to 600 CSS px wide, so:

```
camWidth   = 2 * orthographicSize * Screen.width / Screen.height
playWidth  = min(camWidth, MAX_PLAY_WIDTH)      // MAX_PLAY_WIDTH = 6.00 (600 ref px)
```

`playWidth` — not `camWidth` — is what wall collisions, spawn positions and cannon
clamping use. On a display wider than the clamp, dress the margins with the backdrop
and a frame; never let orbs travel into them.

`FieldGeometry` (§23.4) owns these numbers and is the only place that reads
`Screen.width`.

### 3.5 Why bounce timing is resolution-independent

Worth understanding because it justifies the whole model. Bounce period is

```
T = 2v/g,   v = √(2 · g · apexFrac · H),   g = GRAVITY · fall
⇒ T = 2·√(2 · apexFrac · H / (GRAVITY · fall))
```

`H` here is the *world* field height, a constant. No screen dimension appears in `T`.
That is why the tuner drawer can shrink the playfield mid-run without disturbing the
timing the player is tuning, and why the game feels identical on every device.

---

## 4. Game state machine

```
        ┌──────┐
        │ Boot │  load config, save data, warm pools
        └──┬───┘
           v
        ┌──────┐   Start pressed
        │ Menu │ ─────────────────┐
        └──────┘                  v
           ^                ┌───────────┐  banner 1.7s, spawn timer armed
           │                │ WaveIntro │
           │                └─────┬─────┘
           │                      v
           │                ┌──────────┐   last orb destroyed
           │                │ Playing  │ ────────────────────┐
           │                └────┬─────┘                     v
           │   orb hits cannon,  │                    ┌──────────────┐
           │   no shield         │                    │ WaveCleared  │  NEW (§15)
           │                     v                    └──────┬───────┘
           │              ┌──────────┐                       │ Next pressed
           └───────────── │ GameOver │                       │
             Rebuild      └──────────┘                       v
                                                      (WaveIntro, n+1)
```

```csharp
public enum GameState { Boot, Menu, WaveIntro, Playing, WaveCleared, GameOver }
```

**Simulation ticks only in `Playing`.** In every other state the orb/bullet/cannon
integrator is skipped; cosmetic systems (particles, camera shake, UI animation) keep
running on unscaled time.

> **Do not use `Time.timeScale = 0` to pause.** Panel tweens, the banner animation and
> particle fade-outs all read time. A state flag is unambiguous; `timeScale` forces
> every cosmetic system onto `unscaledDeltaTime` and one missed conversion freezes the
> UI.

**Sub-phase inside `Playing`.** The wave director carries its own phase, matching the
HTML's `G.phase`:

```csharp
public enum WavePhase { Spawning, Fighting }
```

- `Spawning` — orbs still queued; release one every `SPAWN_GAP`.
- `Fighting` — queue empty; waiting for the field to clear.

The transition `Fighting → (no orbs alive) → GameState.WaveCleared` is the wave-clear
trigger. Note it must check **both** that the queue is empty and that no orbs are
alive; checking only "no orbs alive" fires spuriously in the gap before the first
spawn.

---

## 5. Constant tables

All values are the shipped HTML values. World-unit columns are HTML ÷ 100 per §3.2.

### 5.1 Field and physics

| Name | HTML | World units | Notes |
|---|---|---|---|
| `REF_HEIGHT` | 780 | 7.80 | Field height |
| `GRAVITY` | 1450 | 14.50 u/s² | Before the fall dial |
| `GROUND_STRIP` | 30 | 0.30 | Below the ground line |
| `BULLET_SPEED` | 1550 | 15.50 u/s | |
| `BULLET_RADIUS` | 5 | 0.05 | |
| `MAX_ORBS` | 80 | — | Split is suppressed above this |
| `MAX_PARTICLES` | 420 | — | Burst requests are truncated |
| `SPAWN_GAP` | 1.15 s | — | Between arrivals |
| `FIRST_SPAWN_DELAY` | 1.0 s | — | After a wave starts |
| `DT_CLAMP` | 0.034 s | — | Max integrated step |

### 5.2 Orb tiers

Tier 0 is the smallest. Tier 4 is the largest.

| Tier | Radius (world) | Apex (fraction of 7.80) | Apex (world) | Drift (u/s) | Wave-1 HP | Hue |
|---|---|---|---|---|---|---|
| 0 | 0.13 | 0.30 | 2.340 | 1.30 | 3 | 190° cyan |
| 1 | 0.21 | 0.38 | 2.964 | 1.18 | 7 | 100° lime |
| 2 | 0.31 | 0.45 | 3.510 | 1.06 | 16 | 45° amber |
| 3 | 0.43 | 0.52 | 4.056 | 0.95 | 38 | 325° magenta |
| 4 | 0.57 | 0.58 | 4.524 | 0.85 | 90 | 272° violet |

Hue is HSL hue in degrees at 100% saturation. Orb stroke lightness is 64%, rising to
94% on the hit flash.

Derived bounce speeds at default tuning (`fall = 0.65`, `bounce = 1.00`):

| Tier | Bounce speed (u/s) | Bounce period (s) |
|---|---|---|
| 0 | 6.641 | 1.409 |
| 1 | 7.475 | 1.586 |
| 2 | 8.134 | 1.726 |
| 3 | 8.744 | 1.856 |
| 4 | 9.234 | 1.959 |

Computed as `v = √(2 · 14.50 · 0.65 · apexFrac · 7.80)` and `T = 2v / (14.50 · 0.65)`.

### 5.3 Growth and economy

| Name | Value | Meaning |
|---|---|---|
| `HP_GROWTH` | 1.26 | Orb HP multiplier per wave |
| `REWARD_RATE` | 0.40 | Scrap per point of orb max HP |
| `PRICE_DAMAGE` | 560 | × current damage per bullet |
| `PRICE_RATE` | 5 | × current shots per second |
| `PRICE_BARREL` | 120 | × `PRICE_BARREL_STEP^(barrels-1)` |
| `PRICE_BARREL_STEP` | 3 | |
| `PRICE_SHIELD` | 70 | × `HP_GROWTH^(wave-1)` |
| `MIN_PRICE` | 15 | Price floor |
| `START_SCRAP` | 70 | |
| `START_SHIELDS` | 1 | One free hit to learn on |
| `WAVE_BONUS(n)` | `30 + 8n` | Scrap awarded on clearing wave *n* |
| `RATE_BASE` | 3.4 shots/s | Fire rate at level 1 |
| `RATE_GROWTH` | 1.085 | Per fire-rate level |
| `RATE_CAP` | 22 shots/s | Reached at level 24 |
| `MULTI_MAX` | 5 barrels | |
| `SHIELD_MAX` | 3 charges | |
| `DAMAGE_GROWTH` | 1.16 | Per damage level |

### 5.4 Damage ladder

```
DMG[1] = 1
DMG[L] = max( DMG[L-1] + 1, round( DMG[L-1] × 1.16 ) )
```

The `+1` floor keeps early levels meaningful before the 16% compounding takes over.
Precompute to L = 400 at boot into a `double[]`.

Reference values — **the port must reproduce these exactly**:

| L | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| DMG | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |

| L | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| DMG | 12 | 14 | 16 | 19 | 22 | 26 | 30 | 35 | 41 | 48 |

| L | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|
| DMG | 56 | 65 | 75 | 87 | 101 | 117 | 136 | 158 | 183 | 212 |

Damage passes 200 per bullet at level 30.

### 5.5 Wave bands

| Band | First wave | Top tier |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 3 | 2 |
| 3 | 6 | 3 |
| 4 | 11 | 4 |

`bandOf(n)` returns the last band whose first wave is ≤ n.

### 5.6 Palette

Authored as HDR colours. LDR hex is the CSS value; intensity is the HDR multiplier
that pushes it past the bloom threshold.

| Token | Hex | HDR intensity | Used for |
|---|---|---|---|
| `void` | `#07030f` | — | Page ground |
| `deep` | `#0e0820` | — | Playfield ground |
| `panel` | `#150d2a` | — | Console/panel fill |
| `edge` | `#2c1a52` | — | Borders, grid |
| `cyan` | `#00eaff` | 2.2 | Cannon, bullets, ground line, wave number |
| `magenta` | `#ff2d95` | 2.0 | Wheels, danger vignette, tier-3 orbs |
| `violet` | `#8b5cff` | 1.8 | Shields, tuner, grid |
| `lime` | `#c6ff3d` | 2.0 | Scrap |
| `amber` | `#ffb52e` | 2.0 | Fire rate, tier-2 orbs |
| `ink` | `#ece2ff` | 1.0 | Body text, orb numbers |
| `muted` | `#8d7bb8` | — | Labels |

---

## 6. Orb physics

### 6.1 Do not use Rigidbody2D

**Requirement: orb motion is a hand-written integrator. Physics2D is not used for
gameplay at all.**

Three reasons, all of which will bite a `Rigidbody2D` implementation:

1. **The apex must be exact and constant.** A bounce is not a restitution response —
   the orb's upward speed is *recomputed from scratch* on every ground contact so it
   reaches a fixed apex forever. A `PhysicsMaterial2D` with bounciness 1.0 accumulates
   floating-point error and the apex visibly drifts within a minute.
2. **The fall dial must be per-orb, not global.** `Physics2D.gravity` is global and
   would drag particles and any future rigidbodies along with it.
3. **The entry gate.** Orbs spawn *outside* the wall and must not collide with it
   until fully inside (§6.4). That is trivial as a flag and awkward as a collider
   layer dance.

Colliders may still be added as triggers if something else needs them, but nothing in
this spec reads them.

### 6.2 Orb state

```csharp
public struct OrbState {
    public int    Tier;
    public double Hp;          // current
    public double MaxHp;       // original — drives score, scrap and split HP
    public Vector2 Position;   // world, y = 0 at ground
    public Vector2 Velocity;   // world u/s
    public float  Radius;      // world
    public float  Flash;       // 1 → 0, hit feedback
    public float  Wobble;      // radians, cosmetic scale pulse
    public bool   Entered;     // has fully cleared the spawn wall
}
```

### 6.3 Integration

Per fixed step of `dt`:

```
velocity.y -= GRAVITY * tune.fall * dt        // note the sign: +y is up in Unity
position  += velocity * dt
flash      = max(0, flash - dt * 4)
wobble    += dt * 2
```

### 6.4 Walls, ceiling, ground

Order matters — apply exactly as written.

```
// entry gate: only start colliding once fully on-field
if (!entered && position.x - radius > -halfWidth
             && position.x + radius <  halfWidth) entered = true;

if (entered) {
    if (position.x - radius < -halfWidth) { position.x = -halfWidth + radius; velocity.x =  abs(velocity.x); }
    else if (position.x + radius > halfWidth) { position.x =  halfWidth - radius; velocity.x = -abs(velocity.x); }
}

// ceiling: soft, kills 60% of the speed
if (position.y + radius > FIELD_TOP) { position.y = FIELD_TOP - radius; velocity.y = -abs(velocity.y) * 0.4f; }

// ground: hard, recomputed to a fixed apex
if (position.y - radius <= 0f) {
    position.y = radius;
    velocity.y = BounceSpeed(tier);
    Vfx.Burst(position.x, 0f, hue, 3, 1.30f);
    Shake.Add(0.02f + tier * 0.02f);
}
```

**The ground test is containment, not sweep.** Because the orb is clamped to
`y = radius` whenever it is at or below the ground, it can never tunnel through
regardless of step size. No swept test is needed here (unlike bullets, §11.3).

### 6.5 Bounce speed

```csharp
float BounceSpeed(int tier) =>
    Mathf.Sqrt(2f * GRAVITY * tune.fall * TIER_APEX[tier] * tune.bounce * FIELD_HEIGHT);
```

Resulting apex above the ground:

```
apex = v² / (2g)
     = (2 · G · fall · apexFrac · bounce · H) / (2 · G · fall)
     = apexFrac · bounce · H
```

The `fall` term cancels. **Fall speed changes tempo only; bounce changes height.**
This is the property the tuner UI advertises and `PhysicsParityTests.ApexInvariance`
asserts.

### 6.6 Threat readout

Recomputed every step across all orbs, feeding the danger vignette (§17.6):

```
near   = 1 - clamp(|orb.x - cannon.x| / (playWidth * 0.4), 0, 1)
low    = clamp(1 - orb.y / (FIELD_HEIGHT * 0.45), 0, 1)
danger = max over all orbs of (near * low)
```

The vignette is drawn only when `danger > 0.35`, at alpha `(danger - 0.35) / 0.65`.

---

## 7. Wave generation

### 7.1 The problem this solves

A naive "wave *n* has *n* orbs" schedule breaks in two ways: the wave that first
introduces a new orb size spikes difficulty ~3.4×, and a flat damage budget can end up
smaller than one top-tier orb costs, in which case the biggest orbs silently never
spawn. Both bugs were present in earlier drafts of the HTML and are fixed by the
algorithm below. **Do not simplify it.**

### 7.2 Full cost of an orb

Clearing a tier-*t* orb of HP *h* requires the player to deal damage not just to it
but to every orb it splits into. Each split layer halves HP but doubles the count, so
each layer costs the same *h*:

```
fullCost(t, h) = h × (t + 1)
```

A tier-4 orb of 10,000 HP therefore costs 50,000 total damage to clear. This is the
unit the budget is denominated in.

### 7.3 Algorithm

```csharp
List<OrbSpawn> BuildWave(int n, IRandom rng) {
    double mult = Math.Pow(HP_GROWTH, n - 1);
    double HpOf(int t)   => Math.Max(1, RoundHalfUp(TIER_HP[t] * mult));
    double CostOf(int t) => HpOf(t) * (t + 1);

    var (firstWave, top) = BandOf(n);

    // Budget is a MULTIPLE OF ONE TOP-TIER ORB'S FULL COST, so the largest size is
    // always affordable and "how many heavies" is the difficulty dial.
    double load   = Math.Min(4.5, 1.0 + 0.45 * (n - firstWave));
    double budget = CostOf(top) * load;

    var plan = new List<OrbSpawn>();
    for (int guard = 0; guard < 40 && plan.Count < 10; guard++) {
        int t = (top > 0 && rng.NextDouble() < 0.3) ? top - 1 : top;   // 30% variety
        while (t > 0 && CostOf(t) > budget * 1.05) t--;                // step down to fit
        if (CostOf(t) > budget * 1.05) break;                          // even tier 0 won't fit

        plan.Add(new OrbSpawn(t, HpOf(t)));
        budget -= CostOf(t);
        if (budget <= CostOf(0) * 0.5) break;                          // remainder too small
    }
    if (plan.Count == 0) plan.Add(new OrbSpawn(top, HpOf(top)));       // never empty

    for (int i = 0; i < plan.Count; i++)                               // alternate flanks
        plan[i].Side = (i % 2 == 0) ? -1 : +1;

    return plan;
}
```

The `× 1.05` slack lets an orb that slightly overshoots the remaining budget still be
placed, which keeps waves from ending on an awkward single tier-0 orb.

### 7.4 Banner subtitle

| Condition | Subtitle |
|---|---|
| `plan.Count == 1` | `Solitary` |
| ≥ 5 orbs at the band's top tier | `Heavies` |
| otherwise | `Incoming` |

### 7.5 Reference curve

Produced by the balance simulation the HTML was tuned against, assuming a player who
spends greedily on the best DPS-per-scrap upgrade. Use this to validate the port —
`bigHP` and `waveDamage` are deterministic given the same RNG sequence; clear time
depends on purchase order.

| Wave | Top tier | Orbs | Largest orb HP | Total wave damage | Clear time (s) | Damage / rate / barrels |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 7 | 14 | 4 | 1 / 3.4 / 1 |
| 3 | 2 | 1 | 25 | 75 | 13 | 1 / 6.0 / 1 |
| 6 | 3 | 1 | 121 | 484 | 25 | 1 / 9.8 / 2 |
| 10 | 3 | 8 | 304 | 3,384 | 26 | 2 / 22.0 / 3 |
| 11 | 4 | 1 | 908 | 4,540 | 17 | 3 / 22.0 / 4 |
| 15 | 4 | 7 | 2,288 | 31,981 | 36 | 8 / 22.0 / 5 |
| 20 | 4 | 10 | 7,266 | 163,326 | 31 | 48 / 22.0 / 5 |
| **22** | 4 | 10 | **11,535** | 259,282 | 27 | 87 / 22.0 / 5 |
| 26 | 4 | 10 | 29,074 | 653,524 | 24 | 246 / 22.0 / 5 |
| 30 | 4 | 10 | 73,280 | 1,647,183 | 22 | 695 / 22.0 / 5 |
| 34 | 4 | 10 | 184,702 | 4,151,691 | 22 | 1,694 / 22.0 / 5 |

Orb HP passes 10,000 at wave 22. Across all 34 waves clear time spans 4–39 s and
averages 25 s, settling at 22–27 s once damage is the only live track. The ridge at
waves 13–18 (up to 39 s) is where rate and barrels have both capped and damage has not
yet compounded — an intended difficulty crest, not a stall.

Clear time is only reproducible if the simulated player buys the way the reference
player does (best relative-DPS-gain per scrap); `bigHP` and `waveDamage` are
deterministic given the same RNG sequence and are the columns to assert against.

---

## 8. Spawning

While `WavePhase.Spawning`, decrement a timer and release one orb when it expires.

```
timer = FIRST_SPAWN_DELAY (1.0 s) when the wave starts
on expiry: release next queued orb; timer = SPAWN_GAP (1.15 s)
when the queue empties: phase = Fighting
```

Release parameters:

| Property | Value |
|---|---|
| x | `side < 0 ? -halfWidth - radius·0.8 : +halfWidth + radius·0.8` |
| y | uniform random in `[FIELD_TOP - 0.28·H, FIELD_TOP - 0.15·H]` → **[5.316, 6.330]** world |
| velocity.x | `TIER_DRIFT[tier] × tune.drift × (side < 0 ? +1 : -1)` |
| velocity.y | 0 |
| `Entered` | `false` |

Track `biggestOrbSeen = max(biggestOrbSeen, hp)` at release for the game-over readout.

---

## 9. Cannon

### 9.1 Geometry

All world units, with `y = 0` the ground line and `cx` the cannon's x.

| Part | Value |
|---|---|
| Wheel radius | 0.11 |
| Wheel centres | `(cx ± 0.168, y = 0.11)` |
| Body width | 0.56 (half-width **0.28**) |
| Body height | 0.20 |
| Body bottom | `y = 0.0825` (= wheelRadius × 0.75) |
| Body top | `y = 0.2825` |
| Barrel length | 0.34 |
| Barrel width | 0.11 |
| Muzzle (rest) | `y = 0.6225` |
| Muzzle (recoiled) | `y = 0.6225 - recoil × 0.07` |

Chassis outline is a trapezoid: `(cx ± 0.28, 0.0825)` at the base, `(cx ± 0.2016,
0.2825)` at the top.

### 9.2 Collision box

```
x ∈ [cx - 0.28, cx + 0.28]
y ∈ [0, 0.2825]
```

**The barrel is deliberately excluded** — an orb clipping the barrel tip does not end
the run. This is a fairness allowance, not an oversight; keep it.

### 9.3 Movement

```
target += inputDelta                       // §10
target  = clamp(target, -halfWidth + 0.28, halfWidth - 0.28)
x      += (target - x) * min(1, dt * 22)   // smoothing
x       = clamp(x, -halfWidth + 0.28, halfWidth - 0.28)
```

> **Divergence D1 (recommended).** `min(1, dt·22)` is frame-rate dependent. With the
> fixed-step loop of §24 it is deterministic, so it can be kept verbatim. If you run
> the sim on variable `deltaTime` instead, use
> `x = Mathf.Lerp(x, target, 1f - Mathf.Exp(-22f * dt))`, which is the frame-rate
> independent form of the same curve.

### 9.4 Cosmetic state

| Field | Behaviour |
|---|---|
| `recoil` | Set to 1 on fire; `recoil -= dt × 7`, floored at 0. Drives barrel offset and muzzle glow. |
| `spin` | `spin += (target - x) × 0.0025 + sign(target - x) × dt × 1.2`. Wheel rotation. |
| `invuln` | Set to 1.5 s when a shield absorbs. Blinks at `floor(time × 14) % 2`, alpha 0.35. |

### 9.5 Firing

```
cooldown -= dt
if (firing && cooldown <= 0) Fire();
```

`Fire()` emits `multi` bullets, sets `recoil = 1`, sets `cooldown = 1 / rate`, and
spawns 4 muzzle particles (`hue 190`, life 0.18 s, velocity x ∈ [-0.70, 0.70],
y ∈ [0.60, 2.60] u/s).

Per bullet *i* of *n*:

```
off   = i - (n - 1) / 2            // symmetric: -1, 0, +1 for n = 3
angle = 90° + off × 0.075 rad      // up, fanned
origin = (cx + off × 0.05, muzzleY)
velocity = (cos angle, sin angle) × BULLET_SPEED
damage   = DMG[damageLevel]
```

---

## 10. Input

One `InputActionAsset` with a `Gameplay` map.

| Action | Type | Bindings |
|---|---|---|
| `Point` | Value / Vector2 | `<Pointer>/position` |
| `Press` | Button | `<Pointer>/press` |
| `Move` | Value / Axis | `<Keyboard>/leftArrow` ↔ `rightArrow`, `a` ↔ `d` |
| `Fire` | Button | `<Keyboard>/space` |
| `Upgrade1..4` | Button | `<Keyboard>/1..4` |
| `ToggleTuner` | Button | `<Keyboard>/t` |
| `Confirm` | Button | `<Keyboard>/enter` |

### 10.1 Drag model — relative, not absolute

**The cannon does not teleport to the touch point.** It moves by the *delta* of the
pointer since the previous frame, so the player's thumb never has to cover the cannon:

```
on press:   dragging = true;  lastX = pointerScreenX;  firing = true;
on move:    if (dragging) { target += (pointerScreenX - lastX) * PX_TO_WORLD * 1.25;
                            lastX = pointerScreenX; }
on release: dragging = false; firing = false;
```

`PX_TO_WORLD = 2 × orthographicSize / Screen.height`. The `1.25` sensitivity
multiplier is deliberate — 1:1 tracking feels sluggish for dodging.

### 10.2 Keyboard

`Move` shifts `target` at **6.20 u/s**. `Fire` held sets `firing`. These compose with
touch rather than replacing it.

### 10.3 Focus and interruption

On application pause/focus loss, force `firing = false` and clear held movement, or
the cannon fires forever after an alt-tab. Unity: `OnApplicationFocus(false)` and
`OnApplicationPause(true)`.

### 10.4 Blocking UI

Pointer input over the upgrade console or tuner must **not** roll the cannon or fire.
The console sits outside the playfield in the layout (§18), and gameplay press
handling must additionally check `EventSystem.current.IsPointerOverGameObject()` (with
the correct `pointerId` on touch: `Input.GetTouch(i).fingerId`).

---

## 11. Bullets and collision

### 11.1 Bullet state

```csharp
public struct BulletState {
    public Vector2 Position;
    public Vector2 PrevPosition;   // required for the swept test
    public Vector2 Velocity;
    public double  Damage;
}
```

### 11.2 Integration and despawn

```
prevPosition = position;
position += velocity * dt;
despawn if position.y > FIELD_TOP + 0.40 or |position.x| > halfWidth + 0.40
```

### 11.3 Swept collision — mandatory

At 15.5 u/s and a 0.034 s step a bullet advances 0.53 units per step. A tier-0 orb is
0.26 units across. **A point-in-circle test misses it entirely.** Test the *segment*
from `PrevPosition` to `Position` against the orb circle:

```csharp
static bool SegmentHitsCircle(Vector2 a, Vector2 b, Vector2 c, float r) {
    Vector2 ab = b - a;
    float len2 = ab.sqrMagnitude;
    float t = len2 > 0f ? Vector2.Dot(c - a, ab) / len2 : 0f;
    t = Mathf.Clamp01(t);
    return (a + ab * t - c).sqrMagnitude <= r * r;
}
```

Called with `r = orb.Radius + BULLET_RADIUS`.

### 11.4 Resolution

Iterate bullets outermost, orbs inner, and break on the first hit — **one bullet
damages exactly one orb**, it does not pierce.

```
orb.Hp -= bullet.Damage;
orb.Flash = 1;
if (floaters.Count < 10 && rng.NextDouble() < 0.3)
    SpawnDamageFloater(bullet.Position, orb.Position.y + orb.Radius * 0.6, bullet.Damage);
Vfx.Burst(bullet.Position, orb.Hue, 3, 1.20f);
Despawn(bullet);
if (orb.Hp <= 0) Kill(orb);
break;
```

The floater throttle is not optional: at 22 shots/s across 5 barrels, 110 floaters a
second bury the playfield.

### 11.5 Cost

Worst case 120 bullets × 80 orbs = 9,600 segment tests per step. That is fine as a
flat double loop over contiguous arrays. Only if profiling says otherwise, bucket orbs
into a uniform grid of cell size `2 × maxOrbRadius`; do not start there.

---

## 12. Destruction and splitting

```csharp
void Kill(Orb orb) {
    score      += orb.MaxHp;
    orbsKilled += 1;
    waveOrbsKilled += 1;

    double scrap = Math.Max(1, RoundHalfUp(orb.MaxHp * REWARD_RATE));
    wallet.Add(scrap);
    waveScrapEarned += scrap;
    SpawnScrapStreak(orb.Position, scrap);

    Vfx.Burst(orb.Position, orb.Hue, 8 + orb.Tier * 6, 2.40f + orb.Tier * 0.90f);
    Shake.Add(0.16f + orb.Tier * 0.10f);

    if (orb.Tier > 0 && liveOrbs.Count < MAX_ORBS) {
        int    childTier = orb.Tier - 1;
        double childHp   = Math.Max(1, Math.Ceiling(orb.MaxHp / 2.0));
        float  lift      = BounceSpeed(childTier) * 0.5f;

        foreach (int dir in new[] { -1, +1 }) {
            var child = pool.Get();
            child.Init(childTier, childHp,
                position: orb.Position + new Vector2(dir * orb.Radius * 0.45f, 0f),
                velocity: new Vector2(dir * TIER_DRIFT[childTier] * tune.drift * 1.15f, lift),
                entered:  true);
            child.Flash = 1f;
        }
    }
    Despawn(orb);
}
```

Points that matter:

- **Split HP derives from `MaxHp`, not remaining HP.** Overkill damage is discarded.
- **Children spawn with `Entered = true`** — they are already inside the field and
  must collide with walls immediately.
- **Children get 1.15× the tier's normal drift**, so a split visibly bursts apart.
- **Children launch upward at half a full bounce**, not a full one.
- **Above `MAX_ORBS` the orb dies without splitting.** A pathological chain would
  otherwise reach 31 orbs from one tier-4. This is a safety valve, not balance.
- Score uses `MaxHp`, so a tier-4 orb cleared entirely scores `maxHp × 5` across all
  layers, matching the damage it cost.

---

## 13. Economy and upgrades

### 13.1 Player upgrade state

```csharp
public sealed class UpgradeState {
    public int DamageLevel = 1;   // → DMG[DamageLevel]
    public int RateLevel   = 1;   // → RateOf(RateLevel)
    public int Barrels     = 1;   // 1..5
    public int Shields     = 1;   // 0..3, consumable, starts at 1
}
```

### 13.2 The pricing rule — tracks are independent

**Each track is priced off its own level and nothing else. Buying one upgrade never
changes the price of another.** This is a hard requirement, and the reason the obvious
alternative is wrong is worth stating, because it is easy to "simplify" back into the
bug:

> Pricing off total DPS (`price = K × DPS × relativeGain`) looks elegant and makes
> wave clear time self-correcting. But DPS is `damage × rate × barrels`, a **product**
> — so buying a barrel doubles DPS and therefore doubles the displayed price of damage
> and fire rate at the same time. The player is punished for progressing along one
> track by having every other track get more expensive. Do not do this.

```csharp
double PriceDamage()  => Math.Max(MIN_PRICE, RoundHalfUp(PRICE_DAMAGE * DMG[DamageLevel]));
double PriceRate()    => Math.Max(MIN_PRICE, RoundHalfUp(PRICE_RATE   * RateOf(RateLevel)));
double PriceBarrels() => RoundHalfUp(PRICE_BARREL * Math.Pow(PRICE_BARREL_STEP, Barrels - 1));
double PriceShield()  => RoundHalfUp(PRICE_SHIELD * Math.Pow(HP_GROWTH, Math.Max(0, Wave - 1)));
```

| Upgrade | Price | Reads | Maxed when |
|---|---|---|---|
| Damage | `560 × DMG[L]` | damage level | never |
| Fire rate | `5 × RateOf(L)` | rate level | `RateOf(L) >= 22` (level 24) |
| Barrels | `120 × 3^(barrels-1)` | barrel count | `Barrels >= 5` |
| Shield | `70 × 1.26^(wave-1)` | **wave number** | `Shields >= 3` |

Within damage and rate, price is proportional to that track's *current value*, which
holds price-per-unit-of-relative-gain flat as the track climbs — a damage level always
costs the same multiple of the damage it adds.

**Shield is the one exception**, and deliberately so: it buys survival, not damage, so
there is no track value to price against. It scales with the wave's threat level
instead. A wave advancing is not a purchase, so this still satisfies the rule — no
player action ever raises another upgrade's price. Note this also means shields do not
get more expensive as you stack them; buying all three at once is a legitimate early
defensive play that trades damage tempo for safety.

A maxed upgrade shows `MAX` and its button is disabled.

### 13.2.1 What this costs, and why it is still balanced

Independent pricing gives up the old model's self-correction, so the curve has to hold
up on its own. Two structural facts constrain it, both confirmed by simulation:

1. **The damage ladder's shape is forced.** Rate and barrels cap (at 22/s and 5), so
   past roughly wave 15 they contribute a constant ×110 and damage is the only live
   track. There, cumulative income scales as `1.26^n` and so must DPS, which means
   cumulative damage spend must be **proportional to damage value** — i.e. price ∝
   `DMG[L]`, exactly as above. Making it steeper (∝ `DMG[L]^γ`, γ > 1) plateaus the
   player's damage and clear time diverges; making it shallower collapses clear time
   to seconds. There is no freedom here, only in the constant.
2. **The constant is set by the tail.** `PRICE_DAMAGE = 560` places the settled clear
   time at 22–27 s. It scales linearly: doubling it roughly doubles late-game clear
   time.

The consequence is an intended shift in how a run reads:

| Waves | What the player is buying | Why |
|---|---|---|
| 1–10 | Fire rate, then barrels | Cheap (rate starts at 17 scrap) and immediately felt |
| 11–14 | Last barrels, damage begins | Rate has capped |
| 15+ | Damage only | Everything else is maxed; damage carries the rest of the run |

Damage sitting at 1 for the first several waves is expected, not a bug — the first
damage level costs 560 against a wave-1 income of ~44, so it is a saving goal while
rate upgrades supply the early progression.

### 13.3 Fire rate

```csharp
double RateOf(int level) => Math.Min(RATE_CAP, RATE_BASE * Math.Pow(RATE_GROWTH, level - 1));
//                                    22          3.4                  1.085
```

### 13.4 Purchase flow

Purchases are permitted in `Playing` **and** in `WaveCleared` (the panel is the
natural spending moment — §15). Reject silently if the price is `null` (maxed) or the
wallet is short; the button should already be visually disabled in both cases.

### 13.5 Income

| Source | Amount |
|---|---|
| Orb destroyed | `max(1, round(orb.MaxHp × 0.40))` |
| Wave cleared | `30 + 8 × waveNumber` |

---

## 14. Shield and loss condition

Checked per orb per step, skipped entirely while `invuln > 0`:

```csharp
float nx = Mathf.Clamp(orb.Position.x, cannonX - 0.28f, cannonX + 0.28f);
float ny = Mathf.Clamp(orb.Position.y, 0f, 0.2825f);
if ((orb.Position - new Vector2(nx, ny)).sqrMagnitude < orb.Radius * orb.Radius) {
    if (upgrades.Shields > 0) {
        upgrades.Shields--;
        cannon.Invuln = 1.5f;
        orb.Velocity = new Vector2(
            orb.Velocity.x + Mathf.Sign(orb.Position.x - cannonX == 0 ? 1 : orb.Position.x - cannonX) * 0.90f,
            BounceSpeed(orb.Tier));
        Vfx.Burst(new Vector2(cannonX, 0.2825f), hue: 272, count: 34, power: 4.60f);
        Shake.Set(1.2f);
    } else {
        GameOver();
        return;    // stop iterating orbs this step
    }
}
```

The shield **launches the orb at a full bounce** and pushes it sideways, so the player
gets breathing room rather than an instant second hit. The `|| 1` guard on the sign
handles an orb dead-centre on the cannon.

**Game over** clears `firing`, fires two bursts at the cannon (`hue 325` ×60 power
6.20, `hue 190` ×40 power 4.20), sets shake to 1.2, writes the best wave to disk if
beaten, and shows the panel after **0.7 s** so the explosion reads before the UI
covers it.

---

## 15. Level Cleared panel (NEW)

**This is the one addition to the HTML design.** The HTML shows a 1.5 s "Clear" banner
and auto-advances. The Unity build replaces that with a panel the player dismisses.

### 15.1 Flow

```
last orb destroyed
   → WavePhase.Fighting sees zero live orbs and an empty queue
   → award WAVE_BONUS(n) = 30 + 8n
   → GameState.WaveCleared
   → hold 0.35 s (let the final explosion and scrap streaks land)
   → panel animates in (0.25 s, scale 0.94 → 1, alpha 0 → 1)
   → player may buy upgrades here
   → "Next Wave" pressed
   → GameState.WaveIntro for wave n+1 → banner → Playing
```

### 15.2 Simulation while the panel is up

| System | State |
|---|---|
| Orb / bullet / cannon integrator | **Stopped** |
| Live bullets | Despawned on entry (they have nothing to hit) |
| Particles, scrap streaks, camera shake | Continue, on unscaled time |
| Backdrop grid drift, ground dash scroll | Continue |
| Upgrade console | **Interactive** |
| Tuner | Interactive |

### 15.3 Panel contents

| Row | Content | Source |
|---|---|---|
| Title | `WAVE {n} CLEARED` | Monoton, cyan, HDR |
| Stat | Orbs destroyed | `waveOrbsKilled` |
| Stat | Scrap earned | `waveScrapEarned` (includes the bonus) |
| Stat | Clear bonus | `30 + 8n`, called out separately |
| Stat | Time | `Time.time - waveStartTime`, `m:ss` |
| Stat | Accuracy | `waveHits / waveShots` as a percentage |
| Block | The four upgrade buttons | Same component as the console (§18.3) |
| Button | `NEXT WAVE` | Advances |

Show "Next wave: **{largest orb HP}** incoming" as a one-line preview under the
button, computed by building wave *n+1* early and reading its largest orb. Build it
once and cache it, so the wave the player then fights is the wave they were shown.

### 15.4 Per-wave counters

Reset these in `WaveIntro`, not in `Playing`, so the intro banner does not pollute
them:

```csharp
waveOrbsKilled  = 0;
waveScrapEarned = 0;
waveShots       = 0;
waveHits        = 0;
waveStartTime   = Time.time;
```

`waveShots` increments per bullet emitted (so a 5-barrel volley counts 5);
`waveHits` increments per bullet that connects. Accuracy above 100% is impossible by
construction.

### 15.5 Optional auto-advance

Ship a serialized `autoAdvanceSeconds` (default **0 = off**). When greater than zero,
a thin progress bar drains across the Next button and advances on expiry. Any pointer
interaction cancels it. Off by default because the panel exists to give the player an
unhurried spending moment.

---

## 16. Physics tuner

A live-tuning drawer, opened by the **TUNE** button in the top bar or the `T` key.

| Dial | Field | Range | Step | Default | Effect |
|---|---|---|---|---|---|
| Fall speed | `fall` | 0.35 – 1.50 | 0.05 | **0.65** | Multiplies gravity → bounce tempo |
| Bounce | `bounce` | 0.50 – 1.40 | 0.05 | 1.00 | Multiplies apex → bounce height |
| Drift | `drift` | 0.30 – 1.80 | 0.05 | 1.00 | Multiplies horizontal speed |

Rules:

1. **Applied live.** Changes take effect on the next step; no restart.
2. **`fall` and `bounce` need no retroactive work** — gravity is read each step and
   bounce speed is recomputed at each ground contact.
3. **`drift` must be applied retroactively.** Horizontal speed is baked into each
   orb's velocity at spawn, so on change, rescale every live orb:
   `orb.Velocity.x *= newDrift / oldDrift`. Without this the slider looks dead until
   the next spawn.
4. **Persisted** to `PlayerPrefs` on change, clamped to `[0.2, 2.0]` on load so a
   corrupted save cannot produce a broken run.
5. **Reset** restores all three defaults, including the retroactive drift rescale.
6. Opening the drawer in the HTML shrinks the playfield. In Unity the field is fixed
   (§3.2), so the drawer overlays instead — **no resize, no entity rescaling.** This
   removes an entire class of bug the HTML needed special handling for.

---

## 17. Presentation

Everything in the HTML is drawn procedurally. §17 describes intent; the companion
document `UNITY_ART_ASSETS.md` says which parts need imported assets.

### 17.1 Orb

Layered, back to front:

1. **Ground pool** — an additive radial gradient on the ground directly below the orb,
   width `radius × (0.7 + h × 0.9)` where `h = clamp(1 - orbY / (0.7 × H), 0, 1)`,
   alpha `0.06 + h × 0.30`. It reads as a shadow and works as a landing warning.
2. **Body** — radial gradient, orb hue, alpha `0.20 + flash × 0.35` at centre falling
   to 0.02 at the rim.
3. **Tube ring** — stroked circle, width `(2 + tier × 0.35)` ref px, lightness
   `64 + flash × 30`%, HDR so bloom halates it.
4. **Health arc** — drawn only when `hp < maxHp`. Starts at 12 o'clock, sweeps
   clockwise by `hp / maxHp` of a full turn, radius `orbRadius - 0.04`, lightness 82%.
5. **Number** — `Fmt(hp)` centred, bold, size `radius × 0.8`, shrunk to fit a
   `radius × 1.5` box. Colour `ink`, or pure white while `flash > 0.5`.

A cosmetic scale pulse of `1 + sin(wobble) × 0.02` is applied to the whole orb.

### 17.2 Cannon

Neon wireframe: magenta wheels (circle plus three chords, rotating with `spin`), cyan
chassis trapezoid with 16% fill, cyan barrel with 12% fill riding the recoil. Muzzle
glow is a radial gradient of radius `0.26 × recoil`, white core → cyan → transparent.
When shields are held, an arc of radius `0.42` spans 194°–345° above the chassis in
violet at alpha `0.32 + sin(t × 3) × 0.08`.

### 17.3 Backdrop

- Vertical gradient `#0a0518` → `deep` → `#1a0d38`.
- 16 horizontal grid rules at `y = groundY - (1 - f)² · groundY` for
  `f = (i + drift) / 16`, `drift = (time × 0.05) mod 1`, alpha `0.055 + f × 0.11`.
  The squared term bunches them toward the horizon.
- 10 radial verticals from `(0, 0.42 × groundY)` fanning to the ground line, alpha
  0.07.
- Scanlines and vignette as a full-screen overlay (§17.7).

### 17.4 Ground

A 2 ref-px cyan line with HDR bloom, a downward gradient fading `rgba(0,234,255,.30)`
→ transparent over the 0.30-unit strip, and a dashed line 0.07 below it scrolling at
0.34 u/s (dash 0.06, gap 0.10).

### 17.5 Particles

One additive system, max 420. A burst of *n* at power *p* emits particles with random
angle, speed `[0.25, 1.0] × p`, life `[0.3, 0.7] s`, width `[1.4, 3.0]` ref px, drawn
as short streaks along their velocity. Particle gravity is **6.20 u/s²** and drag is
`velocity.x × 0.98` per 1/60 s step.

> **Divergence D2.** `vx *= 0.98` per frame is frame-rate dependent. Under the fixed
> step of §24 it is stable. If ever run on variable dt, use
> `vx *= Mathf.Pow(0.98f, dt * 60f)`.

| Event | Count | Power | Hue |
|---|---|---|---|
| Muzzle | 4 | — (explicit velocity) | 190 |
| Bullet hit | 3 | 1.20 | orb hue |
| Orb ground bounce | 3 | 1.30 | orb hue |
| Orb destroyed | `8 + tier × 6` | `2.40 + tier × 0.90` | orb hue |
| Shield absorb | 34 | 4.60 | 272 |
| Game over | 60 + 40 | 6.20 / 4.20 | 325 / 190 |

### 17.6 Camera shake and danger

Shake accumulates per §12/§14, caps at **1.2**, decays at `2.6 / s`, and offsets the
camera by a random vector of magnitude up to `shake × 0.07` world units. Disable when
`reduceMotion` is set.

Danger vignette: magenta gradient rising from the bottom edge to 45% height, alpha
`0.3 × (danger - 0.35) / 0.65`, drawn only above the 0.35 threshold.

### 17.7 CRT overlay

A full-screen quad above gameplay, below UI: horizontal scanlines (1 px dark, 2 px
clear, ~20% opacity) multiplied over, plus a radial vignette darkening to
`rgba(4,1,10,.82)` at the corners.

### 17.8 Reduced motion

Honour `reduceMotion` (a settings toggle, since Unity has no OS query on all
platforms): disable camera shake, the logo flicker and the CTA pulse. Gameplay is
unaffected.

---

## 18. UI layout

### 18.1 Canvas setup

uGUI rather than UI Toolkit, because: TextMeshPro gives per-character HDR emission for
the neon type, the console buttons need bloom-participating borders that are trivial
as Image + material and awkward in UI Toolkit, and the runtime is portrait-fixed so
UI Toolkit's layout advantages do not pay for themselves.

- Canvas: `Screen Space - Camera`, on the main camera, plane distance 1.
- `CanvasScaler`: **Scale With Screen Size**, reference **1080 × 1920**, match **0.5**.
- Root layout: vertical, `Top bar / Playfield spacer / Tuner drawer / Upgrade console`.
- Safe area: an anchor-driven `SafeAreaFitter` on the root, reading
  `Screen.safeArea`, so the top bar clears a notch and the console clears a home
  indicator.

### 18.2 Top bar

`WAVE {n}` (cyan) on the left, three shield pips centred, `SCRAP {value}` (lime) on
the right, `TUNE` button at the far right. Shield pips are 9 px rings, filled and
glowing when held, 22% alpha when not. The scrap value pulses (scale 1 → 1.22 → 1)
each time a scrap streak lands.

### 18.3 Upgrade console

Four buttons in a row below the playfield, each showing name, current value, and
price. Accent colours: Damage cyan, Rate amber, Barrels magenta, Shield violet. Each
has a 2 px top rule in its accent that glows.

| Button state | Condition | Appearance |
|---|---|---|
| `rich` | affordable | full accent border, glow, press-scale 0.95 |
| `poor` | too expensive | 42% opacity, price in muted grey |
| `maxed` | at cap | price reads `MAX` in violet, non-interactive |

The console must sit **outside** the playfield's input area so buying never conflicts
with drag-to-move.

### 18.4 Screens

- **Start** — logo (Monoton, cyan with magenta "CANNON"), tagline, three how-to lines,
  Start button, best-run line if a best exists.
- **Level Cleared** — §15.3.
- **Game Over** — `CRUSHED` in Monoton magenta, a three-cell tally (Wave / Score /
  Best HP), best-run line, `REBUILD` button. Appears 0.7 s after death.

---

## 19. Persistence

`PlayerPrefs`, wrapped so a failure never throws into gameplay.

| Key | Type | Meaning |
|---|---|---|
| `neon-cannon-best` | int | Highest wave reached |
| `neon-cannon-tune-fall` | float | Clamped `[0.2, 2.0]` on load |
| `neon-cannon-tune-bounce` | float | Clamped `[0.2, 2.0]` on load |
| `neon-cannon-tune-drift` | float | Clamped `[0.2, 2.0]` on load |

Call `PlayerPrefs.Save()` on tuner change, on new best, and in
`OnApplicationPause(true)`. **No run state is persisted** — a closed app loses the
run, exactly as the HTML does.

---

## 20. Number formatting

Orb HP passes 180,000 by wave 34 and score runs into the millions, so every displayed
number goes through one formatter.

```csharp
static readonly string[] Units = { "K", "M", "B", "T", "Qa", "Qi" };

public static string Fmt(double n) {
    n = Math.Floor(n + 0.5);
    if (n < 1000) return ((long)n).ToString(CultureInfo.InvariantCulture);
    int i = -1;
    while (n >= 1000 && i < Units.Length - 1) { n /= 1000; i++; }
    return (n < 10 ? n.ToString("0.0", CultureInfo.InvariantCulture)
                   : Math.Floor(n + 0.5).ToString(CultureInfo.InvariantCulture)) + Units[i];
}
```

`999 → "999"`, `1000 → "1.0K"`, `11535 → "12K"`, `184702 → "185K"`, `4151691 → "4.2M"`.

Always pass `CultureInfo.InvariantCulture` — a device set to a comma-decimal locale
otherwise renders `1,0K`.

---

## 21. Numeric types and rounding traps

### 21.1 Use `double`, not `int`

Orb HP is `TIER_HP[t] × 1.26^(n-1)`. At wave 100 that is ≈ 7.9 × 10¹¹, well past
`int.MaxValue` (2.1 × 10⁹). Use `double` for HP, damage, scrap and score throughout.
`float` is not enough either — 24 bits of mantissa loses integer precision above
16.7 million, which arrives around wave 45.

### 21.2 JavaScript `Math.round` ≠ C# `Math.Round`

This is the single likeliest source of silent divergence.

| Input | JS `Math.round` | C# `Math.Round` (default) |
|---|---|---|
| 2.5 | **3** | **2** — banker's rounding |
| 3.5 | 4 | 4 |
| 0.5 | **1** | **0** |

C# defaults to `MidpointRounding.ToEven`. Every `Math.round` in the HTML must become:

```csharp
public static double RoundHalfUp(double v) => Math.Floor(v + 0.5);
```

All rounded quantities here are positive, so `Math.Floor(v + 0.5)` is an exact match
for JS. (`MidpointRounding.AwayFromZero` also matches for positives but differs for
negatives — prefer the explicit floor.)

Sites that must use it: the damage ladder, every upgrade price, scrap reward,
`HpOf(t)` in the wave builder, and the number formatter.

### 21.3 `Math.Ceiling` for split HP

Split HP uses `ceil(maxHp / 2)`, which is the same in both languages. Do not
substitute rounding — `ceil` guarantees a child never drops to 0 HP.

### 21.4 RNG

Use a seedable `System.Random` (or an injected `IRandom`) held by the wave director,
**not** `UnityEngine.Random`. Tests need to reproduce a wave exactly, and
`UnityEngine.Random` is global mutable state that anything can perturb.

---

## 22. Code hierarchy

```
Assets/
└── NeonCannon/
    ├── Scenes/
    │   ├── Boot.unity                  bootstrap, loads Game
    │   └── Game.unity                  everything else
    │
    ├── Settings/
    │   ├── URP-Renderer2D.asset
    │   ├── URP-Pipeline.asset
    │   └── PostProcessVolume.asset     bloom profile
    │
    ├── Art/                            see UNITY_ART_ASSETS.md
    ├── Fonts/
    ├── Prefabs/
    │   ├── Orb.prefab
    │   ├── Bullet.prefab
    │   ├── DamageFloater.prefab
    │   ├── ScrapStreak.prefab
    │   ├── Cannon.prefab
    │   └── UI/  (HudBar, UpgradeButton, TunerDrawer, LevelClearedPanel, …)
    │
    ├── ScriptableObjects/
    │   ├── OrbTierTable.asset
    │   ├── WaveBandTable.asset
    │   ├── EconomyConfig.asset
    │   ├── PhysicsConfig.asset
    │   ├── TuningDefaults.asset
    │   └── Palette.asset
    │
    └── Scripts/
        ├── NeonCannon.asmdef
        │
        ├── Core/
        │   ├── GameDirector.cs         state machine, owns the frame
        │   ├── GameState.cs            enum
        │   ├── RunState.cs             score, wave, per-wave counters
        │   ├── FieldGeometry.cs        world bounds, aspect clamp, px↔world
        │   ├── SimulationClock.cs      fixed-step accumulator
        │   └── MathUtil.cs             RoundHalfUp, SegmentHitsCircle, Clamp
        │
        ├── Config/
        │   ├── OrbTierTable.cs         SO: radius/apex/drift/hp/hue per tier
        │   ├── WaveBandTable.cs        SO: band table + load curve
        │   ├── EconomyConfig.cs        SO: per-track price constants, reward, caps
        │   ├── PhysicsConfig.cs        SO: gravity, speeds, limits
        │   ├── TuningDefaults.cs       SO: fall/bounce/drift defaults + ranges
        │   └── Palette.cs              SO: HDR colours by role
        │
        ├── Simulation/
        │   ├── OrbSystem.cs            integrate, walls, ground, threat
        │   ├── Orb.cs                  per-orb data + view binding
        │   ├── BulletSystem.cs         integrate, swept collide, resolve
        │   ├── Bullet.cs
        │   ├── CannonController.cs     movement, recoil, firing cadence
        │   ├── CannonCollision.cs      box test, shield, loss
        │   ├── WaveDirector.cs         BuildWave, spawn cadence, clear detect
        │   ├── WavePlan.cs             plan struct + OrbSpawn
        │   └── SplitResolver.cs        Kill() and split rules
        │
        ├── Economy/
        │   ├── UpgradeLadders.cs       DMG[], RateOf() — static, pure
        │   ├── UpgradeService.cs       prices, affordability, purchase
        │   ├── UpgradeState.cs
        │   └── Wallet.cs               scrap balance + change event
        │
        ├── Presentation/
        │   ├── OrbView.cs              ring, fill, arc, number, ground pool
        │   ├── CannonView.cs           wheels, chassis, barrel, shield arc
        │   ├── BackdropView.cs         gradient + receding grid
        │   ├── GroundView.cs           line, glow, scrolling dashes
        │   ├── VfxService.cs           burst API over one particle system
        │   ├── ScrapStreakView.cs      flight to the HUD counter
        │   ├── DamageFloaterView.cs
        │   ├── CameraShake.cs
        │   ├── DangerVignette.cs
        │   └── NumberFormat.cs         Fmt()
        │
        ├── UI/
        │   ├── HudBar.cs               wave, shields, scrap, TUNE
        │   ├── UpgradeConsole.cs       four buttons, state colouring
        │   ├── UpgradeButton.cs
        │   ├── TunerDrawer.cs          three sliders, live apply, persist
        │   ├── WaveBanner.cs
        │   ├── StartPanel.cs
        │   ├── LevelClearedPanel.cs    ← NEW (§15)
        │   └── GameOverPanel.cs
        │
        ├── Services/
        │   ├── SaveService.cs          PlayerPrefs wrapper
        │   ├── TuningService.cs        live dials + change events
        │   ├── ObjectPool.cs           generic pool
        │   └── IRandom.cs              seedable RNG interface
        │
        └── Tests/
            ├── NeonCannon.Tests.asmdef
            ├── PhysicsParityTests.cs
            ├── EconomyParityTests.cs
            ├── WaveBuilderTests.cs
            └── FormatTests.cs
```

### 22.1 Dependency direction

```
Config  ──────────────► Simulation ──────► Presentation
   │                        │                  ▲
   │                        ▼                  │
   └──────────────────► Economy ───────────► UI
                            ▲                  │
                        Services ◄─────────────┘
```

**Simulation never references Presentation or UI.** It raises events; views subscribe.
This keeps the whole simulation testable in edit-mode tests with no scene loaded,
which is what makes the parity tests in §26 cheap to run.

---

## 23. Class reference

Signatures a developer can implement directly against. Bodies are elided except where
the algorithm is the point.

### 23.1 `GameDirector`

```csharp
public sealed class GameDirector : MonoBehaviour {
    [SerializeField] PhysicsConfig  physics;
    [SerializeField] EconomyConfig  economy;
    [SerializeField] OrbTierTable   tiers;
    [SerializeField] WaveBandTable  bands;

    public GameState State { get; private set; }
    public RunState  Run   { get; private set; }

    public event Action<GameState> StateChanged;
    public event Action<int>       WaveStarted;
    public event Action<int>       WaveCleared;   // wave number just cleared
    public event Action            RunEnded;

    public void StartRun();          // Menu/GameOver → WaveIntro(1)
    public void AdvanceWave();       // WaveCleared  → WaveIntro(n+1)
    public void EndRun();            // → GameOver, persists best

    void Update();                   // drives SimulationClock, ticks systems in Playing
    void SetState(GameState next);
}
```

### 23.2 `SimulationClock`

```csharp
public sealed class SimulationClock {
    public const float  Step     = 1f / 60f;
    public const int    MaxSteps = 3;         // ≥3 frames behind → drop time, never spiral

    float accumulator;

    /// Returns how many fixed steps to run this frame.
    public int Advance(float deltaTime) {
        accumulator += Mathf.Min(deltaTime, 0.034f);   // matches the HTML dt clamp
        int steps = 0;
        while (accumulator >= Step && steps < MaxSteps) { accumulator -= Step; steps++; }
        if (steps == MaxSteps) accumulator = 0f;
        return steps;
    }
    public float Alpha => accumulator / Step;          // for render interpolation
}
```

### 23.3 `OrbSystem`

```csharp
public sealed class OrbSystem {
    readonly List<Orb> live = new(96);
    public IReadOnlyList<Orb> Live => live;
    public float Danger { get; private set; }

    public event Action<Orb> OrbSpawned;
    public event Action<Orb, double> OrbDamaged;   // orb, damage applied
    public event Action<Orb> OrbKilled;
    public event Action<Orb> OrbBounced;

    public Orb Spawn(int tier, double hp, Vector2 pos, Vector2 vel, bool entered);
    public void Step(float dt, float cannonX);     // §6.3–6.6
    public float BounceSpeed(int tier);            // §6.5
    public void ApplyDriftChange(float ratio);     // §16 rule 3
    public void Clear();
}
```

### 23.4 `FieldGeometry`

```csharp
public static class FieldGeometry {
    public const float FieldHeight  = 7.80f;
    public const float FieldTop     = 7.50f;
    public const float GroundStrip  = 0.30f;
    public const float MaxPlayWidth = 6.00f;

    public static float HalfWidth   { get; private set; }   // playWidth / 2
    public static float PixelsToWorld { get; private set; } // for drag deltas

    public static void Recalculate(Camera cam);             // call on resolution change
}
```

### 23.5 `WaveDirector`

```csharp
public sealed class WaveDirector {
    readonly IRandom rng;
    readonly Queue<OrbSpawn> queue = new();
    public WavePhase Phase { get; private set; }
    public int Wave { get; private set; }

    public event Action<int, string> WaveAnnounced;  // wave, subtitle
    public event Action WaveComplete;

    public List<OrbSpawn> BuildWave(int n);          // §7.3 — pure, testable
    public void BeginWave(int n);
    public void Step(float dt, OrbSystem orbs);      // spawn cadence + clear detection
    public double PreviewLargestOrb(int n);          // §15.3 preview, caches the plan
}

public struct OrbSpawn { public int Tier; public double Hp; public int Side; }
```

### 23.6 `UpgradeService`

```csharp
public sealed class UpgradeService {
    public UpgradeState State { get; }
    public double Dps();                       // readout only — MUST NOT feed any price

    // Each reads one track's level (PriceShield reads the wave). See §13.2.
    public double? PriceDamage();              // null == maxed
    public double? PriceRate();
    public double? PriceBarrels();
    public double? PriceShield(int wave);

    public bool TryBuy(UpgradeKind kind);      // checks price + wallet, raises Purchased
    public event Action<UpgradeKind> Purchased;
}

public enum UpgradeKind { Damage, Rate, Barrels, Shield }
```

### 23.7 `UpgradeLadders`

```csharp
public static class UpgradeLadders {
    public static readonly double[] Damage = BuildDamageLadder(400);   // §5.4
    public static double RateOf(int level);                            // §13.3

    static double[] BuildDamageLadder(int max) {
        var d = new double[max + 2];
        d[1] = 1;
        for (int L = 2; L <= max + 1; L++)
            d[L] = Math.Max(d[L - 1] + 1, MathUtil.RoundHalfUp(d[L - 1] * 1.16));
        return d;
    }
}
```

Note the array is sized `max + 2` because `PriceDamage()` reads `Damage[L + 1]`.

### 23.8 `TuningService`

```csharp
public sealed class TuningService {
    public float Fall   { get; private set; } = 0.65f;
    public float Bounce { get; private set; } = 1.00f;
    public float Drift  { get; private set; } = 1.00f;

    public event Action<float> DriftChanged;   // carries newDrift / oldDrift

    public void SetFall(float v);
    public void SetBounce(float v);
    public void SetDrift(float v);             // raises DriftChanged with the ratio
    public void ResetAll();
    public void Load();                        // clamps to [0.2, 2.0]
    public void Save();
}
```

### 23.9 `LevelClearedPanel`

```csharp
public sealed class LevelClearedPanel : MonoBehaviour {
    [SerializeField] TMP_Text title, orbs, scrap, bonus, time, accuracy, preview;
    [SerializeField] UpgradeConsole console;
    [SerializeField] Button nextButton;
    [SerializeField] CanvasGroup group;
    [SerializeField] float revealDelay = 0.35f, revealDuration = 0.25f;
    [SerializeField] float autoAdvanceSeconds = 0f;   // 0 = off

    public event Action NextRequested;

    public void Show(WaveSummary summary);
    public void Hide();
}

public readonly struct WaveSummary {
    public readonly int    Wave;
    public readonly int    OrbsKilled;
    public readonly double ScrapEarned;
    public readonly double ClearBonus;
    public readonly float  Duration;
    public readonly float  Accuracy;      // 0..1
    public readonly double NextLargestOrb;
}
```

### 23.10 `ObjectPool<T>`

```csharp
public sealed class ObjectPool<T> where T : Component {
    public ObjectPool(T prefab, Transform parent, int prewarm);
    public T Get();
    public void Release(T item);
    public void ReleaseAll();
}
```

---

## 24. Execution order and the frame

`GameDirector.Update` owns the frame explicitly rather than relying on Unity's
script execution order, which is invisible in code review and easy to break.

```
Update(deltaTime):
    steps = clock.Advance(deltaTime)

    if State == Playing:
        for i in 0..steps:
            input.Sample()                    // drag delta, fire held
            cannon.Step(Step)                 // move, recoil, cooldown, fire
            waveDirector.Step(Step, orbs)     // spawn cadence, clear detection
            bullets.Step(Step, orbs)          // integrate, swept collide, resolve
            orbs.Step(Step, cannon.X)         // integrate, walls, ground, threat
            cannonCollision.Step(orbs)        // shield / loss
            if State != Playing: break        // loss ends the step loop immediately

    effects.Step(deltaTime)                   // particles, floaters, streaks, shake
    views.Sync(clock.Alpha)                   // positions, numbers, colours
    ui.Sync()                                 // only on dirty flags
```

**Order rationale.** Bullets step before orbs so a bullet fired this frame can hit an
orb at the orb's *previous* position — matching the HTML, where the bullet loop runs
first. Cannon collision runs last so an orb that just bounced is tested at its
post-bounce position, which is what makes the ground-bounce-into-cannon case behave.

**UI sync is dirty-flagged.** The HTML rebuilds its HUD only when a composite key of
`(wave, scrap, damage, rate, barrels, shields)` changes. Do the same — updating four
TextMeshPro fields every frame is a measurable cost on mobile for no visible gain.

---

## 25. Object pooling

Mandatory. At 22 shots/s × 5 barrels the game creates 110 bullets a second; `Instantiate`/
`Destroy` at that rate produces GC pressure that shows up as hitching on mobile.

| Pool | Prewarm | Ceiling | Notes |
|---|---|---|---|
| Orb | 40 | 80 | Hard cap is `MAX_ORBS`; split is suppressed at the cap |
| Bullet | 150 | 250 | Ceiling covers 5 barrels × 22/s × ~0.5 s of flight |
| Particle | — | 420 | One `ParticleSystem` with `Emit()`, not pooled GameObjects |
| Damage floater | 12 | 16 | Spawn is throttled to 10 live (§11.4) |
| Scrap streak | 24 | 48 | |

Release rules: return on despawn, and `ReleaseAll()` on `StartRun`, on entering
`WaveCleared` (bullets only), and on `GameOver`.

---

## 26. Test plan

Edit-mode tests, no scene required, because Simulation has no Presentation dependency.

### 26.1 `PhysicsParityTests`

| Test | Assertion |
|---|---|
| `BouncePeriod` | Tier 4 at default tuning: 1.959 s ±0.02 |
| `ApexInvariance` | Apex at `fall = 0.35` and `fall = 1.50` differ by < 1% |
| `ApexMatchesFormula` | Measured apex == `apexFrac × bounce × 7.80` ±0.5% |
| `BouncePeriodScalesInverseSqrt` | `T(0.65) / T(1.0)` == 1.240 ±0.01 |
| `SweptCollision` | A bullet stepped at dt = 1/15 hits a tier-0 orb on its path |
| `EntryGate` | An orb spawned outside the wall does not bounce off it on step 1 |
| `NoGroundTunnelling` | At dt = 0.034 and 3× gravity, no orb ends below y = 0 |

### 26.2 `EconomyParityTests`

| Test | Assertion |
|---|---|
| `DamageLadder` | `DMG[1..30]` matches the §5.4 table exactly |
| `RateCapsAtLevel24` | `RateOf(24) == 22`, `RateOf(23) < 22` |
| `PricesAtStart` | Damage 560, rate 17, barrels 120, shield 70 |
| **`TrackPricesAreIndependent`** | **From any upgrade state, buying one track leaves all three other prices bit-identical. Assert over the cross product of damage 1..40 × rate 1..24 × barrels 1..5.** |
| `ShieldTracksWaveOnly` | Shield price changes with wave and is unchanged by any purchase |
| `DamagePriceProportional` | `PriceDamage(L) / DMG[L]` is constant (== 560) for L = 1..60 |
| `MaxedReturnsNull` | Rate at L24, barrels at 5, shields at 3 all return null |
| `RoundHalfUp` | `RoundHalfUp(2.5) == 3` — guards the §21.2 trap |

`TrackPricesAreIndependent` is the regression test for the bug this pricing model
exists to fix. It should fail loudly if anyone reintroduces a `Dps()` term into a
price.

### 26.3 `WaveBuilderTests`

| Test | Assertion |
|---|---|
| `TopTierAlwaysAffordable` | For n = 1..60, at least one orb is at the band's top tier |
| `NeverEmpty` | For n = 1..200, `plan.Count >= 1` |
| `CountCeiling` | For n = 1..200, `plan.Count <= 10` |
| `SplitCost` | Total damage to clear a tier-*t* orb of HP *h* == `h × (t + 1)` |
| `HpCrosses10k` | Largest orb HP first exceeds 10,000 at wave 22 |
| `Deterministic` | Same seed → identical plan |
| `NoDifficultyCliff` | Wave-over-wave total damage never more than 2.0× the previous |

### 26.4 Play-mode smoke tests

| Test | Assertion |
|---|---|
| `WaveClearShowsPanel` | Killing the last orb reaches `WaveCleared` and shows the panel |
| `PanelBlocksSimulation` | Orb positions are unchanged across 30 frames while the panel is up |
| `NextAdvances` | Pressing Next reaches `WaveIntro` for n+1 |
| `PurchaseFromPanel` | Buying from the panel debits the wallet and updates the button |
| `TunerPersists` | Set fall to 0.45, restart the run, value is 0.45 |

---

## 27. Divergence register

Everything the Unity build does differently from the HTML, and why. Nothing else
should differ.

| ID | Divergence | Reason |
|---|---|---|
| **N1** | **Level Cleared panel replaces the 1.5 s auto-advance banner** | Requested. Gates progression on the player and gives an unhurried spending moment. |
| N2 | Scale factor `S` removed; world units are fixed | The orthographic camera does the scaling. Removes a whole class of bug. |
| N3 | Fixed 1/60 s simulation step instead of clamped variable dt | Determinism, and makes the parity tests meaningful. The HTML's `min(dt, 0.034)` becomes the accumulator's input clamp. |
| N4 | Tuner drawer overlays instead of shrinking the playfield | Field size is fixed, so the HTML's entity-rescale-on-resize logic is unnecessary. |
| D1 | Cannon smoothing may use `1 - exp(-22 dt)` | Frame-rate independent form of the same curve; only needed if not on a fixed step. |
| D2 | Particle drag may use `pow(0.98, dt × 60)` | Same, for particle velocity damping. |
| N5 | Per-wave counters (orbs, scrap, shots, hits, duration) added | Required to populate the new panel. |
| N6 | `double` everywhere for HP/damage/scrap/score | JS numbers are doubles; C# `int`/`float` would overflow or lose precision (§21.1). |
| N7 | Seedable `IRandom` instead of ambient RNG | Test reproducibility (§21.4). |
| N8 | Audio | The HTML has **no audio at all**. Nothing to port. Any sound design is new work and out of scope for a 1:1 replica. |

---

## Appendix A — Constant quick card

```
FIELD_HEIGHT 7.80   FIELD_TOP 7.50   GROUND_STRIP 0.30   MAX_PLAY_WIDTH 6.00
GRAVITY 14.50       BULLET_SPEED 15.50   BULLET_R 0.05
MAX_ORBS 80         MAX_PARTICLES 420
SPAWN_GAP 1.15      FIRST_SPAWN_DELAY 1.00   DT_CLAMP 0.034

TIER_R      0.13  0.21  0.31  0.43  0.57
TIER_APEX   0.30  0.38  0.45  0.52  0.58     (× FIELD_HEIGHT)
TIER_DRIFT  1.30  1.18  1.06  0.95  0.85
TIER_HP        3     7    16    38    90
TIER_HUE     190   100    45   325   272

HP_GROWTH 1.26   REWARD 0.40   MIN_PRICE 15
START_SCRAP 70   START_SHIELDS 1   WAVE_BONUS 30 + 8n
RATE 3.4 × 1.085^(L-1) cap 22   DMG_GROWTH 1.16   MULTI_MAX 5   SHIELD_MAX 3

PRICES — each reads ONE track's own level; never total DPS
  damage  560 × DMG[L]            rate    5 × RateOf(L)
  barrels 120 × 3^(barrels-1)     shield  70 × 1.26^(wave-1)
  at start: 560 / 17 / 120 / 70

BANDS  (wave 1 → tier 1) (3 → 2) (6 → 3) (11 → 4)
LOAD   min(4.5, 1 + 0.45 × (n - bandFirstWave))
BUDGET fullCost(topTier) × LOAD          fullCost(t,h) = h × (t+1)

TUNE   fall 0.65 [0.35..1.50]   bounce 1.00 [0.50..1.40]   drift 1.00 [0.30..1.80]

CANNON halfW 0.28   bodyTop 0.2825   muzzle 0.6225   wheelR 0.11
       hitbox x ± 0.28, y 0 .. 0.2825   (barrel excluded)
       keyboard 6.20 u/s   drag sensitivity 1.25   smoothing min(1, dt × 22)
       spread 0.075 rad/barrel   barrel x-offset 0.05
```
