# Sparkweave — prototype rationale

A playable vertical slice for evaluating whether this is worth building. The
prototype is `index.html`; this document is the argument behind it.

---

## 1. Why this genre, and what I deliberately avoided

The brief was: ride a rising trend, but do not enter a category that has already
peaked, because a solo dev cannot buy users against an entrenched leader.

**What the 2026 data says is rising:**

- Hybrid-casual was the **only** casual segment to grow IAP revenue last year —
  up 20% to $4.2B, with the top 10 titles posting 67–100% YoY IAP growth. Growth
  is concentrated in hybrid-casual *puzzle*.
- Global IAP hit $167B (+10.6%) while downloads *fell* 7.2% to 50.4B. Installs
  are getting harder; retention and depth are where the money moved.
- The daily seeded challenge + shareable result card is now a standard retention
  primitive ("one shared challenge, a few minutes, compare with friends, done").
  It costs a solo dev almost nothing and is the cheapest organic acquisition
  channel left.
- Spatial adjacency-synergy systems are validated: Backpack Battles brought the
  inventory/adjacency auto-battler to iOS and Android in February 2026.

**What I ruled out, and why:**

| Ruled out | Reason |
| --- | --- |
| Roguelike deckbuilder | Post-Balatro the category is "very crowded, especially on mobile." Card-format twists are the single most copied idea of the last 18 months. |
| Block puzzle / match-3 | Leading downloads, but Azur's own report warns entering is "extremely difficult" — the incumbents have a decade of tuning, content pipelines and UA budgets. This is precisely the tenfold-expertise trap. |
| Backpack / inventory-grid | This is the one that matters. The mechanic is rising, but the *format* has crested: Backpack Battles landed on both stores in Feb 2026, and Backpack Brawl, Backpack Attack and Backpack Legends are already shipping into its wake. Building a fourth backpack game in 2026 is competing for users against a game that just got the whole genre's press. |
| Survivor-likes, merge-mansion, idle tycoon | Peaked 2023–24; incumbent live-ops moats. |

**The gap I aimed at:** take the *rising* mechanic (spatial adjacency, chain
resolution, build-a-machine) out of the *crested* format (a backpack of RPG
loot), express it through a verb every mobile player already knows (drag a piece
onto a grid), and resolve it with the one thing those games do not have — a
visible, animated chain reaction that is its own ad creative.

Azur's advice for small teams, verbatim: pick genres where "established players
do not have a tenfold expertise advantage." Nobody owns "beam-routing roguelite"
on mobile.

---

## 2. The game in one paragraph

You place glyphs on a 5×5 loom. Then you ignite: a beam leaves the source, runs
in a straight line, and every glyph it touches fires — paying light, bending the
beam, refilling its charge, or multiplying the whole weave. Each glyph fires up
to three times per weave, so the skill ceiling is **routing the beam into a
closed loop** so it runs your best glyphs again and again. Charge drains one per
cell entered — empty cells included — so the beam is a fuse and the board is the
machine you build with it. Beat the thread's quota or the run ends.

Everything you place stays for the whole run. By thread 8 the board is a machine
you built three pieces at a time.

### Why the verb works on a phone
- Drag-and-drop onto a grid. One thumb, no dexterity, no reaction time.
- The resolution is a spectator moment — you set it up, then watch it go off.
  That is the same dopamine shape as a slot pull or a Balatro score-count, and it
  is inherently ad-friendly: a 6-second capture of a chain 36 cascade *is* the
  UA creative, with no bespoke ad production.
- A thread is ~20 seconds. A run is 4–6 minutes. Genuinely snackable, unlike
  Backpack Battles, which reviewers flagged as "not a commute game."

---

## 3. Measured numbers (from the actual simulator, not estimates)

A competent player growing one board three glyphs at a time, against the shipped
quota curve:

| Thread | Glyphs | Charge | Quota | Score reached | Chain | Margin |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 | 10 | 18 | 21 | 3 | 1.17× |
| 2 | 6 | 10 | 36 | 48 | 6 | 1.33× |
| 4 | 10 | 12 | 100 | 130 | 15 | 1.30× |
| 5 | 13 | 12 | 175 | 412 | 33 | 2.35× |
| 6 | 15 | 12 | 290 | 888 | 36 | 3.06× |
| 8 | 21 | 14 | 720 | 888 | 36 | 1.23× |

Two things this table proves, and they are the reasons to keep going:

1. **The engine has a real power curve.** Score climbs 21 → 888 not because
   numbers got bigger but because the player closed a loop. The jump at thread 5
   is the moment the circuit closes — that is the game's "aha", and it is
   dramatic enough to be felt.
2. **There is a natural wall.** The loop caps at three laps (glyphs burn out after
   three fires), so scores plateau at 888 while the quota keeps climbing. Threads
   7–8 force a second decision: extend the ring, or plant high-value one-shots
   (Thorn +26, Fuse +70) on the escape path. That is a genuine second strategic
   layer arriving exactly when the first one runs out — which is what a run-based
   game needs to survive contact with a good player.

Balance is a first pass. It is tuned to be clearable, not solved.

---

## 4. Retention and monetisation (designed in, demoed in the build)

**Hybrid-casual, ad-led, IAP-supported** — matching where the growth actually is.

| Layer | In the prototype | Notes |
| --- | --- | --- |
| Rewarded ad — Second Wind | Mock button on the game-over panel, once per run | The single highest-yield rewarded placement in run-based games. Offered at peak loss aversion. |
| Rewarded ad — Restock the Stall | Natural fit (button exists as a filament cost) | Convert the ◈2 restock into an optional ad view. |
| Meta currency (Shards) | Workshop, 6 permanent upgrades | Paid out win *or* lose, which is what makes a failed run worth finishing. This is the hybrid-casual meta that turns a hypercasual loop into a retained one. |
| Daily Loom | Seeded run, one attempt, emoji share card | The share card is the board itself — a 5×5 emoji grid that is genuinely different every day and readable at a glance. Wordle-shaped, and free acquisition. |
| Cosmetics (not built) | Beam colours, loom skins | Non-pay-to-win IAP; the beam is on screen for the whole cascade, so skins are visible where it counts. |
| Battle pass (not built) | — | Only worth it after D7 proves out. |

**Deliberately not in the design:** energy timers, PvP, and anything requiring
live-ops content churn — all three are where a solo dev loses to a studio.

---

## 5. Production reality for one person

The prototype is 2,000 lines of vanilla JS with **zero art assets**. Every glyph
is a typographic mark; every effect is canvas; every sound is synthesised at
runtime. That is not a prototype shortcut — it is the actual art direction, and
it means:

- No artist dependency, no art pipeline, no asset budget.
- Localisation is trivial (no baked text in art; ~60 strings).
- New content is a data row: a glyph is a name, an icon, and a `fire()` function.
  16 glyphs shipped here in about 60 lines total. 60 glyphs is a weekend.
- Build target: Unity or Godot for store deployment, or ship the web build in a
  thin native wrapper. The simulation is already pure and deterministic, so it
  ports without redesign.

**Rough scope to soft launch:** 6–10 weeks solo, assuming the core stays as-is
and the work is content (40+ glyphs), meta depth, store presence, and ad SDK
integration.

---

## 6. Risks — the honest list

1. **Auto-resolution means no agency during the payoff.** Mitigated by making the
   setup the whole game, but if playtesters find the cascade boring by run 10, the
   game needs a tap-to-trigger active during resolution. Watch for this first.
2. **Beam routing may be too "puzzle" for casual players.** The mirror-direction
   mental model is the hardest thing to teach; the tutorial spends three of its
   six steps on it. If D1 tutorial completion is under ~75%, simplify to vanes only
   for the first three threads.
3. **The three-fire cap is doing a lot of balance work.** If players find an
   unbounded loop the economy breaks. Currently bounded by both fire caps and the
   900-step simulation ceiling.
4. **"Roguelite with a quota" reads as Balatro-adjacent** to genre-literate
   players, even though the verb is different. Worth watching in store reviews;
   the answer is to lean the presentation harder into the loom/circuit fantasy.
5. **Daily-challenge virality is not free.** The share card only spreads if the
   board is pretty. It is currently good; keep it a design constraint.

---

## 7. What to look for while playing

- Does the first cascade land? (It should read as "oh, *that's* the game.")
- Thread 3–5: do you find the loop on your own, or did the hint card have to tell
  you? The hint is a fallback, not the plan.
- Thread 7–8: does the plateau feel like a wall or a puzzle?
- Would you tap Second Wind?
- Would you come back tomorrow for the Daily Loom?

If the answer to the first and last are yes, this is worth building.
