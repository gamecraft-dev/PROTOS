# PROTOS

Playable mobile game prototypes. Each folder is a self-contained HTML file you
can open in a browser — no build step, no dependencies, no assets.

| Prototype | What it is | Status |
| --- | --- | --- |
| **[backfire](backfire/)** | Bouncing-ball breaker where blocks you cut loose fall, flip, and slam back up into the ceiling. | Current |
| **[blockcharge](blockcharge/)** | Block puzzle where clearing lines earns powers you pick and bank. | Playable |
| **[sparkweave](sparkweave/)** | Beam-routing roguelite on a 5×5 loom. Deep systems, but too much to explain for a casual audience. | Shelved — see note |

Each folder has a `DESIGN.md` with the market rationale, the balance numbers, and
the risks.

### Shared shape

All three are one file, vanilla JS, no libraries and no art assets — canvas or
DOM plus synthesised WebAudio. Each has `src/app.html` (artifact-host format, no
`<html>`/`<head>`/`<body>`) and a `build.sh` that splices those in to produce a
standalone `index.html`.

Two patterns are worth reusing:

- **Deterministic simulation, separate playback.** Sparkweave's `simulate()`
  emits an event log that the renderer animates. Balance can be measured without
  touching the renderer.
- **Headless balance probes.** Backfire exposes `window.__bf` with a `turbo(n)`
  time multiplier, and its difficulty curve was tuned by running bot games under
  Playwright rather than by guessing. The first tuning pass was badly wrong and
  the probe is the only reason that was caught.

### Note on sparkweave

Kept because the engine work is reusable. Shelved as a product because it needed
a tutorial before a player could tell what they were looking at, which is
disqualifying for a mass-market casual title.
