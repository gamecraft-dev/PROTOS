# Hexa Stack

An endless hex-stacking puzzle. Drag a stack of coloured hex tiles from the tray
onto an empty cell of the 19-cell board. Any neighbouring stack whose top colour
matches sends its top run across, tile by tile, and merges cascade. Ten tiles of
one colour clear. A new colour joins every seven clears, and the run ends when
the board is full.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait. ← and → (or the buttons at the bottom) rotate the
board, so a stack hidden behind a tall one can be brought forward.

In [Playbox](../playbox/) this game appears as **Hex Tile Sort**. Playbox runs
this page unchanged and adds two things around it: a back button in the header,
and the `window.storage` the game uses to keep its best score (backed by
`localStorage`, under keys starting `playbox.hexa-stack.`). Opened on its own
outside Claude, the page has no `window.storage`, so the best score lasts only
until the page is closed.

For a Unity build (in 3D, as part of Playbox), see
[`../playbox/PLAYBOX_UNITY_PLAN.md`](../playbox/PLAYBOX_UNITY_PLAN.md) (Part III)
and [`../playbox/PLAYBOX_ASSETS.md`](../playbox/PLAYBOX_ASSETS.md) (section 3).

## Files

```
index.html   the whole game: one file, canvas + synthesised WebAudio
```

## Tuning knobs

Top of the script in `index.html`: `CLEAR_AT` (tiles per clear), `CLEAR_GRACE`
(how long a full stack waits to be fed before it clears), `CLEARS_PER_TIER`
(clears per new colour), `START_COLOURS`, `SEED_STACKS`, and `stackHeight()` /
`pickColour()` for how the tray stacks are dealt.
