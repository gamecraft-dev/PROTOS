# Playbox

One app, a shelf of small games. The shell handles the home screen, settings,
saving and sound. Each game is a separate file that plugs into it.

**Games on the shelf**

| Game | What it is |
| --- | --- |
| **Paint Sort** | Pour paint between glass vials until every vial holds one colour. Levels are generated on the device with a sawtooth difficulty curve: the 5th and 10th level of every ten are hard. |

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. `index.html#paint-sort` opens straight into the game.

Why Paint Sort is built the way it is, and the measured difficulty curve:
**[DESIGN.md](DESIGN.md)**.

---

## Paint Sort: how to play

Tap a vial to pick it up, then tap another to pour. The top colour pours
across, but only onto the same colour or into an empty vial, and only as much as
fits. Fill a vial with four units of one colour and it gets corked.

- Every level has a small painting above the vials, drawn in pencil. Each
  colour you finish brushes its part of the picture in.
- Grey layers with a **?** are hidden paint. They show their colour once
  the paint above them has been poured off (from level 13).
- **Boosters:** Undo (5 per try), Hint (points at a pour that still wins),
  Add vial (one extra empty vial, once per level). Coins buy more.
- **Levels 5 and 10 of every ten are hard and super hard.** The level after
  each one eases off. They pay 30 and 60 coins; a normal level pays 10, plus 5
  more if you used no boosters.
- If the board can no longer be finished, a bar says so and offers undo, an
  extra vial or a restart.

Progress (level, coins, boosters, and the board you're partway through) is
saved on the device after every pour.

## What's in the build

- Hub: home shelf, shared settings (sound, vibration, light/dark/auto theme,
  erase progress), one save file with a section per game, synthesised audio,
  haptics, sheets and toasts
- Level generator: deterministic per level number, solver-checked, picked by
  simulated players to hit the sawtooth (see DESIGN.md)
- A pour animation where the paint stays level as the vial tips: the pour rate
  follows how much the tilted glass can still hold, the stream lands on the
  target's rising surface, and the surface ripples
- Glug sounds that rise in pitch as the target fills, a cork pop, and a chime that
  climbs a pentatonic scale with each vial you finish in a level
- Generated paintings, 12 named pigments, colour-blind symbols option,
  hidden-paint levels, hard and super-hard level intros, dead-end detection,
  hint and undo, tutorial on level 1, level road showing the sawtooth
- Light and dark themes, keyboard controls (number keys pick vials, arrows and
  Enter, U undo, H hint, R restart)

## Files

```
index.html               the app, built; open this
src/shell.html           the hub: home, settings, save, audio, sheets, game registry
src/games/paint-sort.html  Paint Sort: styles + script, registers itself with the shell
build.sh                 inlines every src/games/*.html into the shell -> index.html
tools/probe.mjs          prints the difficulty of each generated level (node tools/probe.mjs 1 60)
DESIGN.md                why Paint Sort works the way it does, with numbers
```

Edit files under `src/`, then run `./build.sh`. Set `ARTIFACT_OUT=some/path.html`
to also get the page without `<html>`/`<head>`/`<body>`, for hosts that add
their own.

## Adding a game

Drop a file in `src/games/` containing a `<style>` and a `<script>` that calls
`Playbox.register`, then rebuild. The shell gives each game a card on the home
shelf, its own save object, and a full-screen stage.

```js
Playbox.register({
  id: 'my-game',                       // also the #hash that opens it directly
  title: 'My Game',
  tagline: 'One line for the home card.',
  status: save => `Level ${save.level || 1}`,   // chip on the home card
  card(el, save) { /* draw the card's artwork into el */ },
  mount(stage, api) {
    // api.save        this game's saved object; mutate it, then api.persist()
    // api.persist(now) write to localStorage (debounced unless now is true)
    // api.audio       tone(), noise(), bell(): the shared synth
    // api.buzz(ms)    vibration, respects the setting
    // api.ui          sheet(), closeSheet(), toast(), h(), toggle(), openSettings()
    // api.on(ev, fn)  'theme' when light/dark changes, 'wipe' when progress is erased
    // api.exit()      back to the home shelf
    return { unmount() { /* stop loops, remove listeners */ } };
  }
});
```

Colours come from the shell's CSS tokens (`--bg`, `--surface`, `--ink`, `--accent`,
`--hard`, `--super`, …), which already switch for dark mode.

## Tuning Paint Sort

At the top of the engine section in `src/games/paint-sort.html`:

- `RAMP` is the shape of the sawtooth inside a block of ten. `BLOCK_STEP` is how
  much harder each block starts than the last.
- `PICK` chooses, per position in the block, which generated candidate to keep:
  0 is the most forgiving, 1 the most punishing.
- `K_CAP` is the colour ceiling per tier (normal 10, hard 11, super hard 12). It
  keeps the spikes above the ramp after colours stop growing.
- `spec()` also decides where hidden paint appears and how much.
- `PRICES` and `spec().reward` are the economy.

Run `node tools/probe.mjs 1 60` after any change. It regenerates every level,
checks each one is solvable, and prints the curve.

## Headless hooks

`window.__ps` exposes `spec(n)`, `generate(n)`, `solve(state, cap, budget)`,
`probe(from, to)` and, while the game is open, `state()`, `level()`, `tap(i)`,
`undo()`, `hint()`, `addVial()`, `restart()`, `solveNow()`, `idle()` and
`play(n)` (jump to level n).
