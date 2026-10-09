# Roundabout Rush

A tap-timing traffic game. Your cars wait on a side road; every tap sends the
front one into a busy roundabout. Find the gap, merge clean, and get every car
onto the ring before the clock runs out. One bad tap and it's a pile-up.

Based on **Car Circle** (Shoom Games, on Poki), rebuilt as a publish-ready
mobile prototype: the same core loop plus a level clock, stars, four boosters,
a car garage with a coin economy, daily rewards, and every ad and store
placement mocked in place.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. On desktop: Space or ↑ to tap, ← → on two-road
levels, 1–4 for boosters, Esc to pause.

- **[DESIGN.md](DESIGN.md)**: the rules, the level generator, the measured
  balance, the economy and ad rules, the screen flow, and notes for the Unity build.
- **[ASSETS.md](ASSETS.md)**: every art, audio and store asset the Unity
  build needs that this prototype draws in code or fakes.

In [Playbox](../playbox/) this game appears as **Car Loop**. Playbox runs this
page unchanged (it embeds `index.html` when Playbox is built) and adds a back
button to the home screen's top row; progress stays in this game's own save
(`roundabout-rush-v1`), which the Car Loop board reads to show your level. After
changing the game, run `./build.sh` here and then `../playbox/build.sh`.

For a Unity build of Car Loop as part of Playbox, use
[`../playbox/PLAYBOX_UNITY_PLAN.md`](../playbox/PLAYBOX_UNITY_PLAN.md) (Part IV)
and [`../playbox/PLAYBOX_ASSETS.md`](../playbox/PLAYBOX_ASSETS.md).
They take their rules and numbers from this prototype and from DESIGN.md, and
bake the shipped levels from this page's own generator.

---

## How to play

- Tap anywhere: the front car pulls off the stop line and merges onto the ring.
- Every car on the ring moves at one shared speed, clockwise (some levels flow
  the other way). A tap that lands your car on top of another one is a crash.
- Get all your cars in before the clock runs out. The clock starts on your first tap.
- Stars come from time left: 40% or more is three stars, 15% or more is two.
- Squeezing into a tight gap earns a **CLOSE!** bonus (+3 coins).

## What's in the build

| Area | Contents |
| --- | --- |
| Core | 10 track shapes, clockwise and counter-clockwise flow, offset and twin entrances, rush-hour speed surges, hard levels, crash physics with wrecks |
| Levels | 10 hand-tuned levels, then an endless seeded generator whose speed, traffic and clock adapt to the player (a Bayesian skill estimate, keeping the hard spikes); every level is proven clearable by three bots before it ships |
| Boosters | Slow-Mo, Green Light, Tow Truck, Autopilot: unlock intros, inventory, buy with coins or a rewarded ad |
| Economy | Coins from clears, stars, hard levels, close calls and car bonuses; 12 cars in 4 rarities bought with coins, ads or level milestones; free-car progress bar |
| Panels | Splash, home, level select, garage, shop, pause, settings, level complete (with ×2–×5 multiplier needle), crash / time's up (with revive countdown), booster intro, booster purchase, not enough coins, new car, starter pack, rate us, daily reward, store confirm |
| Ads (mocked) | 320×50 banner, interstitials with frequency caps, rewarded video at 9 placements, close-early warning, no-fill simulation |
| Store (mocked) | 4 coin packs, Remove Ads, Starter Pack, restore purchases |
| Juice | Procedural cars, headlight beams, tire smoke, crash shockwave, sparks, fire, debris, confetti, screen shake, synthesised SFX and music, haptics |
| Tools | Developer section in Settings (coins, boosters, unlock levels, ad failure, short ads, reset) and headless hooks for bots |

## Files

```
index.html     the game — open this
src/app.html   source (no <html>/<head>/<body>; the artifact host supplies those)
build.sh       wraps src/app.html into the standalone index.html
DESIGN.md      rules, generator, balance data, economy, ads, flow, Unity notes
ASSETS.md      the asset list for the Unity build
```

Edit `src/app.html`, then run `./build.sh`.

## Tuning knobs

All in the config block at the top of the script in `src/app.html`:

- `GEOM`: car size, hitbox, road width, queue gap, close-call distance.
- `ECON`: level payouts, star and hard-level multipliers, revive prices, the
  multiplier needle, free-car progress, free-coin cooldown.
- `ADS`: when interstitials may first appear, how often, the minimum gap, the
  grace period after a rewarded video, mock video length.
- `BOOSTERS`, `CARS`, `DAILY`, `IAP`: the content tables.
- `HAND` and `rawDef()`: the hand-made levels and the generator curves.
  `levelDef()` holds the validation and the clock formula; see DESIGN.md §4.
- `SKILL`, `HARD_WORTH`, `heatRange()` and `levelTarget()`: the adaptive
  difficulty (the model's prior and noise, the range it may move a level, and
  each level's target win rate).

## Headless hooks

`window.__rr` exposes `startLevel(n)`, `tap(f)`, `step(dt)`, `turbo(k)`,
`plan(f, lead, margin)`, `light(f)`, `levelDef(n, e)`, `rawDef(n, e)`,
`heatFor(n)`, `skill()`, `setSkill(mu, sd)`, `state()`, every panel under
`open.*`, the ad mock under `ads`, and the analytics log under `log`. The balance
tables in DESIGN.md were measured through these with Playwright.
