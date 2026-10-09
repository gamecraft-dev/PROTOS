# Paint Sort: design notes

The first game on the Playbox shelf. The prototype is `index.html`; this is the
reasoning behind it and the numbers it was tuned with.

---

## 1. The reference

Colour-sort puzzles are one of the most crowded shelves on the Play Store
(*Water Sort Zen*, *Sort Paint: Water Sort Puzzle*, *Painting Sort: Color Sort*,
*Colorwood Sort* and many more). They share one rule set that nobody has to be
taught:

- tubes hold four units; tap one tube, tap another, and the top colour pours
  across;
- paint only lands on its own colour or in an empty tube, and only as much as
  fits;
- the board is solved when every tube is empty or one colour;
- boosters are undo, an extra tube, and sometimes a hint;
- "mystery" tubes hide the lower layers behind a question mark until they are
  exposed.

The *paint* variants that are trending now add a reward layer on top: finishing a
colour paints part of an artwork, so a level ends with a picture rather than a
row of full tubes.

I kept the rule set exactly. Comprehension is the whole value of the genre, and
every added rule costs some of it.

## 2. What this version adds

1. **A painting per level, revealed by the pigments you finish.** Each level
   generates an abstract composition with one shape per colour, drawn as a pencil
   underdrawing. Each vial you finish brushes its pigment into its shape, and
   the finished picture is the win screen ("Study No. 12"). The pigments are
   real paint names (Ultramarine, Burnt Sienna, Payne's Grey…), shown as each
   vial is corked. This is the paint-sort hook, and it costs no extra rules.
2. **The game tells you when you're stuck.** Most sort games let you pour back
   and forth in a dead position until you give up. Here a solver checks the
   board after each pour. If the board is proven unwinnable, a bar says "No way
   out from here" and offers Undo, an extra vial, or Restart. In a test of 20
   random games each on levels 30, 60, 100 and 120, 16 to 19 of every 20 were
   in a proven dead end after 12 to 31 random pours, so this fires often enough
   to matter. The check runs a few milliseconds after each pour (capped at 5,000
   searched positions), so it never holds up play.
3. **Hints come from a real solver.** A hint is the first move of an actual
   solution from the current position, not a guess. If there is no solution, the
   hint booster tells you so and is not spent.
4. **Levels are generated, not authored, and every one is checked.** See §3.
5. **Difficulty follows a sawtooth, fitted to the player, and you can see it.**
   Every level is mixed when it starts, as hard as suits this player (§4), and
   the level road in the lobby plots the ten levels of the current block by how
   often each is meant to be lost, so a player can see the spikes at 5 and 10
   coming and the breather after them.

### What I deliberately left out
Timers, lives, energy, move limits and ads. The prototype has coins and a
booster shop so the economy can be tuned, but nothing sells the player out of a
dead end: the dead-end bar and the free Restart always offer a way on.

## 3. Level generation

`generate(n)` in `src/games/paint-sort.html`. It is deterministic: a level number
always produces the same board on every device, so Restart replays the same
puzzle, a reinstall doesn't reshuffle the campaign, and a player can describe
level 37 to someone else.

1. `spec(n)` turns the level number into targets: colours, empty vials (always
   2), how much paint is hidden, how many candidates to try, and which one to
   keep.
2. Deal candidates: shuffle the paint into full vials, rejecting deals where a
   vial starts complete or where too many units already sit together.
3. **Solve each candidate** (weighted A* over canonicalised states, budget
   25k nodes). Unsolvable or unproven deals are thrown away. Every shipped board
   has a known solution.
4. **Measure each candidate with two simulated players.** A *casual* player
   never looks ahead: it always finishes a vial if it can, prefers stacking onto
   matching paint, and otherwise pours at random. A *steady* player rates every
   pour one move deep (finish a vial, move whole runs, don't spend empty vials,
   uncover paint that has somewhere to go) and adds a little noise. Each plays
   the board 14–20 times; difficulty is their combined failure rate.
5. Sort the candidates by difficulty and keep the one the level's heat picks
   (§4): the fraction of the heat runs from the easiest candidate to the
   hardest.
6. Choose the palette and the hidden layers from the same seed.

Generation takes 33 ms on average for levels 1–30 and never more than about
350 ms up to level 120 (Node, one core). The next level is mixed while the win
screen is showing, so the player never waits.

## 4. The sawtooth, and fitting it to each player

Every level is made at a **heat**. The whole part of the heat sets the colours
(`3 + floor(heat)`, up to 12); the fraction picks which generated candidate to
keep, from the most forgiving to the most punishing (10 candidates are made for
a super-hard level, 8 for a hard one, 5 otherwise). The same level number and
heat always give the same board.

**The typical curve.** Levels come in blocks of ten. Inside a block the heat
climbs, spikes at the 5th level (**hard**), drops back, climbs again and spikes
harder at the 10th (**super hard**). Each of the first four blocks starts
`BLOCK_STEP` (1.15) higher than the last; after that the curve stops climbing,
and how hard a level gets is up to the player's skill.

```
RAMP (in-block heat):  0  .45  .9  1.35  [2.5]  .6  1.05  1.5  1.95  [3.6]
heat = RAMP[pos] + 1.15 × min(block, 4)
```

That curve is what a new player starts on, and what the probe measures:
`node tools/probe.mjs 1 30`. *Difficulty* is the share of simulated games lost;
*moves* is the solver's solution length.

```
 lvl  tier  colours hidden moves  difficulty
   1              3       0      9  ........................  0.00
   2              3       0     10  ........................  0.00
   3              3       0     12  ........................  0.00
   4              4       0     13  ........................  0.00
   5   HARD       5       0     18  #.......................  0.05
   6              3       0     11  ........................  0.00
   7              4       0     12  ........................  0.00
   8              4       0     14  ........................  0.00
   9              4       0     15  ........................  0.00
  10   SUPER      6       0     22  ######..................  0.23
  11              4       0     13  ........................  0.00
  12              4       0     15  ........................  0.00
  13              5       2     15  ........................  0.00
  14              5       0     15  #.......................  0.04
  15   HARD       6       9     21  ######..................  0.25
  16              4       0     13  #.......................  0.04
  17              5       0     16  #.......................  0.04
  18              5       5     16  ##......................  0.07
  19              6       0     18  ##......................  0.07
  20   SUPER      7      15     23  #############...........  0.53
  21              5       0     18  #.......................  0.04
  22              5       0     17  #####...................  0.21
  23              6       4     21  ###.....................  0.14
  24              6       0     21  ###########.............  0.46
  25   HARD       7      15     22  ###############.........  0.63
  26              5       0     17  ####....................  0.18
  27              6       0     18  ........................  0.00
  28              6       9     20  #######.................  0.29
  29              7       0     23  ###.....................  0.14
  30   SUPER      8      11     27  #################.......  0.72
                                      

mean difficulty   normal 0.07 · hard 0.31 · super 0.49
```

Two teeth per block, the 10th sharper than the 5th, a real drop straight after
each one, and every block starting above the last.

**Fitting it to the player.** A fixed curve is too easy for some players and
too hard for others. Playbox keeps a Bayesian estimate of each player's skill
on the heat scale: a normal distribution with a mean and an uncertainty (the
model is shared by every game, in `src/shell.html`).

- Each slot of a block of ten has a **target win rate**: about .9 falling to
  .78 on the run-up, **.5 on the hard 5th**, .88 falling to .76 after it, and
  **.36 on the super-hard 10th**. A level is made at the heat this player beats
  with that chance, given what the model knows. The spikes stay spikes, measured
  against the player rather than against an average.
- The heat stays within a range around the level's block (never below 2.5 under
  the block's start, never more than 4 over its hardest level), so a late level
  never turns into a first one.
- **Every attempt is read once.** A finished board is a win, and how close the
  pours came to the solver's says how easy it was (undo, hint or the extra vial
  count against that); a proven dead end, or giving up after 3 or more pours, is
  a loss. A win or loss updates the estimate with the moment-matched probit
  update TrueSkill uses; the ease of a win is a softer second reading.
- **Mercy.** Each lost try at a level eases its target for the next try. A
  restart keeps the same board (players expect to retry the same puzzle), but
  after two lost tries the restart sheet also offers to mix a gentler one.

With idealised players (`node tools/adaptive-sim.mjs model`, levels 21–60,
first-try win rates on ordinary / hard / super-hard levels against targets
.83 / .50 / .36):

| Player | Fixed curve | Adaptive |
| --- | --- | --- |
| Weak | .14 / .01 / .00 | .81 / .46 / .32 |
| Typical | .51 / .11 / .02 | .82 / .47 / .32 |
| Strong | .99 / .89 / .67 | .83 / .47 / .33 |

`node tools/adaptive-sim.mjs paint` runs the same check with Paint Sort's own
generator and simulated players (slow, because every level is solved).

**Where the measurement runs out.** Above about heat 7 (10 or more colours)
both simulated players lose almost every game, so the probe's difficulty column
saturates near 1.0. The spikes still have more colours, more hidden paint and
longer solutions, but the probe can't rank boards precisely at that end, and
only players the model rates highly get there. A stronger simulated player
(two-move lookahead) is the fix if those levels need finer tuning.

## 5. The pour

The pour is the verb the player repeats a thousand times, so it got the most
work.

- **The paint stays level.** Liquid is drawn in world space, clipped to the glass,
  with a flat surface found by solving for the height that encloses the right
  area. When the vial tips, the paint slides toward the lip as it would in real
  glass.
- **The pour rate follows the physics.** The vial tips about its lip. A
  precomputed table gives how much the glass still holds at each angle, so the
  pour starts at exactly the angle where the surface reaches the lip, and paint
  leaves only as the vial tips further. Pouring one unit is a small tilt;
  emptying a vial tips it past horizontal.
- **Timing:** 230 ms to lift and swing over the target, 190 + 105 ms per unit
  poured, 280 ms back with a slight overshoot. The stream is 85 ms behind the
  lip, the target's surface rises with it and ripples, and droplets splash up
  from the impact. Other vials can be tapped during a pour, so fast players are
  never held up.
- **Finishing a vial:** a cork drops in with a bounce, a coloured glow pulses,
  sparks burst, and the pigment's name floats up.

## 6. Sound

Everything is synthesised with the Web Audio API, so there are no files.

- **Glugs.** A pour is a train of bubble chirps, each a sine sweeping up about
  an octave in 45 ms. Their pitch is set by how full the target will be at that
  moment, so a vial audibly fills up, like a bottle under a tap. A soft
  low-passed hiss runs underneath.
- **Cork and chime.** Finishing a vial is a filtered-noise pop and a glass bell.
  The bell climbs a pentatonic scale with each vial you finish in a level, so the
  last few pours of a level play a rising tune.
- Pick-up tink, a dull bonk for an illegal pour, a sparkle when hidden paint is
  revealed, a reverse swoosh for undo, drums and a minor chord for the hard level
  intro, coin ticks and a bell arpeggio for the win.

## 7. Economy

| | Coins |
| --- | --- |
| Start | 120 |
| Normal / hard / super hard level | 10 / 30 / 60 |
| Finished without undo, hint or extra vial | +5 |
| Hint | 40 |
| Extra vial (max one per level) | 90 |
| 5 more undos (5 free per try) | 30 |

Starting inventory is 3 hints and 2 extra vials.

## 8. Risks and open questions

- **No human has played past level 10.** The curve is measured with bots. The
  bots agree with each other, but a round of real playtests on levels 5, 10, 15
  and 20 is the first thing to do.
- **The model's noise (β 1.8) and targets are first estimates.** They come from
  the bots. The analytics to refit them from real players (heat, outcome and
  the model's estimate on every attempt) are listed in the Unity plan.
- **Hidden paint isn't measured.** The simulated players see through the
  question marks, so hidden levels are harder for people than the table says.
  That's intended on the spikes, but it may make levels 13, 18 and 23 heavier
  than their place in the ramp.
- **Twelve colours on a phone.** Titanium White and Payne's Grey are close to the
  glass tints in light and dark mode respectively. They're separable with the
  gloss and outline, and the colour-symbol option exists for anyone who needs it,
  but they should be checked on real low-end screens.
- **The dead-end bar is a spoiler.** It tells the player something the genre
  normally makes them discover. It stays because a silent unwinnable board is
  the genre's most common complaint, but it's easy to make it opt-in.
