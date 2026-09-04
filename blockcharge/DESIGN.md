# Blockcharge — prototype rationale

Block puzzle, plus one change. The prototype is `index.html`; this is the
argument behind the change.

---

## 1. The reference, and why I stopped fighting it

The last prototype failed the only test that matters for a mass-market game: you
should not need a tutorial to understand what you are looking at. So this one
starts from the most understood verb on mobile.

- **Block Blast**: ~368M downloads, **zero IAP**, pure ad monetisation.
- **Woodoku** (Tripledot): 100M+ downloads, 4.8 stars, marketed as "2026's
  hottest puzzle."

Nobody has ever had to be told how these work. Drag a shape onto a grid, fill a
line, the line pops. That comprehension is worth more than any novel mechanic,
and it is the thing my previous prototype did not have.

**The honest tradeoff:** this is the single most contested category on mobile,
and a solo dev will not out-spend Tripledot on user acquisition. The bet here is
not "win the category" — it is "be the version of it that a player who already
likes the genre switches to and tells someone about." That means the tweak has to
be a real improvement, not a reskin, and it means organic channels (the daily
board, the share card, word of mouth) carry the growth rather than paid installs.
If you want a category where UA is winnable, that is a different brief and I
should build for that instead.

---

## 2. What players actually complain about

Not the mechanic. The reviews are consistent: the core loop is "addictive... relaxing
and stimulating," and the frustration is **ad frequency** — "the majority of ads
are 20 or more seconds and some go to the app store when tapped on the X."
Aggressive ad load is named as the churn risk that undermines these games'
acquisition.

And Deconstructor of Fun's read on where the genre is going: boosters "act as
critical safety valves that allow players to reverse bad luck, modify the board
layout, and extend competitive runs that would otherwise end."

Put those together and the design writes itself. The genre's structural weakness
is that **the run ends by bad luck, at a moment where the only options are pay,
watch an ad, or quit.** Every competitor sells you out of that moment. That is
where the tweak goes.

---

## 3. The tweak: powers you earn, choose, and bank

Every line you clear fills a charge meter. Fill it and **you pick a power** —
Bomb (clears 3×3), Laser (clears a row and column), or Swap (three fresh blocks).
It sits in a slot until you decide to spend it.

Three things follow from that, and all three are improvements on the reference:

1. **The booster is earned by playing well, not bought.** It stays inside the one
   verb the player already understands — you place it on the board like anything
   else. No separate booster shop, no currency, no menu.
2. **The dead end becomes a decision.** When nothing fits, the game does not end;
   it asks what you want to do about it. A player who banked a Bomb three moves
   ago gets rewarded for restraint. That converts the genre's worst moment — an
   arbitrary loss — into the moment the player feels smartest.
3. **The rewarded ad becomes optional rather than extortionate.** It is still
   there (clear the bottom two rows, once per game) but it competes with a free
   answer the player earned. That is the opposite of the ad-load complaint, and I
   think it is the more defensible long-term position.

There is a fourth, quieter improvement: **the game never deals you three blocks
that cannot be placed.** The tray reroll checks for a legal move before handing
you the deal. Players quit over unwinnable deals, not over hard ones.

### What I deliberately did not add
No rotation (it is the proven form, and every added rule costs comprehension), no
energy timers, no levels-with-objectives, no PvP. The tweak budget was spent in
one place.

---

## 4. Numbers

| | |
| --- | --- |
| Board | 8×8 |
| Tray | 3 pieces, 29 shapes, no rotation |
| Scoring | cells placed, then `cleared × 10 × lineMult × comboMult × levelMult` |
| Line multiplier | 1 / 1.6 / 2.4 / 3.4 / 4.5 for 1–5 lines at once |
| Combo | +25% per back-to-back clearing move, caps at ×3 |
| Level | every 10 lines; +5% score per level |
| Charge | +3 per line, +2 per extra line in the same move; power at 12 |
| Power slots | 2 |

A clean single-line clear early is 83 points; a double with a combo running is
several hundred. The curve is a first pass — it is tuned to feel good, not solved.

---

## 5. Monetisation

Ad-led, matching the reference, but placed where it does not poison the loop:

| Placement | Why |
| --- | --- |
| Rescue at the stuck moment (in the prototype, mocked) | Highest-intent moment in the game. Optional, because powers do the same job for free. |
| Interstitial between games | Standard. Frequency-capped — the reviews above are what happens when it is not. |
| Optional "double your score" at game over | Untested, but the natural second placement. |
| Cosmetic block skins (not built) | Non-pay-to-win IAP. The blocks are on screen constantly. |

No energy, no paywalled boosters, no forced ad after every clear. The category's
biggest complaint is the easiest thing to beat them on.

---

## 6. Retention

- **Daily Board** — same blocks, same order, one attempt, copyable emoji grid of
  your final board. The proven and nearly free retention primitive.
- **Personal best** — one number, always on screen, always beatable.
- **Levels** — a visible pace marker with no fail state attached.

---

## 7. Risks

1. **Powers could trivialise the game.** Two banked powers plus the ad rescue is a
   lot of forgiveness. If runs stop ending, raise the charge cost or cut to one
   slot. Watch average run length first.
2. **The category is brutal.** Comprehension is solved; discovery is not. Growth
   here is organic or it is nothing.
3. **The guaranteed-fit deal removes some tension.** It is the right call for
   retention, but if the game feels too safe, that is the first knob I would
   reconsider.

---

## 8. What to look for while playing

- Did you need any of the tutorial, or was it obvious before it spoke?
- The first time your meter fills — is picking a power a real decision?
- When you get stuck: does spending a banked power feel like a save you earned,
  or like the game bailing you out?
- Would you play tomorrow's Daily Board?
