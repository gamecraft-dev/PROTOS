# Sparkweave

A mobile roguelite prototype: place glyphs on a 5×5 loom, fire a beam through
them, chain the cascade. Built to be played on a phone and judged by feel.

**Play it:** open `index.html` in any browser. No build step, no server, no
dependencies. Best in a narrow window or on a phone (portrait).

Why this genre and whether it is worth building: **[DESIGN.md](DESIGN.md)**.

---

## Controls

| Action | How |
| --- | --- |
| Place a glyph | Drag it from the hand onto a cell, or tap the glyph then tap the cell |
| Rotate a mirror or vane | Tap it on the loom |
| Read what a glyph does | Long-press it on the loom |
| Take back a glyph | Long-press one you placed this thread |
| Fire the beam | **Ignite** |
| Redraw your hand | ↻ (costs ◈2, or free with the Loose weft upgrade) |

## The rules

1. A beam leaves the **source** (bottom-left) heading up.
2. It travels in a straight line. Mirrors turn it 90°, vanes point it, bulwarks
   reverse it, prisms split it.
3. Every cell it enters costs **1 charge** — empty cells too. At zero, the weave
   ends.
4. Every glyph it touches **fires**, up to three times per weave.
5. **Light × Weave** is your score. Beat the thread's quota or the run is over.
6. Everything you place stays for the whole run. Hold all eight threads to win.

The skill is routing the beam into a closed loop so your best glyphs fire three
times each. A vane pointing up plus mirrors on the other three corners makes a
ring the beam runs until its glyphs burn out.

## What's in the build

- Scripted 6-step first-time tutorial with spotlight coaching
- One-time onboarding cards for every system as it appears: loops, the Stall,
  knot modifiers, running out of charge, the Workshop, the Daily Loom
- Pause, round-cleared, shop, game-over (with a mock rewarded-ad revive),
  victory, endless mode, codex, workshop, settings, how-to-play
- 16 glyphs across 4 families, 4 knot modifiers, 6 permanent meta upgrades
- Daily Loom: seeded run, one attempt, copyable emoji share card
- Canvas beam trails, particles, floating numbers, screen shake, chain popups
- Synthesised audio (WebAudio, no files), haptics, reduced-motion and fast-weave
  settings, progress saved to localStorage

## Files

```
index.html     the game — open this
src/app.html   source (no <html>/<head>/<body>; the artifact host supplies those)
build.sh       wraps src/app.html into the standalone index.html
DESIGN.md      market rationale, measured balance data, monetisation, risks
```

Edit `src/app.html`, then run `./build.sh` to regenerate `index.html`.

## Tuning knobs

Everything worth pulling is at the top of the script in `src/app.html`:

- `GLYPHS` — one object per glyph: name, icon, family, cost, and a `fire()`
  function. Adding a glyph is adding a row.
- `QUOTAS` — the eight thread quotas.
- `MODS` — knot (boss) modifiers.
- `META` — permanent Workshop upgrades.
- `maxCharge` in `newRun()` — the single most powerful balance lever.

The simulation (`simulate()`) is pure and deterministic: it takes the board and
returns an event log, which the playback layer animates. Balance changes can be
measured headlessly without touching the renderer.
