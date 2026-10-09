# Hexa Stack

An endless hex-stacking puzzle. Drag a stack of coloured hex tiles from the tray
onto an empty cell of the 19-cell board. Any neighbouring stack whose top colour
matches sends its top run across, tile by tile, and merges cascade. Ten tiles of
one colour clear. A new colour joins every seven clears, and the run ends when
the board is full.

Every seven clears is also a **stage**. Stages follow the Playbox rhythm: the
5th of every ten is a **hard wave** and the 10th a **super hard wave**, each
announced with a banner. How the tray stacks are dealt (how tall they are, how
many colours each holds, how often they match what's on the board) is set per
stage from a Bayesian estimate of the player's skill, the same model the other
Playbox games use, so a strong player gets tougher stacks and a struggling one
gets more help. Surviving a stage counts as a win (with more free cells at the
tightest moment counting as easier), the board filling up as a loss, and the
estimate is kept between runs.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. ← and → (or the buttons at the bottom) rotate the
board, so a stack hidden behind a tall one can be brought forward.

In [Playbox](../playbox/) this game appears as **Hex Tile Sort**. Playbox runs
this page unchanged and adds two things around it: a back button in the header,
and the `window.storage` the game uses to keep its best score and the skill
estimate (backed by `localStorage`, under keys starting `playbox.hexa-stack.`).
Opened on its own outside Claude, the page has no `window.storage`, so both
last only until the page is closed.

For a Unity build (in 3D, as part of Playbox), see
[`../playbox/PLAYBOX_UNITY_PLAN.md`](../playbox/PLAYBOX_UNITY_PLAN.md) (Part III)
and [`../playbox/PLAYBOX_ASSETS.md`](../playbox/PLAYBOX_ASSETS.md).

## Files

```
index.html   the whole game: one file, canvas + synthesised WebAudio
```

## Tuning knobs

Top of the script in `index.html`: `CLEAR_AT` (tiles per clear), `CLEAR_GRACE`
(how long a full stack waits to be fed before it clears), `CLEARS_PER_TIER`
(clears per new colour, and per stage), `START_COLOURS`, `SEED_STACKS`, and
`stackHeight()` / `pickColour()` / `genStack()` for how the tray stacks are
dealt at a stage's heat. `SKILL` and `HEAT_MAX` (next to the skill model) are
the model's prior and noise and the hottest a stage can get; `observeStage()`
holds what counts as winning a stage and how easy it was.

`window.__hx` exposes `G`, `skill()`, `heat()`, `stage()`, `setSkill(mu, sd)`
and `advance(k)` (count k clears) for testing.
