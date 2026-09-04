# Blockcharge

Block puzzle with one change: clearing lines charges a meter, and filling it lets
you **pick a power** — a bomb, a laser, or a fresh set of blocks — which you bank
until you need it. When nothing fits, that banked power digs you out instead of
the game just ending.

**Play it:** open `index.html` in any browser. No build step, no dependencies.
Best on a phone, portrait.

Why this design, what it improves on Block Blast and Woodoku, and the honest
competitive read: **[DESIGN.md](DESIGN.md)**.

---

## How to play

Drag blocks onto the 8×8 grid. Fill a full row or column and it clears. Blocks
don't rotate. When you've placed all three, three more arrive.

- Clear more than one line in a move, or clear on back-to-back moves, and the
  points multiply.
- Every clear fills the charge meter. Full meter → pick a power.
- **Bomb** clears a 3×3 patch. **Laser** clears a row and column. **Swap** deals
  three new blocks.
- The game only ends when none of your three blocks fit anywhere — and a power
  can still save you.

You can also tap a block to select it, then tap the grid to place it.

## What's in the build

- 4-step tutorial that guarantees a line clear on your first placement
- One-time tip cards for the charge meter, the first level-up, the first time
  you get stuck, and the daily board
- Pause, stuck/rescue, game over, power picker, daily result, how-to-play,
  settings
- 29 block shapes, 3 powers, 2 power slots, combo and level multipliers
- Never deals three blocks that can't be placed
- Daily Board: same blocks for everyone, one attempt, copyable emoji share card
- Placement preview that shows exactly which lines a drop would clear
- Particles, screen shake, floating scores, banners, synthesised audio, haptics
- Light and dark themes, calm mode, progress saved to localStorage

## Files

```
index.html     the game — open this
src/app.html   source (no <html>/<head>/<body>; the artifact host supplies those)
build.sh       wraps src/app.html into the standalone index.html
DESIGN.md      the rationale, the tweak, monetisation, risks
```

Edit `src/app.html`, then run `./build.sh`.

## Tuning knobs

Top of the script in `src/app.html`:

- `SHAPES` — the block set, each with a spawn weight. Add or reweight freely.
- `POWERS` — the three powers; `target:true` means it needs a tap on the board.
- `CHARGE_MAX` / `SLOT_MAX` — how often powers arrive and how many you can hold.
  These two are the whole difficulty dial.
- `LINE_MULT` — the multi-line bonus curve.
- `refillTray()` — the guaranteed-legal-deal rule lives here.
