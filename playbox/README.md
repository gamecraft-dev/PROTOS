# Playbox

One app, a shelf of small games. The shell handles the home screen, settings,
saving and sound. Each game is a separate file that plugs into it.

**Games on the home screen**

Each game is a board on the home screen. The game you last played (or the first
playable one) gets the big board at the top; the rest sit in a two-column grid
below it.

| Game | What it is | Status |
| --- | --- | --- |
| **Paint Sort** | Pour paint between glass vials until every vial holds one colour. Levels are generated on the device to suit how you play; the 5th and 10th level of every ten are hard. | Playable |
| **Hex Tile Sort** | Hexa Stack ([`../hexa-stack`](../hexa-stack/)): drag stacks of hex tiles onto a 19-cell board; matching colours flip across and ten of a colour clear. Endless, with a best score. | Playable |
| **Car Loop** | Roundabout Rush ([`../roundabout`](../roundabout/)): tap to merge cars into a busy roundabout before the clock runs out. | Playable |
| **Cake Sort** | Drag plates of cake slices onto a counter; matching slices spin across to the plate next door until six make a whole cake. Ten cakes, each with its own look; levels adapt to how you play, with the same hard 5th and 10th levels as Paint Sort. | Playable |

Hex Tile Sort and Car Loop are standalone games that live in their own folders;
Playbox runs their finished pages inside the app (see *A game built elsewhere*
below) and adds a back button to each.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. `index.html#paint-sort`, `#hex-tile-sort`,
`#car-loop` and `#cake-sort` open straight into a game.

Why Paint Sort is built the way it is, and the measured difficulty curve:
**[DESIGN.md](DESIGN.md)**.

**Levels that adapt to the player.** Every game picks the difficulty of each
level when it starts, from an estimate of how well this player plays, so a
strong player isn't bored and a struggling one isn't stuck; the 5th and 10th of
every ten still spike (see *Adaptive difficulty* below).

**Building it in Unity.** Two documents cover the whole app:

- **[PLAYBOX_UNITY_PLAN.md](PLAYBOX_UNITY_PLAN.md)**: one brief for an AI agent
  (or a developer) to build Playbox and all four games in Unity 6 (URP,
  Universal 3D): the rules of each game, the architecture and code hierarchy,
  shared services (save, settings, audio, haptics, ads, purchases, analytics),
  the adaptive-difficulty model, the home screen of boards, every engine as C#
  to port, the 3D Hex Tile Sort and Cake Sort, every asset the agent generates
  in code, tests, milestones and golden values from the web engines.
- **[PLAYBOX_ASSETS.md](PLAYBOX_ASSETS.md)**: the assets you supply for each
  game's gameplay (just fonts; the agent generates everything else).

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
- Each board is mixed when you start the level, as hard as suits how you have
  been playing. Restarting keeps the same board; after two lost tries the
  restart sheet also offers to mix a gentler one.
- If the board can no longer be finished, a bar says so and offers undo, an
  extra vial or a restart.

Progress (level, coins, boosters, and the board you're partway through) is
saved on the device after every pour.

## Cake Sort: how to play

Drag a plate from the tray onto any empty spot on the counter (or tap a plate,
then tap a spot). Each plate holds up to six slices.

- When plates sit side by side (not corner to corner), slices of the same cake
  fly over to whichever plate can hold the most of that cake, spinning on the
  way, and the plate they land on turns to make room. Sorting chains: a plate
  that changes looks at its own neighbours next.
- Six slices of one cake make a whole cake. It spins, then flies up to the
  order card. Bake the number of cakes on the order to win the level.
- Empty plates are cleared away. If the counter fills up, use the hammer to
  clear one plate, undo, or start again.
- You get three plates at a time and three more once all three are down.
- You never wait for the sorting: drag the next plate down while slices are
  still flying. Each plate's sorting plays after the one before it.
- **Ten cakes**, each told apart by more than colour: Strawberry, Chocolate,
  Lemon, Matcha, Blueberry, Birthday, Mango, Cookies & Cream, Red Velvet and
  Caramel. Each has its own topping (a berry, a square of chocolate, a lemon
  wedge, a tea leaf, blueberries, a candle, mango cubes, a cookie, a raspberry,
  a hazelnut), its own layers where it is cut, a frosted or bare side, and a
  pattern on top. New cakes join the menu as you go (all ten by level 27), each
  shown off on a turntable the first time.
- **Boosters:** Undo (3 per try), Hammer (clears one plate), New plates (swaps
  the plates in your tray). Coins buy more.
- **Levels 5 and 10 of every ten are hard and super hard**, with glass cake
  stands blocking spots. They pay 30 and 60 coins; a normal level pays 10, plus
  5 more if you used no boosters.
- Each level is laid out when you start it, as hard as suits how you have been
  playing; a level you lost comes back a little easier.

The level in progress, coins, boosters and your collection are saved after
every plate.

## What's in the build

- Hub: home shelf, shared settings (sound, vibration, light/dark/auto theme,
  erase progress), one save file with a section per game, synthesised audio,
  haptics, sheets and toasts
- Level generator: deterministic per level number and heat, solver-checked,
  picked by simulated players (see DESIGN.md); the heat comes from the
  adaptive model
- A pour animation where the paint stays level as the vial tips: the pour rate
  follows how much the tilted glass can still hold, the stream lands on the
  target's rising surface, and the surface ripples
- Glug sounds that rise in pitch as the target fills, a cork pop, and a chime that
  climbs a pentatonic scale with each vial you finish in a level
- Generated paintings, 12 named pigments, colour-blind symbols option,
  hidden-paint levels, hard and super-hard level intros, dead-end detection,
  hint and undo, tutorial on level 1, level road showing the rhythm of each ten
- Light and dark themes, keyboard controls (number keys pick vials, arrows and
  Enter, U undo, H hint, R restart)
- Cake Sort: a pure rules engine (the sort, the plate dealer, the level curve)
  checked by simulated players; input that never waits for a sort (the
  engine settles each plate at once and the animations catch up through one
  queue); ten drawn cakes cut in six, in a 3D view where
  each slice shows its layers when cut; slices that spin as they fly, plates
  that turn to make room, finished cakes that spin and fly to the order card;
  a pitched pluck for every slice that lands (it climbs as the plate fills),
  chimes that climb with each cake in a chain; a cake collection; hard-level
  intros; a tutorial on level 1; keyboard controls (1 to 3 pick a plate, arrows
  and Enter put it down, U undo, H hammer, N new plates)

## Files

```
index.html               the app, built; open this
src/shell.html           the hub: home, settings, save, audio, sheets, game registry
src/games/paint-sort.html  Paint Sort: styles + script, registers itself with the shell
src/games/hex-tile-sort.html  Hex Tile Sort: board art + runs ../hexa-stack/index.html
src/games/car-loop.html  Car Loop: board art + runs ../roundabout/index.html
src/games/cake-sort.html  Cake Sort: styles + script, registers itself with the shell
build.sh                 inlines every src/games/*.html into the shell -> index.html,
                         embedding the two pages above
tools/probe.mjs          prints the difficulty of each generated level (node tools/probe.mjs 1 60)
tools/cake-probe.mjs     the same for Cake Sort (node tools/cake-probe.mjs 1 60)
tools/adaptive-sim.mjs   simulated players against the adaptive model (node tools/adaptive-sim.mjs model|cake|paint)
DESIGN.md                why Paint Sort works the way it does, with numbers
PLAYBOX_UNITY_PLAN.md    the brief for building Playbox and all four games in Unity
PLAYBOX_ASSETS.md        the assets you supply for each game (fonts)
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

## Adaptive difficulty

Each level is made at a **heat**: one number that turns every difficulty knob
of that game at once. The shell keeps a Bayesian estimate of the player's skill
on the same scale (`Playbox.skill`, between the `@skill-start` and `@skill-end`
markers in `src/shell.html`): a normal distribution with a mean and an
uncertainty, saved in each game's own save.

- **Picking a level.** Each slot of a block of ten has a target win rate: about
  .9 down to .78 on the run-up, **.5 on the 5th (hard)**, .88 to .76 after it,
  and **.36 on the 10th (super hard)**. The heat is the one at which this player
  wins with that chance, given what the model knows (`skillHeat`), clamped to a
  range around the level's block so late levels never fall back to the first
  ones. So the spikes are still spikes, measured against this player.
- **Learning.** Every attempt is read once: a win or a loss updates the
  estimate (a probit model, the same moment-matched update TrueSkill uses), and
  a win also says how easy it was (moves against the solver's, room left on the
  counter, time left) as a softer second reading. The uncertainty starts wide,
  so the first levels adjust quickly, then settles.
- **Mercy.** Each lost try at a level eases its target (`SKILL_MERCY`): a
  player stuck on a level gets a gentler version of it.
- **Per game:** Paint Sort's heat is the number of colours plus how punishing a
  candidate to keep; Cake Sort's turns the cakes on the menu, order size,
  cake stands, plates already out and how plates are dealt; Car Loop's is the
  level whose speed, traffic and clock a generated level takes (levels 1 to 10
  stay hand-made); Hex Tile Sort's turns stack height, colours per stack and
  how often new tiles match the board, every 7 clears (a "stage"; the 5th and
  10th of every ten are hard and super hard waves).

Why this and not something else: it needs no data to start, works from the
first level, runs instantly on the device, and its uncertainty makes it
forgiving while it knows little. Fixed-step ratings have no notion of
uncertainty; bandits or reinforcement learning over level parameters need a lot
of live data first.

`node tools/adaptive-sim.mjs model` plays idealised players of different skill
through 60 levels; `cake` and `paint` do the same with the games' real engines
and bots. On levels 21 to 60, the fixed curve the games used to have gave a weak
player first-try win rates of .14 / .01 / .00 on ordinary / hard / super-hard
levels and a strong one .99 / .89 / .67; with the model both land near the
targets .83 / .50 / .36 (.81 / .46 / .32 and .83 / .47 / .33).

## Tuning Paint Sort

At the top of the engine section in `src/games/paint-sort.html`:

- `RAMP` is the shape of the sawtooth inside a block of ten and `BLOCK_STEP`
  how much each block adds, for the first `BASE_BLOCKS` blocks: this is the
  typical curve (`baseHeat`) a new player starts on and the probe measures.
  `heatRange` is how far the model may move a level.
- `spec()` turns a heat into the level: `3 + floor(heat)` colours, and the
  fraction picks which of the generated candidates to keep (0 the most
  forgiving, 1 the most punishing; 10 candidates on super-hard levels, 8 on
  hard ones, 5 otherwise). It also decides where hidden paint appears and how
  much.
- `SKILL` (inside `mount`) is the model's prior and noise for this game.
- `PRICES` and `spec().reward` are the economy.

Run `node tools/probe.mjs 1 60` after any change. It regenerates every level of
the typical curve, checks each one is solvable, and prints it.

## Tuning Cake Sort

At the top of the engine section in `src/games/cake-sort.html`:

- `RAMP`, `BLOCK_STEP`, `BASE_BLOCKS` and `heatRange` are the typical curve
  and the model's range, as in Paint Sort.
- `spec()` turns a level's heat into the cake stands in the way (`blocked`,
  each worth `STAND_WORTH` of the heat; a hard level always has one and a
  super-hard level two), then the rest of the heat into the number of cakes on
  the menu (`K`), the order size (`goal`), the plates already out (`pre`), and
  how plates are dealt: `mix` and `mix3` (chance of a second and third cake on
  one plate), `help` (chance a plate's cake is one already on the counter) and
  `big` (chance of a 4- or 5-slice plate).
- `SKILL` (inside `mount`) is the model's prior and noise for this game.
- `UNLOCK_AT` is the level each cake joins the menu.
- `PRICES`, `UNDOS_PER_TRY` and `spec().reward` are the economy; `FLIGHT` and
  `STAGGER` time the slices in the air.

Run `node tools/cake-probe.mjs 1 60` after any change. It plays every level of
the typical curve (no model) with a casual and a skilled simulated player and
prints how often each fails. Measured over levels 1 to 100 (16 runs each):
normal levels hardly ever fail before level 40, then climb to a block average
of about 0.5 by level 80, where the typical curve stops climbing; hard levels
go from 0 in the first two blocks to about 0.4 by level 45 and 0.66 from level
85; super-hard ones from 0.03 at level 10 to about 0.5 by level 50 and close to
1 at levels 90 and 100. From level 20 on, both spikes sit above their block's
normal average. Real players get the heats the model picks for them, which
`node tools/adaptive-sim.mjs cake 60` measures.

## Headless hooks

`window.__ps` exposes `spec(n, h)`, `generate(n, h)`, `solve(state, cap, budget)`,
`probe(from, to)` and, while the game is open, `state()`, `level()`, `tap(i)`,
`undo()`, `hint()`, `addVial()`, `restart()`, `solveNow()`, `idle()`,
`play(n)` (jump to level n), `skill()`, `heatFor(n)`, `heat()` (this attempt's)
and `setSkill(mu, sd)`.

`window.__cs` does the same for Cake Sort: `spec(n, h)`, `newLevel(n, h)`,
`place(level, tray, cell)`, `resolve(cells, cell)` and `probe(from, to, runs)`
at any time, and while the game is open `state()`, `level()`, `place(tray, cell)`,
`canPlace(tray, cell)`, `sorting()`, `undo()`, `hammer(cell)`, `refresh()`,
`idle()`, `won()`, `where()` (screen positions of the tray and cells),
`play(n)`, `skill()`, `heatFor(n)`, `heat()` and `setSkill(mu, sd)`.
