# PROTOS

Playable mobile game prototypes. Each folder is a self-contained HTML file you
can open in a browser — no build step, no dependencies, no assets.

| Prototype | What it is | Status |
| --- | --- | --- |
| **[playbox](playbox/)** | A multi-game app: a home screen of game boards with shared saving, settings and sound. Plays **Paint Sort** (pour paint between vials until each holds one colour, levels generated on a sawtooth difficulty curve); **Hex Tile Sort** and **Car Loop** have boards and are coming soon. | Current |
| **[roundabout](roundabout/)** | Roundabout Rush: tap to merge your cars into a busy roundabout before the clock runs out. Full publishing shell: boosters, garage economy, mocked ads and store, Unity asset list. | Current |
| **[backfire](backfire/)** | Bouncing-ball breaker where blocks you cut loose fall, flip, and slam back up into the ceiling. | Playable |
| **[blockcharge](blockcharge/)** | Block puzzle where clearing lines earns powers you pick and bank. | Playable |
| **[sparkweave](sparkweave/)** | Beam-routing roguelite on a 5×5 loom. Deep systems, but too much to explain for a casual audience. | Shelved — see note |

Each folder has a `DESIGN.md` with the market rationale, the balance numbers, and
the risks. Roundabout also has an `ASSETS.md` listing what a Unity build needs.

### Shared shape

All of them build to one file, vanilla JS, no libraries and no art assets — canvas or
DOM plus synthesised WebAudio. Each has its source in artifact-host format (no
`<html>`/`<head>`/`<body>`) under `src/` and a `build.sh` that produces a
standalone `index.html`. Playbox splits its source into a shell plus one file per
game; its `build.sh` inlines the games back into a single page.

Three patterns are worth reusing:

- **Deterministic simulation, separate playback.** Sparkweave's `simulate()`
  emits an event log that the renderer animates. Balance can be measured without
  touching the renderer.
- **Headless balance probes.** Backfire exposes `window.__bf` with a `turbo(n)`
  time multiplier, and its difficulty curve was tuned by running bot games under
  Playwright rather than by guessing. The first tuning pass was badly wrong and
  the probe is the only reason that was caught.
  Playbox's Paint Sort goes one step further: its level generator is pure JS
  between two markers, and `tools/probe.mjs` runs it in Node to print the
  difficulty of every level, measured by simulated players.
- **Levels proven by bots that play like people.** Roundabout generates every
  level from a seed, then only ships it if a frame-perfect bot, a reference
  player and a cautious player can all clear it; the clock comes from the
  reference player's time. A clock based on the frame-perfect bot alone made
  every level from 7 onward unwinnable for human-like play.

### Note on sparkweave

Kept because the engine work is reusable. Shelved as a product because it needed
a tutorial before a player could tell what they were looking at, which is
disqualifying for a mass-market casual title.
