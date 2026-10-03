# Playbox

One app, a shelf of small games. The shell handles the home screen, settings,
saving and sound. Each game is a separate file that plugs into it.

**Games on the home screen**

Each game is a board on the home screen. The game you last played (or the first
playable one) gets the big board at the top; the rest sit in a two-column grid
below it.

| Game | What it is | Status |
| --- | --- | --- |
| **Paint Sort** | Pour paint between glass vials until every vial holds one colour. Levels are generated on the device with a sawtooth difficulty curve: the 5th and 10th level of every ten are hard. | Playable |
| **Hex Tile Sort** | Hexa Stack ([`../hexa-stack`](../hexa-stack/)): drag stacks of hex tiles onto a 19-cell board; matching colours flip across and ten of a colour clear. Endless, with a best score. | Playable |
| **Car Loop** | Roundabout Rush ([`../roundabout`](../roundabout/)): tap to merge cars into a busy roundabout before the clock runs out. | Playable |

Hex Tile Sort and Car Loop are standalone games that live in their own folders;
Playbox runs their finished pages inside the app (see *A game built elsewhere*
below) and adds a back button to each.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. `index.html#paint-sort`, `#hex-tile-sort` and
`#car-loop` open straight into a game.

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
src/games/hex-tile-sort.html  Hex Tile Sort: board art + runs ../hexa-stack/index.html
src/games/car-loop.html  Car Loop: board art + runs ../roundabout/index.html
build.sh                 inlines every src/games/*.html into the shell -> index.html,
                         embedding the two pages above
tools/probe.mjs          prints the difficulty of each generated level (node tools/probe.mjs 1 60)
DESIGN.md                why Paint Sort works the way it does, with numbers
```

Edit files under `src/`, then run `./build.sh`. After changing Roundabout Rush,
run `../roundabout/build.sh` first so Playbox embeds the new page. Set `ARTIFACT_OUT=some/path.html`
to also get the page without `<html>`/`<head>`/`<body>`, for hosts that add
their own.

## Adding a game

Drop a file in `src/games/` containing a `<style>` and a `<script>` that calls
`Playbox.register`, then rebuild. The shell gives each game a board on the home
screen, its own save object, and a full-screen stage.

```js
Playbox.register({
  id: 'my-game',                       // also the #hash that opens it directly
  title: 'My Game',
  tagline: 'One short line for the board (keep it under ~55 characters).',
  order: 4,                            // position on the home screen
  status: save => `Level ${save.level || 1}`,   // chip on the board
  cta: save => save.level > 1 ? 'Continue' : 'Play',   // button label on the big board
  card(el, save, { featured }) { /* draw the board's artwork into el (fills it) */ },
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

**The board's own colours.** In the game's `<style>`, set `--b-accent` (button),
`--b-deep` (the slab under the board and the button's edge), `--b-soft` (chip
background), `--b-text` (chip text) and `--b-ink` (button text) on
`.board[data-game="my-game"]`, with dark-mode values in the same three blocks
the rest of the CSS uses. Without them a board uses Playbox blue.

**Small boards show a short status.** Everything after the first ` · ` in
`status()` is dropped on the small boards ("Level 4 · 120 coins" shows as
"Level 4"), so put the most important part first.

**A board before its game exists.** Register with `soon: true` and no `mount`:
the board shows its artwork with a lock, a "Coming soon" chip, and a toast when
tapped, and its `#hash` won't open anything. To link the game later, add its
`mount` and drop `soon`, keeping the same `id`.

**A game built elsewhere.** A game that already exists as its own page doesn't
need porting. In its file under `src/games/`, write
`const GAME_PAGE = /*@embed-base64:../my-game/index.html*/null;` (the path is
relative to `playbox/`); the build swaps in that page as base64. Then:

```js
mount: Playbox.framedGame({
  page: GAME_PAGE, title: 'My Game', background: '#101820',   // shown while it loads
  head: '...',   // optional HTML added before the page's </head>
  body: Playbox.exitButton({ into: '#menu .top-row', className: 'their-btn', size: 22 })
})
```

`framedGame` runs the page in a same-origin frame that fills the stage, so it
keeps its own screens, sound and `localStorage` save, and the board can read
that save for its chip. `exitButton` adds a back button as the first child of
`into`, styled with the game's own `className`; it posts `{playbox: 'exit'}`,
which closes the game. `car-loop.html` and `hex-tile-sort.html` are the two
examples; Hex Tile Sort also uses `head` to give the game the `window.storage`
it expects for its best score.

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
