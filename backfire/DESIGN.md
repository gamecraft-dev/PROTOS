# Backfire — prototype rationale

A bouncing-ball breaker where everything hangs from the ceiling, and anything you
cut loose falls, flips, and slams back up into whatever was above it.

The prototype is `index.html`. This is the argument behind it and the measured
numbers it was tuned on.

---

## 1. The reference

Two proven mechanics, welded at the joint:

- **Ballz / Bricks n Balls / Swipe Brick Breaker** — aim once, a stream of balls
  flies out and ricochets, numbered blocks lose one per hit, a new row pushes
  down every turn. Nobody has to be taught this.
- **Bubble shooter connectivity** — anything that loses its link to the ceiling
  falls. Also nobody has to be taught this; it is twenty years old and physical.

Both halves are individually understood on sight, which is the bar the last
prototype failed. What is new is only what happens *after* the fall.

---

## 2. The tweak: what falls comes back up

In every bubble shooter, a disconnected cluster drops off the bottom of the
screen and pays out a small bonus. It is a tidy-up animation. It is the most
visually dramatic moment in the genre and it does nothing.

Here, a disconnected cluster drops, **flips, and rockets back up its own
columns**, each block dealing damage equal to the number printed on it, piercing
upward until that damage is spent.

That one change does four things:

1. **It makes the biggest blocks the best ammunition.** A 200-HP block is the
   thing you most want to *drop*, not the thing you most want to break. The
   scariest object on screen is re-read as the most valuable one, which inverts
   the whole board-reading habit the player brought in.
2. **It creates chains without adding a rule.** A backfire that destroys another
   support cuts another group loose, which falls, which backfires. Wave two is
   worth more than wave one. No combo meter, no special block, no explanation —
   it just happens and the player sees why.
3. **It converts aiming from "hit the most blocks" to "hit the right block".**
   Chipping faces is the losing strategy, deliberately. The winning shot is at
   one specific load-bearing block that may be worth almost nothing itself.
4. **It gives the genre an out from its own dead end.** Ballz-likes fail by
   arithmetic: your ball count grows, the wall's HP grows, and eventually one of
   the curves wins forever. Backfire damage comes from the wall's own HP, so it
   scales with the difficulty automatically. The bigger the blocks get, the
   harder they hit when they come loose.

### What I deliberately did not add
No rotation, no ball types, no special blocks, no power-ups, no energy, no
levels-with-objectives. The board is blocks, a number, and green ammo orbs. One
new idea is the entire budget.

---

## 3. The board reads itself

The load-bearing block is never labelled and there is no "support" indicator.
The connectivity is visible in the geometry — that is the whole skill, and
marking it would remove the game. The only concession is the tutorial, which
hands you one unmistakable pillar holding one unmistakable slab.

---

## 4. Numbers

| | |
| --- | --- |
| Grid | 8 columns, ~13 rows to the cannon line |
| Block HP | `0.8 × wave^1.35 × (0.6–1.45)`, 10% chance of a ×2.2 heavy |
| Row density | 42% → 74%, rising with the wave |
| Row shapes | scatter / bridge (one solid span) / pillars (two clumps, wide gap) |
| Ball damage | 1 to start, bought upward |
| Ball count | 5 to start, cap **45** |
| +1 Ball cost | `7 × 1.115^n` — geometric, so ball count cannot outrun the wall |
| +1 Damage cost | `30 × 1.72^n` |
| Coins per block | `1 + √HP` |
| Backfire damage | the block's **current** HP, pierces upward until spent |
| Chain bonus | `40 × chain × wave` on any collapse of two waves or more |

Three constants carry the whole difficulty curve and they are marked in the
source: `MAX_BALLS`, the HP exponent in `mkBlock`, and `COST_DMG`.

---

## 5. Measured balance

A headless bot plays with no strategy at all — it aims at the deepest occupied
column with ±13° of slop, buys every ball it can afford, and buys damage on a
crude threshold. It never *looks* for a load-bearing block. That makes it a
floor, not a benchmark.

| | |
| --- | --- |
| Waves survived (5 runs) | 22, 29, 47, 65, 80 |
| Scores | 682 · 2,255 · 22,659 · 43,115 · 73,949 |
| Hits per ball | ~1.8 mid-run |
| Board depth over a run | 3/13 → 13/13, oscillating on every big collapse |
| Firing straight up every turn | dead by wave 16 |

The spread is the interesting part: identical policy, identical tuning, and a
3× range in waves and a 100× range in score — because the runs that stumbled
into chains ran away with it. That gap is where the skill lives, and a player who
hunts supports on purpose should sit well above the bot.

The first tuning pass failed this test outright: the bot hit a 120-turn cap at
wave 124 with 122 balls and an empty board. Ball count was linear-cost and block
HP was linear-growth, so the player's curve simply won. Geometric ball cost, a
hard ball cap, and a `wave^1.35` HP curve are what fixed it.

---

## 6. Monetisation

Ad-led, matching the reference category, placed where it does not poison the loop:

| Placement | Why |
| --- | --- |
| Rescue at the loss moment (mocked here) — clears the bottom three rows | Highest-intent moment in the game. Once per run. |
| Interstitial between runs | Standard, frequency-capped. |
| Optional "double your cores" at run end | Untested; the natural second placement. |
| Cosmetic ball trails and block skins (not built) | Non-pay-to-win IAP; both are on screen constantly. |

No energy, no paywalled power, no forced ad after every shot.

---

## 7. Retention

- **Workshop** — cores (one per 1,500 points) buy permanent starting balls,
  starting damage, and a coin multiplier. Slow on purpose: the full board is
  about nine good runs.
- **Personal best** — one number, always on screen, always beatable.
- **Waves survived** — a second, coarser scoreboard for players who bounce off
  score chasing.

Not built, and the obvious next thing: a daily seeded wall with a fixed block
sequence and a shareable result. It worked in both previous prototypes and it is
nearly free here since the board is already deterministic given a seed.

---

## 8. Risks

1. **The player may never notice the mechanic.** Everything in the tutorial
   exists to prevent this, but in free play a player can chip faces for twenty
   waves and lose without once cutting a support deliberately. The one-time
   "more balls will not save you" card is the safety net. If playtests show
   people still miss it, the next lever is a subtle highlight on blocks whose
   removal would drop three or more others — at the cost of some of the skill.
2. **Two support columns instead of one.** Real boards frequently hold a slab up
   from both ends, so the player must break two specific blocks in the same turn
   to get the payoff. That is a genuinely harder read than the tutorial teaches,
   and it may be the single biggest gap between "understood it" and "can do it".
3. **The cap at 45 balls is a visible ceiling.** It keeps the turn under a second
   and the screen readable, but it also means late runs are entirely a damage
   economy. If the late game feels flat, the fix is a third purchasable axis
   rather than raising the cap.
4. **Ricochet is not universally legible.** ~1.8 hits per ball means most balls
   hit once; the fantasy of a ball pinballing twenty times is rarer than the
   genre's marketing suggests. Denser boards raise it, which is one more argument
   for the density curve.

---

## 9. What to look for while playing

- The first time a slab comes loose — is it obvious *why* it fell?
- When you deliberately hunt a support and get it: does that feel better than a
  lucky twenty-hit ricochet? It has to, or the tweak has not earned its place.
- The moment you notice a 200-block is worth more dropped than broken. Did it
  land, and how far in?
- Two-ended slabs: could you read them, or did you only ever get single pillars?
- Is the wall's arrival pressure exciting or just inevitable?
