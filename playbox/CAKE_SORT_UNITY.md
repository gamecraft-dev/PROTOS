# Cake Sort in Unity: the game and its 3D slices

A self-contained brief for adding **Cake Sort** to the Playbox Unity project. The
project already has the shared systems from Part I of
`playbox/PLAYBOX_UNITY_PLAN.md`: save, settings, theme, synth and SFX, haptics,
sheets, toasts, fonts, the Hub and the skill model. It also has the other three
games. This file holds everything Cake-Sort-specific:

1. **§0**: what to build on, where the sources and assets are, and what changed
   since the plan.
2. **Part V of the plan, Cake Sort (§46–§56)**, copied word for word with two
   exceptions:
   - **§47** fixes the world axes for Unity.
   - **§51 is rewritten** for the ten 3D slices made in Blender. They replace
     the slice meshes, top patterns, toppings and piping that the plan had Unity
     generate.
3. **Cake Sort's parts of the plan's Part I and Part VI**, updated for the 3D
   slices: the director's settings, the Hub board, the folders, the tests, the
   milestones and the texture manifest.
4. **Appendix E**: the engine fixtures, copied as they are.

Section numbers follow the plan, so its cross-references still work. §46–§56 and
Appendix E are in this file. Any other number (§2, §3.1, §4.3, §4.8, §4.9,
§6.1, §7.3, §14.2, §18.1, §19.4, §19.5 and so on) is a shared system the
project already has; look it up in the full plan.

---

## 0. Before you start

### 0.1 Sources

| Source | What it is |
| --- | --- |
| `playbox/src/games/cake-sort.html` | The whole web game: engine (between the engine markers), cakes, sounds, the placement queue, every animation, lobby and sheets. **The reference for everything except how a slice looks.** |
| `playbox/art/cake-sort/` | **The ten 3D slices** (§51): one folder per cake with the game GLB, its textures, a README and the checks. Also available as the download `CakeSort_UnityAssets.zip`, ready to drop into the project (§51.1). |
| `playbox/tools/cake-probe.mjs`, `playbox/tools/adaptive-sim.mjs` | Run the web engine in Node: the difficulty table on the typical curve, and the adaptive simulation with the two bots. Use them to make extra fixtures. |
| `playbox/PLAYBOX_UNITY_PLAN.md` | The full plan (shared systems, the other games). |

All of these are in the repository `gamecraft-dev/PROTOS`, branch
`claude/paint-sort-game-thesam`.

**Where each part of the plan is in the web source** (plan §0.3):

| Plan section | HTML source |
| --- | --- |
| §48 Engine | Between the engine markers: `CAP` … `UNLOCK_AT`, `rngNext`, `seedFor`, `shuffle`, `RAMP`, `baseHeat`, `heatRange`, `spec`, `neighbours`, `countOf`, `kindsOf`, `isCake`, `takeSlices`, `addSlices`, `bestGather`, `resolve`, `makePlate`, `deal`, `newLevel`, `place`, `isWon`, `isStuck`, the bots and `probe` |
| §55 Cakes | `CAKES` (names, colours, notes). The slices themselves are now the 3D assets (§51); `drawSlice`, `drawPattern`, `drawPipe` and `drawTopping` are only the design they follow. |
| §51.8–51.10 Plates, stands, icons | `drawPlate`, `drawSlices`, `drawCloche`, `drawWholeCake`, `cakeIcon` |
| §49 Game flow | inside `mount`: `heatFor`, `observe`, `startLevel`, `restart`, `putDown`, `commit`, `enqueue`, `pump`, `stopPlayback`, `settle`, `undo`, `toggleHammer`, `smash`, `refresh`, `win`, `coach` |
| §50 Layout and input | `layout`, `buildBg`, `doily`, `emptyTarget`, `free`, `hitTray`, `hitCell`, the pointer listeners, `onKey` |
| §52 Animations | `vSlice`, `angleOf`, `reslot`, `settled`, `plateScale`, `playStep`, `flyerPose`, `serve`, `drawServed`, `arrive`, `step`, `crumbs`, `sparkle`, `shards`, `drawHand`, `unlock` |
| §53 Sound | `makeSfx` |
| §54 UI | `TEMPLATE`, the `<style>` block, `renderLobby`, `menuChips`, `renderGoal`, `showMsg`, `showStuck`, `menu`, `howTo`, `intro`, `win` |
| Board art (§0.6) | `drawCard` |

**Making extra fixtures** (plan §0.5): the part of `cake-sort.html` between the
engine markers is pure. Evaluate it in Node, add the skill block from
`shell.html` if needed, and call `spec`, `newLevel`, `place`, `resolve`,
`makePlate` or `playout`. That is how `cake-probe.mjs`, `adaptive-sim.mjs` and
Appendix E were made.

**Which one wins** (plan §0.2, for Cake Sort):
1. **This file** wins over the full plan, and both win over the web, for
   everything they specify: architecture, conversions, the C# code, the shader,
   the assets, the save format and the tests.
2. **For how a slice looks, the assets win.** First their renders, then the
   web's 2D drawing, which they follow.
3. **The HTML wins** for behaviour or look that nothing here pins down: an
   animation detail, a colour in an edge case, a string. Port what it does,
   converted to these conventions.
4. **For engine output, the HTML is ground truth.** Appendix E was produced by
   it. If the C# port disagrees with the HTML's output, match the HTML and report
   the difference.

### 0.2 What the project needs to have (all from Part I, already built)

- URP Universal Renderer (Forward), Linear colour space, HDR off, MSAA 4x,
  portrait, 60 fps. Canvas Scaler reference 390 × 844, match 0.5, so 1 canvas
  unit is 1 dp.
- Layers `CakeSort` (15) and `CakeFx` (16): add them if they are missing.
- Shared: `SaveService` (section `games["cake-sort"]`, §56.1), `SettingsService`,
  `ThemeService` + `ThemePalette.asset` (add the `cs-*` tokens of §54.1), the
  shared synth and compressor (§4.3; Cake Sort mixes like Paint Sort:
  `masterGain .7, compress: true`), `SfxPlayer`, `Haptics`, `Analytics` (events
  §56.3, each with `game = "cake-sort"`), `SheetHost`, `Toast`, the fonts
  `AppDisplay` and `AppBody`, Paint Sort's top-bar buttons, coin pill,
  booster-button style and float label, the hard intro (§19.4), the easings
  (§14.2), `GameScene`, `Navigator`, `IGameStatus`.
- The skill model `SkillModel` / `SkillConfig` / the director base (§4.9) and
  `AdaptiveSimCli`.
- Paint Sort's `Seeds.SeedFor` (the Cake Sort engine reuses it, §48.1).
- **A glTF importer**: `com.unity.cloud.gltfast` (glTFast). If the project has
  none, add it (§51.2).

### 0.3 Changes from the plan, in one place

1. **World axes (§47).** `+z` goes **away** from the viewer (screen up), not
   toward them. The plan's axes cannot exist in Unity: in a left-handed space, a
   camera looking toward −z has −x on its right unless it is mirrored. With `+z`
   away, a web angle is the same number as a Unity yaw (§47), which is what the
   slices need.
2. **Slices are ready-made 3D models (§51).** Ten GLBs from Blender. Each holds
   the layers, coat, drips, top pattern, piping and topping in one mesh with a
   baked texture. Gone from the plan:
   - `SliceMeshBuilder`
   - the `cs_pattern_*`, `cs_top_*`, `cs_pipe` and `cs_flame` textures
   - the topping and piping billboards
   - the screen-fixed glaze sheen
   - the edge lines in the shader
3. **`CakeSlice.shader` is new (§51.4).** It is lit, normal-mapped and draws an
   inverted-hull outline. It does its maths in **linear** space, like Blender,
   not in the sRGB the plan listed for it in §2.
4. **Toppings turn with their slice.** The web drew them upright only because it
   is 2D.
5. **The candle flame is in the Birthday mesh (§51.7).** It flickers in the
   vertex shader, not as a separate quad.
6. **The Hub board art uses the 3D slices (§0.6).** It used to be a 2D raster
   port of the slices.
7. The folders (§0.5), tests (§57), milestones (§58) and texture manifest (§59)
   below already include these changes.

### 0.4 Order of work

Follow the milestones in §58 below: CS1 (engine and tests, pure C#), CS2
(textures and sounds), CS3 (the 3D counter and the slices), CS4 (input, the step
queue, animations), CS5 (screens, level flow, save). Each row's checks pass
before the next starts.

### 0.5 Files (plan §3, Cake Sort lines, updated)

```
Assets/_Project/
├─ Scripts/CakeSort/
│  ├─ Engine/                              asmdef Playbox.CakeSort.Engine (noEngineReferences; refs Common)
│  │  ├─ CakeRng.cs, Cfg.cs                RNG with int state, constants, unlock levels (§48.1)
│  │  ├─ Difficulty.cs                     BaseHeat, HeatRange, SpecFor (§48.3)
│  │  ├─ Sort.cs                           neighbours, gathering, Resolve (§48.4)
│  │  ├─ Level.cs                          MakePlate, Deal, NewLevel, Place, IsWon, IsStuck (§48.5)
│  │  └─ Bots.cs, Probe.cs                 simulated players and the probe (§48.6)
│  ├─ Runtime/                             asmdef Playbox.CakeSort (refs Core, Common, Engine)
│  │  ├─ CakeSortController.cs             screens, level flow, boosters, win (§49)
│  │  ├─ CakeDirector.cs                   heat and skill readings (§4.9, §49.7)
│  │  ├─ StepQueue.cs                      the placement queue: Enqueue, Pump, Settle, StopPlayback (§49.4)
│  │  ├─ CakeLayout.cs, CakeInput.cs       §50
│  │  ├─ CakeLook.cs                       sets the slice shader's globals (§51.5)
│  │  ├─ PlateMeshBuilder.cs, ClocheBuilder.cs   §51.8
│  │  ├─ PlateView.cs, SliceView.cs, FlyerView.cs, ServedCake.cs      visual slices, turntable, flights, serving (§52)
│  │  ├─ SlicePool.cs                      pooled slice prefabs per cake (§51.3)
│  │  ├─ CakeFx.cs                         crumbs, stars, shards, floats on the CakeFx layer (§52.6)
│  │  ├─ CakeIconRig.cs                    cake icons for chips, lobby and sheets (§51.10)
│  │  ├─ CakeCardArtRig.cs                 the Hub board art (§0.6)
│  │  ├─ CakeSortSfx.cs, CakeSortHaptics.cs   §53
│  │  └─ CakeSortStatus.cs                 IGameStatus for the board (§56.1)
│  └─ UI/                                  asmdef Playbox.CakeSort.UI
│     ├─ CakeLobbyScreen.cs, CakePlayScreen.cs, OrderCard.cs, MenuChip.cs, MessageBar.cs   §54
│     └─ CakeSheets.cs                     new cake, pause, how to play, win, restart, booster buy (§54.4)
├─ Scripts/Editor/
│  ├─ Audio/CakeSortRecipes.cs             (§53.1)
│  ├─ Textures/CakeTextureRecipes.cs       cloth, doily, tray, cupcake, hand (§51.9, Appendix A)
│  ├─ Build/CakeSlicePrefabBuilder.cs      slice materials and prefabs from the GLBs (§51.3); run by Playbox/Build/Prefabs
│  └─ Probe/CakeProbeCli.cs                -executeMethod entry point (Cake Sort curve, §56.2)
├─ Art/CakeSort/<cake>/                    the ten slices, as delivered (§51.1)
├─ Shaders/CakeSlice.shader                §51.4
├─ Shaders/CakeGlass.shader                the cloche dome (§51.8)
├─ Materials/CakeSort/CakeSlice_<cake>.mat written by CakeSlicePrefabBuilder (one per cake: each has its own atlas)
├─ Prefabs/CakeSort/Slice_<cake>.prefab    written by CakeSlicePrefabBuilder
├─ Scenes/CakeSort.unity                   written by SceneBuilder (§3.1)
└─ Config/
   ├─ Games/CakeSort.asset                 GameDefinition (§0.6)
   ├─ Cakes.asset                          values from §55.1, plus each cake's slice prefab and ink (§51.3)
   └─ Difficulty/CakeSort.asset            SkillConfig, targets and ranges (§0.7)
```

Scene `CakeSort` (plan §3.1): `CakeRig` (pitched orthographic camera, counter,
tray, pools), `CakeFxRig` (overlay camera), `CakeIconRig`, UI canvas with
`CakeLobbyScreen` and `CakePlayScreen`, `SheetHost`, `Toast`, and
`CakeSortController` (§47). Back: the lobby's Back returns to the Hub
(`RequestExit()`); the Android back key does the same as the visible back button
on each screen and closes the top sheet first.

### 0.6 The Hub board (plan §5)

| Field | Cake Sort |
| --- | --- |
| `Id` | `cake-sort` |
| `Order` | 4 |
| `Title` | Cake Sort |
| `Tagline` | Slide plates together until every slice joins a whole cake. |
| `Soon` | false |
| `SceneName` | `CakeSort` |
| Status | `CakeSortStatus`: `level > 1 ? "Level L · K cakes" : "New · 10 cakes to discover"` |
| Cta | `level > 1 \|\| cur != null ? "Continue" : "Play"` |
| Art | `tex_board_cake_sort_light.png` / `_dark.png` (below) |
| Board colours (§6.1, light / dark) | b-accent `#F0568C` / `#FF7AA8`, b-deep `#B8305F` / `#B8456E`, b-soft `#FFE4EE` / `#3A1826`, b-text `#B8305F` / `#FF9EC0`, b-ink `#FFFFFF` / `#2A0614` |

**Board art.** 1600 × 1000, light and dark from the §54.1 tokens, with the
subject centred so envelope fit can crop it. It is a port of `drawCard` in
`cake-sort.html`:

- Background: a vertical gradient `cs-bg-a → cs-bg-b`.
- From 34% of the height down, a tablecloth: `cs-cloth` with `cs-check` gingham
  bands `max(8, W/22)` wide, and a 3 px rgba(0,0,0,.06) line at its top.
- Plate radius `pr = min(W/7.4, H/3.3)`. Plates and slices as in §51, at:
  - (17%, 62%): Lemon ×3 + Strawberry.
  - (50%, 74%): a whole Strawberry cake turned .25 rad.
  - (83%, 62%): Chocolate ×4 + Blueberry.
- A Lemon slice in mid-air at (32%, 30%) − .35R in x, start angle −2.2 rad,
  radius `1.08 R`. With it:
  - a dashed trail (2 on, 7 off, 2.5 px, `cs-accent` at α .45) curving up from
    the left plate;
  - a white α .7 motion arc.
- Three gold (#FFD45A) 8-point sparkles at (36%, 40%), (64%, 36%) and
  (57%, 26%), radius `.14 pr` × 1, .8 and .55.

**Changed:** the slices are the 3D prefabs (§51.3), so the art is no longer a
raster port. `CakeCardArtRig` renders it like Paint Sort's `CardArtRig`, on the
`CardArt` layer with the game camera's 42.84° pitch:
- the cloth and sparkles as quads;
- the plates and slices as in the game.

Use it either way:
- render it live into a RenderTexture (and again on theme change);
- or have the editor save it once per theme as the two PNGs above, so the Hub
  never loads the slices.

### 0.7 The director (plan §4.9, Cake Sort row)

`CakeDirector` owns Cake Sort's `SkillConfig`, its heat range and its readings:

| Game | Heat means | β | μ₀ | σ₀ | τ | Range for level n | Slot targets | A lost attempt | A won attempt, and q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cake Sort | §48.3 | 1 | 2.5 | 1.8 | .2 | `HeatRange(n)` (§48.3) | `Target[pos]` | the counter fills, or a restart after ≥ 5 plates | the order is filled: §49.7 |

β comes from the web's bots: the casual and the skilled bot win half their
levels at heat 4.3 and 7.3, with a spread of about 1. `AdaptiveSimCli -game
cake` must print these rows within ± .05 (the bots' random streams are the
web's):

| Player | Fixed curve (the old design) | Adaptive |
| --- | --- | --- |
| Cake Sort casual bot (real engine) | .85 / .46 / .29 | .88 / .58 / .33, settling at heat ≈ 3.2 |
| Cake Sort skilled bot (real engine) | 1.00 / 1.00 / .92 | .83 / .54 / .63, pushed to heat ≈ 6.2 |

The lobby's note says " Levels adjust to how you play." (§54.2). The save
section holds `skill` and `tries` (§56.1). An invalid or missing `skill` is
reset as §4.9 says.

---

# Part V: Cake Sort

## 46. Rules

Cake Sort is a placement puzzle on a 4 × 5 counter. Implement exactly:

- **Counter.** 20 cells, 4 columns × 5 rows, numbered row by row from the top
  left (`c = row × 4 + col`). Two cells are **neighbours** only when they share a
  side; corners never touch. Neighbour order is up, left, right, down, and it
  decides ties, so keep it.
- **Cake stands.** Some levels put glass cake stands on cells. A stand is never
  in the bottom row, never next to another stand, and nothing can go on it.
- **Plates and slices.** A plate holds up to **6 slices**. Each slice is one of
  ten cakes (§55). A plate keeps each cake's slices together in one run of slots.
- **Tray.** Three plates. New plates come only when all three are down.
- **Placing.** Drag a tray plate onto any empty cell (or tap a plate, then tap a
  cell). **Placing never waits for the sort:** the player can put a plate down
  while slices from the last one are still in the air (§49.4).
- **The sort.** When a plate lands (or changes), for each cake on it, among the
  plate and its neighbours holding that cake, the plate that can end up holding
  the most of it becomes the gathering point, and that cake's slices on the
  plates next to it fly over, smallest groups first, as far as there is room. A
  transfer happens only if it leaves more slices together than any giving plate
  had, so the sort always settles. Every plate a transfer touches is checked
  again, so sorting chains across the counter (§48.4).
- **Cakes.** Six slices of one cake on one plate make a **whole cake**: it spins,
  flies to the order card at the top and counts toward the order. A plate left
  empty is cleared away.
- **Win** when the number of cakes baked reaches the order (`goal`).
- **Full counter.** When a tray plate is waiting and no cell is empty, the level
  is stuck: a bar offers the hammer, undo and restart.
- **Boosters.** Undo (takes back the last plate with everything it caused; 3 per
  try, then 30 coins each), Hammer (clears one plate off the counter; 2 to start,
  60 coins), New plates (swaps the plates still in the tray; 2 to start, 40
  coins). Hammer only works when nothing is sorting.
- **Coins.** Start with 100. A level pays 10 (hard 30, super hard 60), plus 5 if
  no booster was used.
- **Cakes on the menu.** Each level uses a few of the cakes unlocked so far; a
  cake joins the menu at the level in §55 and is shown off on a turntable the
  first time it appears.
- **Levels** are made on the device when they start, at a difficulty the
  adaptive model picks for this player (§4.9, §48.3). In every block of ten the
  5th level is **hard** and the 10th **super hard**: they aim at a lower win rate
  and always have one and two cake stands.
- **Level 1** is a fixed tutorial: three strawberry slices on the counter, three
  more in the tray, so the first drop bakes a cake.
- **Progress** (level, coins, boosters, the level in progress, the cake
  collection, the skill estimate) saves after every plate.

---

## 47. Units, camera and scene

**Screen first, then 3D.** Every position in this part is computed in screen dp
exactly as the web computes it (§50), then turned into a point on the counter.
That keeps every web formula usable as written while the cakes are real 3D
meshes that light, sort and spin correctly.

- **World.** The counter is the plane `y = 0`; `+x` is screen right; `+z` goes
  **away from the viewer (screen up)**. 1 world unit = 1 dp. *(Changed from the
  plan, which had `+z` toward the viewer. With `+x` on the right, that needs a
  mirrored camera in Unity's left-handed space.)*
- **Camera.** Orthographic, `transform.rotation = Quaternion.Euler(α, 0, 0)`
  with `α = asin(0.68) = 42.8436°`: it looks down and toward +z, with +x on its
  right. A circle on the counter then shows as an ellipse squashed to 0.68,
  exactly the web's `SQ`, and a height `y` shows as `y × cos α = 0.73268 y` on
  screen.
- **Conversion.** A web screen point `(sx, sy)` on the counter at web height `hz`
  (dp drawn upward) is the world point `(sx − W/2, hz / cos α, (Yref − sy) / SQ)`
  plus the camera offset that puts `Yref` at the screen's vertical centre. Every
  web "height" (cake height, plate thickness, lift, dome height) is divided by
  `cos α` when built in 3D, so it shows on screen at the web's size. The slice
  models already are (§51.2): scale them uniformly.
- **Angles.** A web angle `a` turns clockwise on screen, because screen y points
  down. It is the counter direction `(cos a, 0, −sin a)`, which is exactly
  Unity's yaw: `Quaternion.Euler(0, a·Rad2Deg, 0) * Vector3.right`. So slot
  angles, spins and `rot` (§52) are used as yaws in degrees, unchanged, and a
  web screen offset `(dx, dy)` on the counter is the world offset
  `(dx, 0, −dy / SQ)`.
- **Orthographic size** = screen height in dp / 2 (so 1 unit = 1 dp on screen
  for x; z is foreshortened by SQ as on the web).
- **Depth.** Cakes, plates and stands are opaque meshes with depth write, so
  overlaps sort themselves (the web painter's order is not needed). Glass,
  shadows, doilies and particles are transparent and drawn after, sorted by
  distance.
- **Layers.** `CakeSort` (15) for the counter; `CakeFx` (16) for cakes being
  served, sparkles and the tutorial hand, drawn by an overlay camera (URP camera
  stack) **after** the HUD, because a served cake flies on top of the order card.
  The HUD canvas is *Screen Space – Camera* on the base camera.
- **Scene `CakeSort`** (built by `SceneBuilder`): `CakeRig` (base camera,
  counter root, tray root, slice pool, particle pool), `CakeFxRig` (overlay
  camera), UI canvas with `CakeLobbyScreen` and `CakePlayScreen`, `SheetHost`,
  `Toast`, and `CakeSortController` (§49).

---

## 48. Engine (pure C#, full source)

Namespace `Playbox.CakeSort.Engine`, assembly `Playbox.CakeSort.Engine`
(`noEngineReferences: true`, refs `Playbox.Common`). It must reproduce the web
engine (`playbox/src/games/cake-sort.html`, between the engine markers) exactly;
Appendix E has the fixtures.

### 48.1 `CakeRng.cs`, `Seeds` and constants

```csharp
namespace Playbox.CakeSort.Engine
{
    /// Mulberry32 with its state as a plain int, like the web's rngNext({ s }).
    /// The state is saved with a level in progress and in every undo snapshot.
    public sealed class CakeRng
    {
        public int S;
        public CakeRng(int s) { S = s; }
        public double Next()
        {
            unchecked
            {
                S = S + 0x6D2B79F5;
                uint s = (uint)S;
                uint t = (s ^ (s >> 15)) * (1u | s);
                t = (t + ((t ^ (t >> 7)) * (61u | t))) ^ t;
                return (t ^ (t >> 14)) / 4294967296.0;
            }
        }
        public CakeRng Clone() => new CakeRng(S);
    }

    public static class Cfg
    {
        public const int Cap = 6, Cols = 4, Rows = 5, Cells = 20, Tray = 3;
        public const int Stand = -1;                     // a cell value: a cake stand (null = empty, list = plate)
        public static readonly int[] UnlockAt = { 1, 1, 1, 3, 5, 8, 12, 16, 21, 27 };   // level each cake joins the menu
        public static readonly double[] Ramp = { 0, .4, .8, 1.2, 2.4, .5, .9, 1.3, 1.7, 3.4 };
        public const double BlockStep = .6, HeatMax = 10, StandWorth = .5;
        public const int BaseBlocks = 8;
        /// Port of seedFor(n, salt) (same as Paint Sort's Seeds.SeedFor).
        public static uint SeedFor(int n, int salt) => Playbox.PaintSort.Engine.Seeds.SeedFor(n, salt);
        public static int JsRound(double x) => (int)System.Math.Floor(x + 0.5);
    }
}
```

(If the Cake Sort engine must not reference Paint Sort's assembly, copy
`SeedFor` into `Cfg`; it is eight lines.)

### 48.2 Cells

A counter is `List<int>[] cells` of length 20: `null` is empty, a list is a plate
(bottom slot first), and the stand marker is kept in a separate `bool[] stand`
mirror **or** as a shared static list instance `StandCell` that every engine
function tests by reference. The web uses `-1` in the same array; pick one
representation and keep it everywhere. This plan uses `object[]` mirroring the
web exactly:

```csharp
// cells[c] is null (empty), the boxed int -1 (stand), or a List<int> (plate)
static bool IsPlate(object v) => v is List<int>;
static bool IsStand(object v) => v is int i && i == Cfg.Stand;
```

### 48.3 `Difficulty.cs`

```csharp
using System;

namespace Playbox.CakeSort.Engine
{
    public sealed class Spec
    {
        public int N, Block, Pos, Tier, Pool, Blocked, K, Goal, Pre, Reward;
        public double Heat, Mix, Mix3, Help, Big;
    }

    public static class Difficulty
    {
        static int BlockOf(int n) => Math.Min(Cfg.BaseBlocks, (Math.Max(1, n) - 1) / 10);

        /// The sawtooth a typical new player starts on; also the heat when no model is given.
        public static double BaseHeat(int n) { n = Math.Max(1, n); return BlockOf(n) * Cfg.BlockStep + Cfg.Ramp[(n - 1) % 10]; }

        /// How far the model may move level n: never below 2.5 under the start of its
        /// block of ten, never above 4 over the block's hardest level.
        public static (double Lo, double Hi) HeatRange(int n)
        {
            double start = BlockOf(n) * Cfg.BlockStep;
            return (Math.Max(0, start - 2.5), Math.Min(Cfg.HeatMax, start + Cfg.Ramp[9] + 4));
        }

        /// Every knob follows the heat h. Cake stands come with heat; a hard level
        /// always has one and a super-hard level two. Each stand spends StandWorth
        /// of the heat and the rest drives the other knobs.
        public static Spec SpecFor(int n, double? h = null)
        {
            n = Math.Max(1, n);
            int block = (n - 1) / 10, pos = (n - 1) % 10;
            int tier = pos == 9 ? 2 : pos == 4 ? 1 : 0;
            double heat = Math.Min(Cfg.HeatMax, Math.Max(0, h ?? BaseHeat(n)));
            int pool = 0; foreach (var u in Cfg.UnlockAt) if (u <= n) pool++;
            int blocked = n < 4 ? 0 : Math.Min(4, Math.Max(tier, heat >= 3.5 ? 1 + (int)Math.Floor((heat - 3.5) / 2) : 0));
            double k = Math.Max(0, heat - blocked * Cfg.StandWorth);
            return new Spec
            {
                N = n, Block = block, Pos = pos, Tier = tier, Heat = heat, Pool = pool, Blocked = blocked,
                K = n == 1 ? 3 : Math.Max(3, Math.Min(Math.Min(pool, 8), Cfg.JsRound(3.2 + k * .5))),
                Goal = n == 1 ? 3 : Math.Max(5, Math.Min(26, Cfg.JsRound(6 + k * 2.2))),
                Pre = n < 3 ? 0 : Math.Min(6, 2 + (int)Math.Floor(k * .8)),
                Mix = Math.Min(.7, .28 + k * .07),               // chance a plate holds a second cake
                Mix3 = Math.Min(.3, Math.Max(0, k - 1.5) * .07),  // and a third
                Help = Math.Max(.3, .64 - k * .06),               // chance a new plate's cake is one already out
                Big = Math.Min(.5, .12 + k * .05),                // chance of a 4- or 5-slice plate
                Reward = tier == 2 ? 60 : tier == 1 ? 30 : 10
            };
        }
    }
}
```

### 48.4 `Sort.cs` (the rules)

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

namespace Playbox.CakeSort.Engine
{
    public sealed class Step
    {
        public int D, F;                       // gathering plate, cake
        public List<(int Cell, int Slices)> From = new();
        public bool Cake;                      // D became a whole cake and was served (D is now empty)
        public List<int> Emptied = new();      // giving plates left empty (now empty cells)
    }

    public static class Sort
    {
        public static bool IsPlate(object v) => v is List<int>;
        public static bool IsStand(object v) => v is int i && i == Cfg.Stand;

        /// Up, left, right, down: the order decides ties.
        public static List<int> Neighbours(int c)
        {
            int x = c % Cfg.Cols, y = c / Cfg.Cols; var o = new List<int>(4);
            if (y > 0) o.Add(c - Cfg.Cols);
            if (x > 0) o.Add(c - 1);
            if (x < Cfg.Cols - 1) o.Add(c + 1);
            if (y < Cfg.Rows - 1) o.Add(c + Cfg.Cols);
            return o;
        }
        public static int CountOf(List<int> p, int f) { int k = 0; foreach (var x in p) if (x == f) k++; return k; }
        /// Distinct cakes in order of first appearance.
        public static List<int> KindsOf(List<int> p) { var o = new List<int>(); foreach (var x in p) if (!o.Contains(x)) o.Add(x); return o; }
        public static bool IsCake(List<int> p) => p.Count == Cfg.Cap && p.All(x => x == p[0]);

        /// Slices leave from the end of their run and arrive after it.
        public static void TakeSlices(List<int> p, int f, int k)
        {
            for (int i = p.Count - 1; i >= 0 && k > 0; i--) if (p[i] == f) { p.RemoveAt(i); k--; }
        }
        public static void AddSlices(List<int> p, int f, int k)
        {
            int at = p.LastIndexOf(f);
            var ins = Enumerable.Repeat(f, k);
            if (at < 0) p.AddRange(ins); else p.InsertRange(at + 1, ins);
        }

        sealed class Gather { public int[] Key; public int F, D; public List<(int, int)> From; }

        static int Cmp(int[] a, int[] b) { for (int i = 0; i < a.Length; i++) if (a[i] != b[i]) return a[i] - b[i]; return 0; }

        static Gather BestGather(object[] cells, int c)
        {
            var p = (List<int>)cells[c];
            Gather best = null;
            foreach (int f in KindsOf(p))
            {
                var cands = new List<int> { c };
                foreach (int n in Neighbours(c)) if (cells[n] is List<int> q && q.Contains(f)) cands.Add(n);
                if (cands.Count < 2) continue;
                foreach (int d in cands)
                {
                    var pd = (List<int>)cells[d];
                    int cd = CountOf(pd, f), room = Cfg.Cap - pd.Count;
                    if (room <= 0) continue;
                    var srcs = new List<(int N, int K)>();
                    foreach (int n in Neighbours(d))
                        if (cells[n] is List<int> q && !IsCake(q)) { int k = CountOf(q, f); if (k > 0) srcs.Add((n, k)); }
                    srcs = srcs.OrderBy(s => s.K).ThenBy(s => s.N).ToList();   // stable, like the web's sort
                    List<(int, int)> from; int final;
                    for (;;)
                    {
                        from = new List<(int, int)>(); int left = room;
                        foreach (var (n, k) in srcs) { if (left == 0) break; int take = Math.Min(k, left); from.Add((n, take)); left -= take; }
                        final = cd + room - left;
                        int fin = final;
                        var keep = srcs.Where(s => s.K < fin).ToList();
                        if (keep.Count == srcs.Count) break;
                        srcs = keep;
                    }
                    if (from.Count == 0) continue;
                    int others = pd.Count - cd;
                    bool cake = final == Cfg.Cap && others == 0;
                    int moved = final - cd;
                    // completes a cake > most slices together > fewest other cakes > fewest slices flown > the plate that changed
                    var key = new[] { cake ? 1 : 0, final, -others, -moved, d == c ? 1 : 0 };
                    if (best == null || Cmp(key, best.Key) > 0) best = new Gather { Key = key, F = f, D = d, From = from };
                }
            }
            return best;
        }

        /// Settles the counter after the plate at `start` changed. Mutates `cells`
        /// and returns the steps in playing order.
        public static List<Step> Resolve(object[] cells, int start)
        {
            var steps = new List<Step>(); var queue = new List<int> { start }; int guard = 0;
            while (queue.Count > 0 && guard < 400)
            {
                int c = queue[0]; queue.RemoveAt(0);
                for (;;)
                {
                    if (++guard > 400) break;
                    if (!(cells[c] is List<int> pc) || IsCake(pc)) break;
                    var g = BestGather(cells, c);
                    if (g == null) break;
                    var touched = new List<int> { g.D };
                    foreach (var (n, k) in g.From) { TakeSlices((List<int>)cells[n], g.F, k); AddSlices((List<int>)cells[g.D], g.F, k); touched.Add(n); }
                    var step = new Step { D = g.D, F = g.F };
                    foreach (var (n, k) in g.From) step.From.Add((n, k));
                    foreach (var (n, _) in g.From) if (((List<int>)cells[n]).Count == 0) { cells[n] = null; step.Emptied.Add(n); }
                    if (IsCake((List<int>)cells[g.D])) { step.Cake = true; cells[g.D] = null; }
                    steps.Add(step);
                    foreach (int t in touched) if (t != c && cells[t] is List<int> && !queue.Contains(t)) queue.Add(t);
                    if (!(cells[c] is List<int>)) break;
                }
            }
            return steps;
        }
    }
}
```

### 48.5 `Level.cs` (dealing, new level, placing)

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

namespace Playbox.CakeSort.Engine
{
    public sealed class Level
    {
        public int N; public Spec Sp; public List<int> Flv;     // cakes on the menu, ascending
        public object[] Cells = new object[Cfg.Cells];
        public List<int>[] Tray = new List<int>[Cfg.Tray];
        public CakeRng Rs; public int Baked, Moves;
        public Dictionary<int, int> BakedBy = new();
    }

    public sealed class PlaceResult { public List<Step> Steps; public bool Dealt; }

    public static class Levels
    {
        public static List<int> MakePlate(object[] cells, Spec sp, List<int> flv, CakeRng rs)
        {
            double R() => rs.Next();
            int n; double u = R();
            if (u < sp.Big) n = R() < .7 ? 4 : 5;
            else n = u < sp.Big + (1 - sp.Big) * .22 ? 1 : u < sp.Big + (1 - sp.Big) * .62 ? 2 : 3;
            int kinds = 1;
            if (n >= 2 && R() < sp.Mix) kinds = 2;
            if (n >= 3 && kinds == 2 && R() < sp.Mix3) kinds = 3;
            // what's already out, weighted by slice count, in order of first appearance (the web's Map)
            var outF = new List<int>(); var outK = new List<int>();
            foreach (var v in cells) if (v is List<int> p) foreach (int f in p)
            { int i = outF.IndexOf(f); if (i < 0) { outF.Add(f); outK.Add(1); } else outK[i]++; }
            var chosen = new List<int>();
            while (chosen.Count < kinds)
            {
                int f = -1;
                if (outF.Count > 0 && R() < sp.Help)             // no draw when nothing is out
                {
                    int tot = 0; for (int i = 0; i < outF.Count; i++) if (!chosen.Contains(outF[i])) tot += outK[i];
                    double x = R() * tot;
                    for (int i = 0; i < outF.Count; i++) { if (chosen.Contains(outF[i])) continue; x -= outK[i]; if (x < 0) { f = outF[i]; break; } }
                }
                if (f < 0) { var left = flv.Where(g => !chosen.Contains(g)).ToList(); f = left[(int)(R() * left.Count)]; }
                chosen.Add(f);
            }
            var counts = chosen.Select(_ => 1).ToArray();
            for (int k = kinds; k < n; k++) counts[(int)(R() * kinds)]++;
            var plate = new List<int>();
            for (int i = 0; i < chosen.Count; i++) for (int k = 0; k < counts[i]; k++) plate.Add(chosen[i]);
            return plate;
        }

        public static bool Deal(Level L)
        {
            if (L.Tray.Any(p => p != null)) return false;
            for (int t = 0; t < Cfg.Tray; t++) L.Tray[t] = MakePlate(L.Cells, L.Sp, L.Flv, L.Rs);
            return true;
        }

        /// Level n at heat h: the menu, the stands, the plates already out and the
        /// first tray. Deterministic per (n, heat).
        public static Level NewLevel(int n, double? h = null)
        {
            var sp = Difficulty.SpecFor(n, h);
            var rs = new CakeRng(unchecked((int)Cfg.SeedFor(n, 11 + Cfg.JsRound(sp.Heat * 20))));
            var pool = new List<int>(); for (int f = 0; f < Cfg.UnlockAt.Length; f++) if (Cfg.UnlockAt[f] <= n) pool.Add(f);
            var newest = pool.Where(f => Cfg.UnlockAt[f] == n && n > 1).ToList();
            var rest = pool.Where(f => !newest.Contains(f)).ToList();
            for (int i = rest.Count - 1; i > 0; i--) { int j = (int)(rs.Next() * (i + 1)); (rest[i], rest[j]) = (rest[j], rest[i]); }
            var flv = newest.Concat(rest).Take(sp.K).OrderBy(f => f).ToList();
            var cells = new object[Cfg.Cells];
            int tries = 0, placed = 0;
            while (placed < sp.Blocked && tries++ < 200)                       // stands: never the bottom row, never side by side
            {
                int c = (int)(rs.Next() * (Cfg.Cells - Cfg.Cols));
                if (cells[c] != null || Sort.Neighbours(c).Any(m => Sort.IsStand(cells[m]))) continue;
                cells[c] = Cfg.Stand; placed++;
            }
            var pre = new Spec { Mix = sp.Mix, Mix3 = sp.Mix3, Help = 0, Big = Math.Min(.3, sp.Big) };
            tries = 0; placed = 0;
            while (placed < sp.Pre && tries++ < 300)                           // plates already out, none touching a shared cake
            {
                int c = (int)(rs.Next() * Cfg.Cells);
                if (cells[c] != null) continue;
                var p = MakePlate(cells, pre, flv, rs);
                if (Sort.Neighbours(c).Any(m => cells[m] is List<int> q && q.Any(f => p.Contains(f)))) continue;
                cells[c] = p; placed++;
            }
            var L = new Level { N = n, Sp = sp, Flv = flv, Cells = cells, Rs = rs };
            if (n == 1)
            {
                cells[9] = new List<int> { 0, 0, 0 }; cells[14] = new List<int> { 1, 1, 1, 1 };
                L.Tray = new[] { new List<int> { 0, 0, 0 }, new List<int> { 2, 2, 1 }, new List<int> { 2, 2 } };
                return L;
            }
            Deal(L);
            return L;
        }

        public static PlaceResult Place(Level L, int t, int c)
        {
            if (L.Tray[t] == null || L.Cells[c] != null) return null;
            L.Cells[c] = L.Tray[t]; L.Tray[t] = null; L.Moves++;
            var steps = Sort.Resolve(L.Cells, c);
            foreach (var s in steps) if (s.Cake) { L.Baked++; L.BakedBy[s.F] = (L.BakedBy.TryGetValue(s.F, out var k) ? k : 0) + 1; }
            bool dealt = Deal(L);
            return new PlaceResult { Steps = steps, Dealt = dealt };
        }

        public static bool IsWon(Level L) => L.Baked >= L.Sp.Goal;
        public static bool IsStuck(Level L) => !IsWon(L) && L.Tray.Any(p => p != null) && !L.Cells.Contains(null);
    }
}
```

Note the `pre` spec: the web copies the whole spec and overrides `help` and
`big`; only `Mix`, `Mix3`, `Help` and `Big` are read by `MakePlate`, so the copy
above is equivalent. `MakePlate` draws `R()` for the help test only when
something is out, and that draw still happens when `Help` is 0.

### 48.6 `Bots.cs` and `Probe.cs` (tests, the probe CLI and the adaptive simulation)

Port `cloneLevel`, `boardScore`, `candidates`, `botMove`, `playout` and `probe`
from the web as written (they are short). Their exact behaviour:

- `BoardScore(cells)`: +16 per empty cell; per plate −14 × (kinds − 1) +
  1.4 × count² per cake; +3 per neighbouring pair (counted once, `n > c`) that
  shares a cake.
- `BotMove(L, skill, rand)`: candidates are every (tray slot, empty cell) in tray
  order then cell order. **Skilled** (`skill ≥ 1`): for each, clone, place,
  resolve; score `120 × cakes + BoardScore + 6 × rand()`; best wins (first on
  ties). **Casual**: the candidates whose cell has a neighbour sharing a cake with
  that tray plate; with chance .85 pick uniformly among them, else uniformly
  among all.
- `Playout(n, skill, seed, h)`: `NewLevel(n, h)`, then `L.Rs.S ^= seed` (int32
  xor), `rand = new CakeRng(seed)`; up to 600 placements; return `Moves` on a
  win, −1 when no move is left or the cap is reached.
- `Probe(from, to, runs)`: per level, `runs` casual playouts with seeds
  `SeedFor(n, 500 + i)` and skilled with `SeedFor(n, 900 + i)` (cast to int);
  rows `N, Tier, K, Goal, Blocked, Heat, Casual, Skilled, Fail = mean, Plates`.

### 48.7 Parity rules

Everything in §10.10 applies, plus:

| JavaScript | C# |
| --- | --- |
| `x \| 0` on a non-negative double (indices from `r() * n`) | `(int)x` (truncation) |
| `seedFor(...) \| 0` | `unchecked((int)SeedFor(...))` |
| `Math.round` | `Cfg.JsRound` |
| `arr.sort((a, b) => a[1] - b[1] \|\| a[0] - b[0])` | `OrderBy(K).ThenBy(N)` (stable) |
| `new Map()` iteration | insertion-ordered parallel lists (§48.5) |
| `queue.shift()` / `includes` | `List<int>` with `RemoveAt(0)` / `Contains` (the queue is tiny) |

---

## 49. Level state, the placement queue and game flow

### 49.1 State (`CakeLevelState`, saved as `cur`, §56.1)

`N`, `H` (the heat this attempt was made at), `Flv`, `Cells`, `Tray`, `Rs` (int),
`Baked`, `BakedBy`, `Moves`, `Undos` (left this try), `Clean` (no booster used),
`MinFree` (fewest empty cells seen this attempt, starts at 20), `Observed` (this
attempt has already been read by the skill model), plus the runtime-only `Won`.
Undo snapshots hold `Cells`, `Tray`, `Rs`, `Baked`, `BakedBy`, `Moves` (deep
copies), at most 12.

### 49.2 Starting a level (`StartLevel(n, fresh)`)

1. Close sheets; clear the drag, selection, hammer mode, combo, the undo stack
   and every animation (`StopPlayback`, §49.4); remove floats; hide the bar.
2. Resume when `!fresh && cur != null && cur.N == n`; otherwise
   `h = Director.HeatFor(n)` (§4.9) and `NewLevel(n, h)` with `Undos = 3`,
   `Clean = true`, `MinFree = 20`, `Observed = false`.
3. Tutorial on when `n == 1` and not resumed (the coach line is shown only on
   that level, at a fixed height, so the counter never moves).
4. Show the play screen; tier backdrop; menu chips with baked counts; HUD.
5. Next frame: layout (§50), build visuals from the state with a pop-in
   (plates `born` at now + random 0–120 ms, tray at now + 70 ms × slot), save.
6. Hard or super hard and not resumed: the hard intro (§52.7), then the new-cake
   sheet if any; otherwise the new-cake sheet if any cake on the menu has not
   been seen (`seen[f]`); level 1 marks its three cakes seen silently.
7. If the resumed state is stuck, show the full-counter bar.

### 49.3 Placing (`PutDown(t, c, from, lift)`, `Commit(t, c)`)

```
Free(c) = state.Cells[c] == null && (visual plate at c is absent or dying) && no mover is headed to c
PutDown(t, c): ignore if busy (won), tray t empty or already in flight, or !Free(c)
    selection = none; drop sound; mover {t, c, from, to = cell centre, lift, 150 ms, easeOutCubic} → Commit
Commit(t, c):
    push undo snapshot (cap 12)
    the tray plate's visual becomes the cell's plate (born = now − 200: a small squash on landing)
    place sound, haptic 8
    res = Levels.Place(state, t, c)
    MinFree = min(MinFree, empty cells now)
    for each cake step: stats.cakes++, baked[f]++
    tutorial step 1 → 2
    if res.Dealt: the three new tray visuals pop in at now + 160 + 80 × slot, deal sound at +160 ms
    if IsWon(state): busy = true          // the order is filled: no more plates
    save; Enqueue(res.Steps)
```

### 49.4 The step queue (input never waits)

The engine settles a placement at once, so the board state is always final; the
picture catches up through one queue shared by every placement. A placement's
steps always come after every earlier placement's steps, so playing them
strictly in order keeps the visuals consistent with the board however fast
plates go down.

```
queue = [], playing = false, gen = 0
Enqueue(steps): queue.AddRange(steps); Pump()
Pump(): if playing: return
        if queue empty: Settle(); return
        playing = true; g0 = gen; wait = PlayStep(queue.Dequeue())
        after wait ms: if gen == g0: playing = false; Pump()
Sorting = playing || queue not empty
StopPlayback(): gen++; queue.Clear(); playing = false; flyers, served cakes and movers cleared
```

`PlayStep` is §52.3. `Settle()` runs when the queue runs dry:
1. combo = 0.
2. Compare each cell's visual plate (ignoring dying ones) with the state; rebuild
   any that differ and log a warning (never happens in normal play; it guards
   against bugs).
3. Won: `busy = true`; open the win sheet after 1250 ms if a cake is still
   flying to the order card, else after 250 ms.
4. Stuck: read a lost try (§49.7); show the full-counter bar unless a mover is in
   flight. Otherwise hide the bar (unless in hammer mode).
5. Tutorial: step 2 and a cake baked → step 3.

### 49.5 Boosters

| Booster | Rule |
| --- | --- |
| Undo | Not while won or while a mover is in flight. Needs a snapshot ("Nothing to undo" toast and bonk otherwise). Uses one of the 3 free undos of this try, then offers to buy one for 30. Restores the snapshot, `StopPlayback`, rebuilds visuals (tray pops in), shown counts = state, undo sound, `Clean = false`. |
| Hammer | Not while won, sorting or a mover is in flight ("Wait for the slices to settle" toast). Needs a plate on the counter. With none left, offers one for 60. Hammer mode: plates pulse; the bar reads "Tap a plate to clear it off the counter" with Cancel; the booster button shows accent. Tapping a plate: remove it from the state, `hammer−−`, `Clean = false`, clear the undo stack, shards (§52.6), the plate dies at once, smash sound, haptic [30,30,50], leave hammer mode. |
| New plates | Not while won or a mover is in flight. With none left, offers one for 40. Replaces every tray plate still there with `MakePlate(cells, spec, menu, Rs)` in slot order, pops them in (80 ms stagger), refresh sound, `Clean = false`, clears the undo stack. |

The buy sheet: eyebrow "Booster", title "Another undo?" / "Buy a hammer?" / "Buy
new plates?", sub "{price} coins. You have {coins}.", actions "Buy for {price}"
and "Not now". Not enough coins: toast "Not enough coins ({price} needed)" and
bonk.

### 49.6 Restart, win and economy

- **Restart** (pause menu, full-counter bar): with no plates placed it restarts
  at once; otherwise a sheet "Start this level again?" / "The counter is cleared
  and you get a fresh set of plates." with "Restart" and "Keep playing". Giving up
  after 5 or more plates is a lost try (§49.7). The new attempt is made at the
  model's new heat.
- **Win** (`Win()`, once): `Won = true`; shown counts = state; read the win
  (§49.7); coins += reward + (Clean ? 5 : 0); `level = max(level, n + 1)`;
  `cur = null`; stats (won, hard, super); flush the save; win sound, haptic
  [20,40,20,40,60]; after 350 ms the win sheet (§54.4) with a coin count-up (step
  `max(1, round(total/12))` every 55 ms, coin sound per step).

| Constant | Value |
| --- | --- |
| Starting coins | 100 |
| Starting inventory | 2 hammers, 2 new plates |
| Undos per try | 3 |
| Reward normal / hard / super hard | 10 / 30 / 60 |
| Bonus for no booster | +5 |
| Prices: undo / hammer / new plates | 30 / 60 / 40 |
| Undo history cap | 12 |

### 49.7 Skill readings (`CakeDirector`, §4.9)

One reading per attempt (`Observed` guards it):
- **Lost:** the counter fills (read when the queue settles on a stuck state),
  or a restart after 5 or more plates.
- **Won:** at the win, then a quality reading
  `q = Φ((MinFree / (20 − stands) − 0.12 − (Clean ? 0 : 0.1)) / 0.3)`: bots that
  win half the time keep about 12% of the counter free at the tightest moment,
  easy wins about half of it.
- A win resets `tries`; a loss increments `tries.fails` for this level, which
  eases the next attempt's target (mercy).

### 49.8 Tutorial (level 1)

| Step | Coach line | Pointer |
| --- | --- | --- |
| 1 | "Drag the strawberry plate next to the other strawberries." | a hand from tray slot 0 to cell 10, 1.8 s loop: position eased (easeInOutCubic of min(1, 1.4u)), fading out over the last 15% |
| 2 (after the first plate) | "Six slices of one cake make a whole cake." | none |
| 3 (after the first cake) | "Mixed plates sort themselves when they touch. Bake 3 cakes!" | none; cleared after 6 s |

The hand: a white glove outline (the web's `drawHand` path), 0.32 cw tall,
rotated −0.35 rad, surface fill and 2.2 dp ink stroke, 0.2 cw below the target.

---

## 50. Board layout and input

### 50.1 Layout (`CakeLayout`, port of `layout`)

Measure the field rect (between the coach line or order card and the booster
row) in dp: `fx, fy, fw, fh`; the full play view is `W × H`.

```
RP = .8, TOP = .42, MID = .14, TRAY_H = 1.25
cw    = max(36, min((fw − 36)/4, fh/(TOP + 5·RP + MID + TRAY_H), 116))     // cell width
rp    = cw · RP                                                             // row pitch on screen
used  = cw · (TOP + 5·RP + MID + TRAY_H)
bx    = fx + (fw − 4cw)/2
by    = fy + max(0, (fh − used)/2) + cw·TOP
pr    = .44 cw                       // plate radius; cake radius R = .8 pr; cake height = .52 R
cell centre (c): x = bx + (c mod 4 + .5)·cw,  y = by + (floor(c/4) + .5)·rp
trayY = by + 5·rp + MID·cw + .58 cw
gap   = min(1.3 cw, (W − 24)/3);  tray x = W/2 − gap, W/2, W/2 + gap
```

Static pieces (rebuilt on layout and theme change):
- **Tablecloth**: rounded rect (radius 18) from `(bx − .14cw, by − .5rp − .06cw)`
  size `(4cw + .28cw, 5rp + .2cw)`, `cs-cloth` fill, gingham of `cs-check`
  (stripes `max(10, cw/5)` wide every other band, both directions), 2 dp
  `cs-cloth-edge` outline, a shadow (`cs-shadow`) offset (2, 6).
- **Doilies** on every non-stand cell: radius `1.06 pr`, 18 scallops of radius
  `.11 × 1.06 pr` around `.93 × 1.06 pr`, `cs-mat` fill; a dashed ring (2 on, 3
  off, 1.2 dp, `cs-mat-edge`) at `.78 ×`. Lying on the counter, so the camera
  squashes them to 0.68 like the web.
- **Tray board**: width `min(W − 16, gap·2 + 1.2cw)`, height `1.02cw`, radius 22,
  vertical gradient `cs-wood → cs-wood-2`, 4 grain curves (rgba(0,0,0,.08),
  1.4 dp), a 2 dp rgba(255,255,255,.35) inner edge, shadow offset (2, 6); under
  each slot a spot: ellipse `1.04 pr`, rgba(0,0,0,.05), and a dashed ring
  (4 on, 5 off, 1.5 dp, white α .4) at `.98 pr`.

The web draws all of that into one canvas; in Unity the cloth, doilies and tray
are textured quads on the counter plane (§51.9).

### 50.2 Input (`CakeInput`)

All hit tests are in screen dp.

- **Tray hit:** the nearest tray slot (with a plate, not in flight) whose
  distance `hypot(tx − x, (trayY − y)/.85) < 1.35 pr`.
- **Cell hit** (`HitCell`): the cell with `|x − cx| ≤ cw/2` and
  `|y − cy + .2pr| ≤ rp/2`.
- **Pointer down** (not on HUD): in hammer mode, a plate under the pointer is
  smashed. Otherwise (and not won): on a tray plate → start a drag `{t, x, y,
  start, offset = slot centre − pointer, moved = false, target = −1, wasSel}`,
  clear the selection, pick sound, haptic 5. Else, with a plate selected: a free
  cell under the pointer → `PutDown(sel, c, slot centre, .16cw)`; anything else
  deselects (drop sound).
- **Drag move:** once the pointer has moved 8 dp, the plate follows at
  `(x + ox·.3, y − .45cw + oy·.3)` and the target is the nearest `Free` cell
  within `.75 cw` of that point (vertical distance divided by .9). A soft tick
  (1200 Hz, 30 ms, gain .025, triangle) plays when the target changes to a cell.
- **Release:** no movement → a tap: select that plate (or deselect it if it was
  selected). With a target → `PutDown(t, target, drag point, .2cw)`. Otherwise
  the plate returns: mover to the slot over 180 ms from lift `.2cw`, drop sound.
- Drags start even while slices are flying (§49.4).
- **Editor keys:** 1–3 pick a tray plate (and put the cursor on the first empty
  cell), arrows move the cursor, Enter/Space put the plate down (or smash in
  hammer mode), U undo, H hammer, N new plates, Esc cancels hammer or selection.

---

## 51. Cakes: the 3D slices, materials and toppings

> **Rewritten for the Blender assets.** This replaces the plan's §51.1–51.4
> (`SliceMeshBuilder`, the unlit `CakeSlice.shader`, the generated top patterns,
> the topping and piping billboards). §51.8–51.10 are the plan's §51.5–51.7
> (plates and stands, static art, icons), with small changes marked.

The web draws each slice as flat polygons in a fixed back-to-front order
(`drawSlice`). In Unity every slice is a ready-made 3D model, one per cake, made
in Blender from the same design. Everything is in one mesh and its baked texture:
- the sponge and its fillings (seen in the cut faces);
- the coat and its drips;
- the pattern on top;
- the piped cream;
- the topping.

Depth sorts the faces, so a spinning slice simply rotates. Nothing about a slice
is generated in Unity.

### 51.1 The assets

Ten folders, one per cake, in `playbox/art/cake-sort/` and in the download
`CakeSort_UnityAssets.zip`. Put them in the project as delivered:

```
Assets/_Project/Art/CakeSort/
├─ README.md                        index of the ten cakes, with the checks
├─ strawberry/
│  ├─ strawberry_slice.glb          the game mesh: 1 mesh, 1 material, at most 1,200 triangles, the 512 atlas embedded
│  ├─ textures/
│  │  ├─ StrawberrySlice_albedo.png the base colour atlas, 512 × 512 (sRGB)
│  │  └─ StrawberrySlice_normal.png the tangent-space normal atlas, 512 × 512 (OpenGL, +Y up, like Unity)
│  ├─ README.md                     this cake's notes: units, material, outline decoding, checks
│  └─ stats.json                    every check's numbers from the build (the asset tests read it, §51.11)
├─ chocolate/   lemon/   matcha/   blueberry/   birthday/   mango/   cookies/   redvelvet/   caramel/
```

Reference only, kept out of `Assets/`. They are in the repository and in
`CakeSort_Reference.zip`:
- each cake's `renders/`: the hi-res model and the game asset seen by the game
  camera, each also on a transparent background;
- the `textures/*_1024.png` bake masters;
- the Blender scripts that rebuild everything (`cake_slice.py` and its parts).

| # | Cake | Folder and GLB | Mesh / textures | Triangles | Top of the slice (y) | Coat | On top | Ink (`_Ink`) | Unlocks at level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Strawberry | `strawberry/strawberry_slice.glb` | `StrawberrySlice` | 1156 | 0.99 | frosted to the counter | strawberry on a cream rosette | `#4A1626` | 1 |
| 1 | Chocolate | `chocolate/chocolate_slice.glb` | `ChocolateSlice` | 368 | 0.88 | frosted to the counter, drips down the outside | embossed chocolate square; ganache swirl | `#24100A` | 1 |
| 2 | Lemon | `lemon/lemon_slice.glb` | `LemonSlice` | 1000 | 0.98 | bare sides, glaze dripping down | candied lemon half-wheel on a rosette | `#4A3008` | 1 |
| 3 | Matcha | `matcha/matcha_slice.glb` | `MatchaSlice` | 1000 | 0.98 | frosted to the counter | tea leaf on a rosette; matcha dust | `#1F3A16` | 3 |
| 4 | Blueberry | `blueberry/blueberry_slice.glb` | `BlueberrySlice` | 1160 | 1.02 | frosted to the counter | three blueberries on a rosette | `#2A1A4A` | 5 |
| 5 | Birthday | `birthday/birthday_slice.glb` | `BirthdaySlice` | 1030 | 1.21 | frosted to the counter | lit striped candle on a rosette (§51.7); sprinkles | `#18304A` | 8 |
| 6 | Mango | `mango/mango_slice.glb` | `MangoSlice` | 456 | 0.93 | bare sides, glaze dripping down | three mango cubes | `#4A2408` | 12 |
| 7 | Cookies & Cream | `cookies/cookies_slice.glb` | `CookiesCreamSlice` | 468 | 0.92 | bare sides, thick cream top | sandwich cookie; crumbs | `#1E1A19` | 16 |
| 8 | Red Velvet | `redvelvet/redvelvet_slice.glb` | `RedVelvetSlice` | 422 | 0.90 | bare sides, thick cream top | raspberry; crumbs | `#3E0A14` | 21 |
| 9 | Caramel | `caramel/caramel_slice.glb` | `CaramelSlice` | 490 | 0.96 | frosted to the counter, drips down the outside | hazelnut on a caramel dollop; caramel drizzle and salt | `#3A1C08` | 27 |

The index numbers are the cakes' ids in the engine and the save (§55.1). Each
GLB's mesh and material are named after the asset name; the textures are
`textures/<asset>_albedo.png` and `textures/<asset>_normal.png`. "Top of the
slice" is the highest point of the topping, in units of the cake's radius.

What tells the cakes apart at a glance (§55.1) is all in the meshes:
- the topping's silhouette;
- frosted or bare sides;
- the layer stripes in the cut faces;
- the pattern on top.

The colours and layers follow `CAKES` in the web source, a touch deeper where
lighting would wash them out. What differs, on purpose:
- toppings are 3D and turn with the slice;
- the top patterns are baked from modelled relief (swirl, dust, sprinkles,
  crumbs, drizzle), and the cream is a piped rosette;
- Strawberry's cut faces show two cream fillings, not cream and jam;
- the Birthday candle is lit (§51.7).

The §55.1 colours are still used for what is not a slice:
- crumbs (top colour);
- the float text (§52.5);
- the shards' cake bits;
- the sparkles.

### 51.2 Import

- **Importer:** glTFast (`com.unity.cloud.gltfast`). UnityGLTF works too.
  - Both import the GLB with **X negated** (glTF is right-handed, Unity
    left-handed) and **v flipped on every UV set**. The decoding in §51.4 and the
    checks in §51.11 assume exactly that.
  - The outline data are in **UV1 and UV2** (`TEXCOORD_1`, `TEXCOORD_2`), so
    the importer must keep all three UV sets. Do not convert the GLBs to FBX or
    re-export them.
- **The importer's own material is not used.** The GLB's material carries
  `KHR_materials_clearcoat` and `KHR_materials_specular` from Blender; ignore
  any warnings about them. Only the GLB's **Mesh** is used.
- **Textures:** use the loose PNGs in `textures/`, not the copies embedded in
  the GLB.

  | Texture | Type | sRGB | Mipmaps | Max size | Wrap / filter | Compression |
  | --- | --- | --- | --- | --- | --- | --- |
  | `*_albedo.png` | Default | on | on | 512 | Clamp / Bilinear | ASTC 6×6 (iOS, Android), ETC2 fallback |
  | `*_normal.png` | Normal map | off | on | 512 | Clamp / Bilinear | ASTC 6×6 |

  The atlas has margins baked out (EXTEND), so mipmaps and compression don't
  bleed seams.
- **What the mesh is, after import** (object space, Unity axes, cake radius 1):
  - Pivot: the cake's centre, i.e. the slice's point, on the counter. The base
    is at y = 0.
  - The slice spans from −X turning toward −Z. Bounds: x from −1.024 to 0.02,
    z from −0.887 to 0.023. Its outer face is at radius 1; the coat's lip
    reaches 1.024.
  - The coat's top is at y = 0.71. Toppings reach 0.88–1.21 (table above).
  - In web angles (§47) the slice covers **120°–180°**; §51.3 turns it to
    0°–60°.
  - One submesh. Vertex data: position, normal, tangent, UV0 (the atlas), UV1,
    UV2 (outline data, §51.4). No vertex colours.
- **Heights are already right.** The coat's top at 0.71 is `.52 / cos α`
  (§47): the web's cake height `.52 R`, divided by `cos α`. Scale the slice
  uniformly by `R`, and **never divide its height by `cos α` again**.
- **Faces are single-sided.** Every face the game camera can see faces outward,
  and sponge faces that are always covered have no texture space. Six slices
  close a whole cake with no gaps: no visible overlap between neighbours, and no
  ray from the game camera reaches a sponge cut face from outside or hits a back
  face first. Each cake's README has the numbers.

### 51.3 Slice prefabs (`CakeSlicePrefabBuilder`, editor, run by `Playbox/Build/Prefabs`)

For each cake it writes a material and a prefab:

```
Slice_<cake>.prefab   SliceView; localRotation = yaw a, localScale = R, position = the plate's top centre (below)
└─ Model              MeshFilter: the GLB's Mesh; MeshRenderer: CakeSlice_<cake>.mat
                      localRotation = Euler(0, −120, 0); layer CakeSort; cast/receive shadows off;
                      light probes and reflection probes off
```

- **The mesh.** Take it straight from the GLB:
  `AssetDatabase.LoadAllAssetsAtPath(glbPath).OfType<Mesh>().Single()`. Don't
  instantiate the importer's prefab, so no importer node transform gets in.
- **The frame.** The `Model` child's −120° yaw turns the slice from web angles
  120°–180° to **0°–60°**, the plan's slice frame (§47). Its pivot stays at the
  cake's centre.
- **Angle.** A slice whose start angle is `a` (web radians, §52) has
  `transform.localRotation = Quaternion.Euler(0, a * Mathf.Rad2Deg, 0)`. Slot
  `i` of a plate is `a = SLOT0 + i·SEG` (§52.1). A whole cake is the six slices
  at `rot + i·SEG`.
- **Size.** `localScale = Vector3.one * R`, with `R = .8 pr` (world units are
  dp, §50.1). A flying slice is scaled by `R·sc` (§52.4). Served cakes and the
  dragged plate scale with their plate.
- **Position.** At the centre of its plate's **top disc**, raised to the top of
  the well (§51.8). The web draws a plate's top and its slices from the same
  point (`drawPlateVis`), so the slice root sits on that point. On the counter
  the plate's top is `.075 pr / cos α` above `y = 0`. A lifted plate (drag,
  flight, the tray bob) carries its slices with it.
- **Material.** `Materials/CakeSort/CakeSlice_<cake>.mat`, shader
  `Playbox/CakeSlice` (§51.4):
  - `_BaseMap`: the albedo PNG.
  - `_BumpMap`: the normal PNG.
  - `_Ink`: the cake's ink (table above), set with `SetColor`.
  - `_FlameY`: `1.10` on Birthday, `99` on the others.
  - SRP Batcher compatible. One material per cake, since each has its own
    atlas.
- **Config.** `Cakes.asset` (§55.1) gains two fields per cake: `Slice` (the
  prefab) and `Ink` (the colour).
- **Pool** (`SlicePool`, in `CakeRig`): pooled `SliceView`s per cake. A
  full counter holds up to 20 plates × 6, plus the tray (3 × 6), flying slices,
  and served cakes (6 each). Start with 24 per cake and grow on demand.
- **Cost.** About 1,000 triangles per slice, and two passes (slice and outline).
  A full counter of 120 slices is under 300k triangles and about 240 draws,
  which the SRP Batcher handles easily on mid-range phones.

### 51.4 `CakeSlice.shader`

It replaces the plan's unlit shader with a lit one. The slices were modelled and
textured to be lit like the Blender renders, so the shader has two passes:

1. **Slice.** The atlas colour, lit by a key, a fill, a rim and a sky/ground
   ambient, with the baked normal map. The light values are globals (§51.5),
   so the counter needs no Unity lights, like the rest of the game.
2. **Outline.** An inverted hull: the mesh is pushed out a fixed number of
   **screen pixels** along smooth normals stored in UV1 and UV2, drawn with
   front faces culled in the cake's ink colour. In object units the line would
   vanish: at the counter a plate is about 76 px across at 2x, so R is about
   29 px.

The maths is in **linear** space, like Blender's. The albedo imports as sRGB
and is sampled linear, `_Ink` is set with `SetColor`, and the globals are
linear values set with `SetGlobalVector`.

```hlsl
Shader "Playbox/CakeSlice"
{
    Properties
    {
        [MainTexture] _BaseMap ("Albedo (sRGB)", 2D) = "white" {}
        [Normal] _BumpMap ("Normal map", 2D) = "bump" {}
        _Ink ("Ink", Color) = (0.29, 0.086, 0.149, 1)
        _FlameY ("Flame above object y (Birthday 1.10)", Float) = 99
        _Flicker ("Flame flicker (per renderer)", Float) = 1
    }
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
        TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4  _Ink;
            float  _FlameY;
            float  _Flicker;
        CBUFFER_END

        // The look, shared by every cake: set by CakeLook (§51.5), linear, world space.
        float4 _CakeKeyDir, _CakeFillDir, _CakeRimDir;   // xyz: unit vector toward the light
        float4 _CakeKey, _CakeFill, _CakeRim;            // rgb: colour × strength
        float4 _CakeSky, _CakeGround;                    // the ambient: lerp by the normal's y
        float4 _CakeSpec;                                // rgb: colour × strength, a: Blinn-Phong exponent
        float  _CakeOutlinePx;                           // the outline's width in screen pixels

        // The Birthday candle's flame (object y above _FlameY) stretches in y about its base.
        float3 FlameFlicker(float3 p)
        {
            if (p.y > _FlameY) p.y = _FlameY + (p.y - _FlameY) * _Flicker;
            return p;
        }
        ENDHLSL

        Pass
        {
            Name "Slice"
            Tags { "LightMode" = "UniversalForward" }
            Cull Back ZWrite On ZTest LEqual

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS   : NORMAL;
                float4 tangentOS  : TANGENT;
                float2 uv0        : TEXCOORD0;
                float2 uv2        : TEXCOORD2;
            };
            struct Varyings
            {
                float4 positionCS  : SV_POSITION;
                float2 uv          : TEXCOORD0;
                float3 positionWS  : TEXCOORD1;
                float3 normalWS    : TEXCOORD2;
                float3 tangentWS   : TEXCOORD3;
                float3 bitangentWS : TEXCOORD4;
                float  weight      : TEXCOORD5;
                float  flame       : TEXCOORD6;
            };

            Varyings Vert(Attributes v)
            {
                Varyings o;
                VertexPositionInputs p = GetVertexPositionInputs(FlameFlicker(v.positionOS.xyz));
                VertexNormalInputs n = GetVertexNormalInputs(v.normalOS, v.tangentOS);
                o.positionCS = p.positionCS;
                o.positionWS = p.positionWS;
                o.normalWS = n.normalWS; o.tangentWS = n.tangentWS; o.bitangentWS = n.bitangentWS;
                o.uv = TRANSFORM_TEX(v.uv0, _BaseMap);
                o.weight = 1 - v.uv2.y;                          // the outline weight (§51.4, below)
                o.flame = v.positionOS.y > _FlameY ? 1 : 0;
                return o;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).rgb;
                if (i.flame > 0.5) return half4(albedo, 1);      // the candle flame: unlit, no ink

                float3 nGeo = normalize(i.normalWS);
                float3 V = GetWorldSpaceNormalizeViewDir(i.positionWS);     // orthographic-aware
                // The topping (weight 0) has no hull: ink it where it turns away from the camera.
                // Blender's Layer Weight "Facing" with blend 0.2 is 1 - |N.V|^0.4, on the unbumped normal.
                if (i.weight < 0.1)
                {
                    half facing = 1 - pow(abs(dot(nGeo, V)), 0.4);
                    albedo = lerp(albedo, _Ink.rgb, smoothstep(0.62, 0.8, facing));
                }

                half3 nTS = UnpackNormal(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv));
                float3 N = normalize(TransformTangentToWorld(nTS, half3x3(i.tangentWS, i.bitangentWS, nGeo)));

                float3 light = lerp(_CakeGround.rgb, _CakeSky.rgb, N.y * 0.5 + 0.5)
                             + _CakeKey.rgb  * saturate(dot(N, _CakeKeyDir.xyz))
                             + _CakeFill.rgb * saturate(dot(N, _CakeFillDir.xyz));
                float  rim  = saturate(dot(N, _CakeRimDir.xyz)) * pow(1 - saturate(dot(N, V)), 2);
                float3 H    = normalize(_CakeKeyDir.xyz + V);
                float3 spec = _CakeSpec.rgb * pow(saturate(dot(N, H)), _CakeSpec.a);
                return half4(albedo * light + _CakeRim.rgb * rim + spec, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "Outline"
            Tags { "LightMode" = "SRPDefaultUnlit" }
            Cull Front ZWrite On ZTest LEqual

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            struct Attributes { float4 positionOS : POSITION; float2 uv1 : TEXCOORD1; float2 uv2 : TEXCOORD2; };
            struct Varyings   { float4 positionCS : SV_POSITION; float weight : TEXCOORD0; };

            Varyings Vert(Attributes v)
            {
                Varyings o;
                // The smooth outline normal (object space) and the weight, as the importer leaves them.
                float3 outlineNormal = normalize(float3(-v.uv1.x, 1 - v.uv1.y, v.uv2.x));
                float  weight = 1 - v.uv2.y;
                float4 pos = TransformObjectToHClip(FlameFlicker(v.positionOS.xyz));
                float3 nWS = TransformObjectToWorldDir(outlineNormal);
                float2 nCS = SafeNormalize(float3(mul((float3x3)UNITY_MATRIX_VP, nWS).xy, 0)).xy;   // no NaN facing the camera
                float  px  = _CakeOutlinePx * weight * step(0.5, weight);
                pos.xy += nCS * (2.0 * px / _ScreenParams.xy) * pos.w;
                o.positionCS = pos;
                o.weight = weight;
                return o;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                clip(i.weight - 0.49);                       // no hull on cream and toppings
                return half4(_Ink.rgb, 1);
            }
            ENDHLSL
        }
    }
}
```

If the URP renderer ever needs a depth prepass (SSAO, depth texture), add a
`DepthOnly` pass that applies `FlameFlicker`. Nothing in Cake Sort needs one
today.

**What the outline data mean.** These are the values the shader above decodes.
The file stores them in glTF space, and the importers turn them into the Unity
values below.

| | In the GLB (glTF space) | In Unity, after glTFast or UnityGLTF |
| --- | --- | --- |
| Outline normal | `TEXCOORD_1 = (nx, ny)`, `TEXCOORD_2.x = nz` | `normalize(-uv1.x, 1 - uv1.y, uv2.x)` |
| Weight | `TEXCOORD_2.y = weight` | `1 - uv2.y` |

| Weight | Where | The hull |
| --- | --- | --- |
| 1 | the cake: sponge, coat, cut faces | full width (`_CakeOutlinePx`) |
| 0.5 | the coat's lip at the counter, on frosted cakes (the normal points down and out) | half width |
| 0.25 | piped cream | none (the cream gets no ink) |
| 0 | the topping (and the Birthday flame) | none: a hull would poke through what the topping sits on. The slice pass inks its grazing edges instead (above), except the flame. |

- The outline normals are the smooth average across the cut faces' hard edges.
  At hard edges they are the bisector of the faces that meet. That is why the
  hull does not crack at the slice's corners.
- **Seam lines are intended.** On a whole cake, each slice's hull shows as a
  thin ink line along the seams on top (see `renders/lod_game_cake.png`). The
  web also draws an edge on every slice, and it lets the player count slices.
- `_CakeOutlinePx`: about **2.5 px at 2x and 1.5 px at 1x**, i.e.
  `max(1.5, 1.25 × pixels per dp)`. `CakeRig` sets it once per screen size.
  `CakeIconRig` sets **1.2** while it renders icons and restores it after.

### 51.5 The look (`CakeLook`, set once by `CakeRig` and again by `CakeIconRig`)

**The target.** Match each cake's `renders/lod_game_cake.png` and
`renders/lod_game_single.png`: the GLB with its outline hull, under Blender's
studio lights, seen by the game camera (orthographic, pitched 42.84°). The
`hero.png` render shows the hi-res model. The game asset is meant to read the
same at game size, not to match it in close-up.

**The Blender lights, in Unity world axes (§47).** Each is a direction toward
the light, from the cake.

| Light | Direction (x, y, z) | Relative strength | Colour |
| --- | --- | --- | --- |
| Key (upper left, in front) | (−0.588, 0.626, −0.512) | 1 | warm white (1.00, 0.97, 0.94) |
| Fill (right, in front, low) | (0.715, 0.344, −0.609) | .27 | cool white (0.94, 0.96, 1.00) |
| Rim (behind, right) | (0.584, 0.306, 0.751) | .5 (edges only) | (1.00, 0.95, 0.95) |
| Top (soft, overhead) | (−0.268, 0.948, −0.170) | .1, fold into the ambient | white |
| Sky / ground ambient | Blender's world: (1.00, 0.96, 0.94) above, (0.62, 0.52, 0.48) below, strength 0.45 | | |

The game has no shadows; the plates' blob shadows (§51.8) ground the cakes.

**Starting values** (linear; tune them side by side with the renders, then keep
them in one place):

| Global | Value |
| --- | --- |
| `_CakeKeyDir` | (−0.588, 0.626, −0.512, 0) |
| `_CakeFillDir` | (0.715, 0.344, −0.609, 0) |
| `_CakeRimDir` | (0.584, 0.306, 0.751, 0) |
| `_CakeKey` | (0.75, 0.72, 0.69, 0) |
| `_CakeFill` | (0.16, 0.17, 0.18, 0) |
| `_CakeRim` | (0.25, 0.24, 0.24, 0) |
| `_CakeSky` | (0.42, 0.40, 0.40, 0) |
| `_CakeGround` | (0.26, 0.22, 0.21, 0) |
| `_CakeSpec` | (0.22, 0.22, 0.22, 24) |
| `_CakeOutlinePx` | §51.4 |

With these, a lit top shows at about 0.95 × its albedo, a cut face turned toward
the camera at about 0.8 ×, and a side turned away at about 0.5 ×. That is roughly
what the renders show.

Until `CakeLook` runs, the globals are 0: the slices render black and have no
outline. Make `CakeLook` `[ExecuteAlways]` (values in `Cakes.asset`), so the
editor's scene view and prefab previews show the real look.

- **Themes.** The slices don't change with the light/dark theme; the plates,
  cloth and glass do (§54.1).
- **Not ported from the web:**
  - the screen-fixed glaze sheen, replaced by the key light's highlight;
  - the side shading `_Cake`, replaced by real lighting;
  - the edge lines on every face, replaced by the outline and the ink lines
    baked into the cut faces' fillings.

### 51.6 What the slice frame is

The web works in slice angles, and the prefab (§51.3) turns the model into the
web's frame, so the web's formulas apply unchanged:
- **Centre and angles.** The slice root is the cake's centre. A slice with
  start angle `a` covers web angles `[a, a + SEG]`, clockwise on screen.
- **Centroid.** `RC = .6366` (the centroid of a sixth of a disc, as a share of
  R) is at web angle `a + SEG/2`, at radius `RC·R` from the root: §52.4's
  flight formulas place the root correctly.
- **The topping** stands at radius `.56 R` on the slice's middle angle (the web
  draws it at `.5 R`).

### 51.7 Birthday's candle flame

The flame is part of the Birthday mesh, baked as a flat warm yellow (#FFC94A).
In the imported mesh:

| Part | Object y | Centre (x, z) |
| --- | --- | --- |
| Flame | 1.108–1.208 | (−0.485, −0.28) |
| Wick | 1.086–1.12 | (−0.485, −0.28) |
| Candle's top | 1.09 | (−0.485, −0.28) |

The point (−0.485, −0.28) is `.56 R` along the slice's middle angle. Its
material has `_FlameY = 1.10`, so everything above y 1.10 counts as flame:
- **Unlit.** The fragment returns the albedo as it is, with no lighting and no
  ink.
- **Flicker.** Vertices above 1.10 stretch in y about 1.10 by `_Flicker`. It is
  `1` from the material (on the counter, in the tray, in flight). On **served
  cakes** and the **unlock turntable** set it per renderer with a
  `MaterialPropertyBlock` to `.8 + .2·sin(t·.03)`, with t in ms (plan §51.4,
  §52.5, §52.7). The renderers that take a block simply leave the SRP Batcher.
- **No hull.** The flame's weight is 0.

The wick's very tip (1.10–1.12) falls inside the flame and is lit the same way;
at game size you can't tell.

### 51.8 Plates and stands (plan §51.5)

- **Plate** (`PlateMeshBuilder`, radius `pr`):
  - edge disc at `y = 0`: a short cylinder `.075 pr / cos α` high, in
    `cs-plate-edge`;
  - top disc in `cs-plate`;
  - rim ring at `.87 pr` (width `max(1, .035 pr)`) in `cs-plate-line`;
  - well disc `.72 pr` in `cs-plate-well`, raised a hair.
  - Shadow: `fx_hex_blob` on the counter at `(+.05 pr, +.26 pr)`, radius
    `1.02 pr`, tinted `cs-shadow`. (`(+.05 pr, +.26 pr)` is the web's screen
    offset, right and down; convert it as §47 says.)
  - **Changed:** the slices stand on the well's top at the plate's centre
    (§51.3). The well (`.72 pr`) lies inside the cake's footprint (`R = .8 pr`),
    so a full plate hides it.
- **Cake stand with a cloche** (cells that hold nothing):
  - stand disc `.82 pr` (edge + top like a plate);
  - a cupcake billboard `cs_cupcake.png` (port of the cupcake part of
    `drawCloche`);
  - a glass dome: a half ellipsoid with radii `(.74 pr, 1.15 pr / cos α, .74 pr)`
    in `CakeGlass.shader` (transparent, `cs-glass` fill, a 1–2 dp white α .75
    rim by Fresnel, and a white α .8 highlight stroke on the upper left), with a
    knob on top.
- **Theme.** Plate, glass and edge colours come from §54.1 and update live.

### 51.9 Static art (generated textures, plan §51.6)

| File | Size | Contents |
| --- | --- | --- |
| `cs_gingham.png` | 64 × 64, Repeat | White; two transparent-white crossing bands make a gingham check in white α 1 / α .5 / α 0 (tinted `cs-check` over `cs-cloth`) |
| `cs_doily.png` | 256 × 256 | White scalloped disc (18 scallops) with a dashed ring at 78%; tinted `cs-mat` / `cs-mat-edge` (two layers) |
| `cs_tray_wood.png` | 512 × 128, sRGB | Rounded board (radius 22 px scaled), vertical gradient white → 0.85 grey, 4 grain curves black α .08; tinted `cs-wood → cs-wood-2` by a two-colour gradient material |
| `cs_cupcake.png` | 128 × 160 | Cupcake from `drawCloche` |
| `cs_hand.png` | 128 × 128 | The tutorial hand (`drawHand`) in white with an ink outline |
| `tex_board_cake_sort_light.png`, `…_dark.png` | 1600 × 1000 | Board art (§0.6) |

**Removed:** `cs_pattern_*.png`, `cs_top_*.png`, `cs_pipe.png` and
`cs_flame.png`. They are in the slices now.

### 51.10 Cake icons (`CakeIconRig`, plan §51.7)

The HUD chips, lobby, win sheet and collection show whole cakes on plates. A
hidden rig renders each cake into a cached 128 × 108 sRGB RenderTexture, once per
cake per theme:
- the plate radius fills the icon, at `rot` 0;
- the six slice prefabs at `SLOT0 + i·SEG`;
- the game camera's pitch;
- `_CakeOutlinePx = 1.2`.

The locked icon is a plate with a `cs-plate-edge` cylinder, a grey `#888888` top
and a white "?" (800 weight, `.9R`). The unlock sheet's turntable (§52.7)
renders live. Leave headroom above the plate for the tallest topping: the
Birthday flame reaches `1.21 R`. Optional: the `renders/*_alpha_0001.png` images
(transparent backgrounds) are store or marketing art, not used by the game.

### 51.11 Asset checks (EditMode `CakeAssetTests`, part of milestone CS3)

For each of the ten GLBs, reading the cake's `stats.json` next to it:

1. **Import.** Exactly one `Mesh` with UV0, UV1 and UV2, normals and tangents.
   - Its triangle count equals `glb_check.triangles` and is at most 1,200.
   - Its vertex count equals the sum of `unity_decode.weights_found`.
2. **Axes.** The bounds are x ∈ [−1.03, 0.03], y ∈ [0, 1.22] and z ∈
   [−0.89, 0.03], with min x below −1.0 and min z below −0.88. This catches an
   importer that didn't negate X, or a stray node transform.
3. **Outline data.**
   - Every weight `1 − uv2.y` is 0, 0.25, 0.5 or 1 (± .01), with the counts of
     `unity_decode.weights_found`.
   - For every vertex with weight ≥ 0.5, the decoded outline normal has a dot
     product above 0.3 with the vertex normal. The build measured: smooth
     vertices above 0.5, hard edges at least 0.354.
4. **Frame.** With the prefab's −120° child applied, every vertex at a
   radius above 0.3 lies at a web angle (§47) in [−5°, 65°], and the mean
   direction of those vertices is within 3° of 30°. (A few hidden vertices just
   under the coat lap up to 4° over a seam. They are buried in the
   neighbouring slice and never seen.)
5. **Birthday.** 45 vertices lie above y 1.10: the flame and the tip of the
   wick. The other cakes have none above 1.05.
6. **Prefabs.** Each `Slice_<cake>` has one renderer and one material
   (`Playbox/CakeSlice`), with the cake's `_Ink` and the right `_FlameY`.
   `Cakes.asset` points at all ten.

**Visual check (CS3):** with the game camera, put one whole cake of each kind on
a plate at about the renders' scale. Compare it with `renders/lod_game_cake.png`
and tune `CakeLook` until they read the same. Then check the levels against the
web (§58).

---

## 52. Animations and effects

Time in ms. Easing names are §14.2's (`easeOutCubic`, `easeInOutCubic`), plus
`easeOutBack(t) = 1 + 2.6(t − 1)³ + 1.6(t − 1)²` and
`easeInBack(t) = 2.7t³ − 1.7t²`.

### 52.1 Visual slices and the turntable

Each plate's visual holds a list of visual slices in the same order as its
state list. A visual slice: `{ f, a0, a1, t0, dur, spin, ghost }`; its angle at
time t is `a1` once `t ≥ t0 + dur`, else
`a0 + (a1 − a0)·ease((t − t0)/dur)` with `ease = spin ? easeOutBack : easeOutCubic`.
Slot `i` sits at `SLOT0 + i·SEG`, `SLOT0 = 7π/6` (a plate fills from the back
left, clockwise).

```
Reslot(plate, t, dur, turns):              // every slice eases to its slot; `turns` extra full turns
    for slice i: cur = Angle(slice, t); target = SLOT0 + i·SEG
                 d = ((target − cur) mod 2π + 2π) mod 2π; if d > π: d −= 2π      // shortest way round
                 a0 = cur; a1 = cur + d + turns·2π; t0 = t; dur; spin = turns > 0
```

A plate is **settled** when no slice is a ghost or still easing, it is not dying,
and its pop-in has finished; settled plates can be drawn from a cached snapshot
(the web caches a sprite per slice list; in Unity, static batching or simply
leaving the meshes alone is enough).

### 52.2 Plates appearing and leaving

- **Born** (pop-in): scale `easeOutBack(clamp((t − born)/420))` (0 before
  `born`).
- **Dying:** scale `1 − easeInBack(clamp((t − dying)/300))`; removed 300 ms after
  `dying`.
- **Landing squash** after a drop: `born = now − 200`, so the last 220 ms of the
  pop-in play.

### 52.3 A step (`PlayStep`, port of `playStep`)

```
FLIGHT = 470, STAGGER = 75
dest = visual plate at step.D (if missing: return 0)
total = Σ slices in step.From
insert `total` ghost slices of step.F after the last slice of step.F on dest (or at the end);
    each ghost starts at its slot angle
span = FLIGHT + STAGGER·(total − 1)
Reslot(dest, now, span + 90, turns: 1)          // the plate turns one full turn while slices fly in
spin sound
k = 0; fill0 = dest slice count − total
for each (src, m) in step.From:
    for j < m: take the last slice of step.F off src's visual; a0 = its angle now; ghost = ghosts[k]
               turn = the multiple of 2π that puts (ghost.a1 + turn − a0) in [2π, 4π)   // one to two full spins
               flyer { f, from = src centre, a0, ghost, turn, dest = step.D, t0 = now + k·STAGGER, dur = FLIGHT, note = fill0 + k }
               k++
    src empty → dying at now + k·STAGGER; else Reslot(src, now + k·STAGGER, 320, 0)   // the gap closes after the last slice leaves
for each emptied cell not yet dying: dying at now + span/2
if step.Cake: after span + 110 → Serve(step.D, step.F) (if the queue generation is unchanged); return span + 260
return span + 150
```

### 52.4 Slices in the air (`FlyerPose`, port of `flyerPose`)

```
u = clamp((t − t0)/dur), e = easeInOutCubic(u)
ga = Angle(ghost, t)                                   // the ghost spins with the turntable
RC = .6366 (centroid of a sixth of a disc, as a share of R)
c0 = from centre + RC·R·(cos(a0 + SEG/2), sin(a0 + SEG/2)·SQ)      // screen dp
c1 = dest centre + RC·R·(cos(ga + SEG/2), sin(ga + SEG/2)·SQ)
ang = a0 + (ga + turn − a0)·e                          // a full spin (or a bit more) on the way over
sc = 1 + .14·sin(πu); lift = .72 cw·sin(πu)
m = lerp(c0, c1, e)
slice centre = m − RC·R·sc·(cos(ang + SEG/2), sin(ang + SEG/2)·SQ) − (0, lift)
```

Draw the flying slice at that centre with start angle `ang` and radius `R·sc`
(scale the slice transform), lifted by `lift` (world `y = lift / cos α`). Its
shadow: `fx_hex_blob` at `m + (0, .1 pr)`, radius `.42 pr`, alpha
`.55·(1 − lift/(1.2 cw))`, colour `cs-shadow`. A flyer whose `t0` has not come
sits at its start pose (`u = 0`).

**Landing** (`t ≥ t0 + dur`): remove the flyer, the ghost becomes a real slice
(same angle, so nothing jumps), land sound with `note`, 4 crumbs (§52.6) in the
cake's top colour at the dest centre, `cake height` up.

**Take-off** (first frame with `t ≥ t0`): whoosh sound.

### 52.5 Serving a cake (`Serve`, port of `serve` and `drawServed`)

```
plate at c: a = angle of its first slice now (or SLOT0); its slices are cleared; dying = now + 620
served { f, x, y = cell centre, a, t0 = now, target = centre of the cake's chip icon (or the meter) in screen dp }
combo++; cake sound(combo); haptic [18,40,18]
float text "{Name}!" (or "{Name}! ×{combo}", large, when combo > 1) at (x, y − 1.1 pr), colour = top (side for the white-topped Cookies & Cream and Red Velvet)
draw (on the CakeFx layer):
    e1 = clamp((t − t0)/620), e2 = clamp((t − t0 − 620)/520); done when e2 ≥ 1
    rot = a + easeOutCubic(e1)·3π + e2·2π            // a fast one-and-a-half turns, then a slow turn in flight
    phase 1 (e2 == 0): position (x, y); scale 1 + .16·sin(π·min(1, 1.3 e1)); lift .18 cw·sin(π e1)
                       glow ring: ellipse at (x, y − .2 pr) radius pr·(1 + .5 e1), 4 dp, #FFE38A, alpha .55·(1 − e1)
    phase 2: e = easeInOutCubic(e2); position lerp((x, y), target, e) − (0, .9 cw·sin(πe)); scale lerp(1, .32, e)
    six slices at rot + i·SEG
at t0: a sparkle burst (16 stars, §52.6) at (x, y − .3 pr) in the top colour, #FFE38A and white
at t0 + 1140: removed; that cake's shown count +1, the chip bumps (scale 1.22 at 30% over 450 ms, cubic-bezier(.2,1.6,.4,1)), served sound, meter and counter update
```

Shown counts (`shown[f]`, `shownTotal`) lag the state on purpose: the order card
counts a cake when it lands there. On undo, restart and win they are reset to the
state.

### 52.6 Particles (CakeFx layer, gravity in dp/ms²)

| Kind | Spawn | Motion | Look |
| --- | --- | --- | --- |
| Crumb | 4 at a landing, x spread ±.25 pr | vx ±.06, vy −.08…−.20, g .0009, life 380 | square, half-size .03–.06 pr, cake top colour, alpha 1 − q² |
| Star | 16 around a served cake, evenly spaced angles + up to .3 rad | speed .12–.28 (vy × .8 − .05), g .00012, ×.97 per frame, life 650–950 | 8-point star (radii r and .35r), r .08–.16 pr, spinning `spin + life·.006` rad, alpha 1 − q² |
| Shard | 18 on a hammer smash (every 3rd is a crumb in the plate's cake colours) | random angle, speed .10–.32, upward, g .0011, life 600–900 | triangle `(−r, −.4r) (r, −.7r) (.2r, .8r)` in `cs-plate`, r .07–.15 pr, spinning `vs ±.015`/ms |

### 52.7 Small motion

- **Dragged plate:** drawn at the drag point lifted `.2 cw`, scale 1.06, with a
  shadow ellipse at the drag point (`.95 pr × .9·SQ`), on top of everything else.
- **Selected tray plate:** bobs `.16 cw + .04 cw·sin(t·.007)`.
- **Target cell** (drag or keyboard): filled ellipse `1.08 pr` in `cs-accent` at
  alpha `.18 + .14·pulse` and a 3 dp ring at `1.02 pr`; `pulse = .5 + .5·sin(t·.008)`.
  The keyboard cursor without a plate: a dashed 2 dp ring (5 on, 4 off).
- **Hammer mode:** every plate gets a 3 dp `cs-accent` ring at `1.08 pr`, alpha
  `.45 + .45·pulse`.
- **Unlock turntable** (new cake sheet): plate radius `min(W/2.4, H/(2·SQ + .7))`
  in a 26:19 view; slice i drops in from `.5 pr` above over 300 ms
  (`easeOutCubic`) starting at `90i` ms; the cake turns at `rot = .0011·t +
  (1 − easeOutCubic(min(1, t/900)))·2π`; the candle flame flickers (§51.7).
- **Hard intro:** as Paint Sort's (§19.4), with the text "Bake {goal} cakes[
  around {stands} cake stand(s)]. Worth {reward} coins."

---

## 53. Sound and haptics

### 53.1 Recipes (`CakeSortRecipes.cs`, group `cs_*`, through the shared synth and compressor like Paint Sort, §4.3)

A port of `makeSfx` in `cake-sort.html`. Notation as in §18.1: `tone(f, f1,
dur, gain, type, at, attack, filter, ff)`, `noise(filter, f, f1, dur, gain, q,
at, attack)`, `bell(f, at, gain)`; `note(base, s) = base·2^(s/12)`;
`penta = [0,2,4,7,9,12,14,16,19,21,24,26,28]`.

| Clip | Recipe |
| --- | --- |
| `cs_pick` | tone 1760, .05, .05, triangle; tone 520→780, .08, .10 |
| `cs_drop` | tone 640→420, .08, .08 |
| `cs_place` | noise bandpass 2600, .05, .16, q 3; tone 340→230, .10, .18; tone 2350, .22, .035, triangle, at .01 |
| `cs_whoosh` | noise bandpass 500→2600, .26, .06, q 1.2, attack .05 |
| `cs_land_0` … `cs_land_12` | `f = note(392, penta[k])`: tone f→1.01f, .16, .13, triangle; tone 2f, .08, .04; noise lowpass 900, .05, .05 |
| `cs_spin` | tone 260→620, .30, .035, triangle, attack .04 |
| `cs_cake_0` … `cs_cake_6` | `base = note(523.25, penta[k])`: bells at note(base, 0/4/7/12), at .06·i, gain .12; noise highpass 6000, .5, .05, at .05, attack .04 |
| `cs_served` | tone 1318.5, .06, .05, square, lowpass 3800; tone 1975.5, .12, .05, square, at .05, lowpass 3800 |
| `cs_empty` | tone 980→340, .07, .08 |
| `cs_deal` | for i 0..2: noise bandpass (1400 + 300i)→2400, .07, .05, q 2, at .07i; tone 700 + 90i, .05, .04, at .07i + .02 |
| `cs_bonk` | tone 190→105, .18, .20, square, lowpass 650 |
| `cs_smash` | tone 150→55, .22, .30; for k 0..5: noise highpass 3500 + 600k, .05 + .015k, .10, at .025k; noise lowpass 900, .20, .14 |
| `cs_undo` | noise bandpass 2600→480, .22, .12, q 1.4; tone 700→420, .14, .06 |
| `cs_refresh` | for i 0..2: noise bandpass 900→2600, .12, .07, q 1.5, at .08i |
| `cs_win` | bells at note(523.25, 0/4/7/12/16/19), at .085i, gain .15; noise highpass 5500, .9, .04, at .4, attack .1; tone 130.8→131, .9, .12, triangle, at .5 |
| `cs_full` | tones note(330, 7/4/0), .22, .08, triangle, at .12i |
| `cs_coin` | the same as `sfx_coin` (§18.1) |
| `cs_unlock` | bells at note(659.25, 0/7/12/16/19/24), at .07i, gain .10 |
| `cs_hard_1`, `cs_hard_2` | Paint Sort's hard stingers (§18.1) |
| `cs_tick` | tone 1200, .03, .025, triangle |

Land notes use `min(note, 12)`; cake chimes use `min(combo, 6)`.

### 53.2 Haptics (`CakeSortHaptics`)

| Event | Pattern (ms) |
| --- | --- |
| pick up | 5 |
| plate lands | 8 |
| cake served | [18, 40, 18] |
| hammer smash | [30, 30, 50] |
| counter full | [40, 60, 40] |
| hard intro | [30, 60, 30] |
| win | [20, 40, 20, 40, 60] |

---

## 54. UI layouts

uGUI and the shared widgets (§4.8): sheets, toasts, `AppDisplay`/`AppBody`
fonts, Paint Sort's top-bar buttons, coin pill and booster-button style.

### 54.1 Tokens (light / dark, in `ThemePalette.asset`)

| Token | Light | Dark |
| --- | --- | --- |
| cs-bg-a / cs-bg-b | #FFF6EE / #FFDDE6 | #2C1622 / #12090F |
| cs-hard-a / cs-hard-b | #FFEEE7 / #FFC4BB | #3B1618 / #160809 |
| cs-super-a / cs-super-b | #F4ECFF / #D7C3FA | #2B1A4A / #100A20 |
| cs-cloth | #FFFFFF | #3A2231 |
| cs-check | rgba(240,86,140,.11) | rgba(255,255,255,.045) |
| cs-cloth-edge | #F1BCCD | #5A3349 |
| cs-mat / cs-mat-edge | rgba(255,250,252,.95) / rgba(225,120,158,.36) | rgba(255,255,255,.07) / rgba(255,160,200,.20) |
| cs-plate / cs-plate-edge | #FFFFFF / #CDD4E2 | #ECE6EC / #8F879A |
| cs-plate-well / cs-plate-line | #F2F4F9 / #F6A8C2 | #DAD3DB / #E07AA0 |
| cs-shadow | rgba(120,40,70,.20) | rgba(0,0,0,.45) |
| cs-wood / cs-wood-2 | #F4CFAB / #DDA97F | #6E4632 / #4C2E20 |
| cs-edge | rgba(80,30,45,.30) | rgba(0,0,0,.38) |
| cs-glass | rgba(205,228,255,.42) | rgba(170,200,255,.20) |
| cs-accent / cs-accent-deep / cs-accent-soft | #F0568C / #B8305F / #FFE4EE | #FF7AA8 / #B8456E / #3A1826 |

Backdrop: `Gradient.shader` from `cs-bg-a` (top) to `cs-bg-b`; hard levels use
the hard pair, super hard the super pair.

### 54.2 Lobby (`CakeLobbyScreen`)

```
CakeLobbyScreen (safe area; backdrop behind)
├─ TopBar (padding 12/16/6): Back (→ Hub) · spacer · Coin pill · Settings (app sheet + "How to play Cake Sort" ghost button)
└─ Body (scroll, padding 8/18/22 + safe bottom, gap 18)
   ├─ Wordmark "Cake " + "S","o","r","t" in #FF6F9F, #8B4A2B, #F2BE00, #7DB451 (54 display; each letter with a 3 dp drop 42% darker)
   ├─ NextCard (radius 22, padding 16, surface, shadow; vertical gap 12)
   │  ├─ Row (gap 14): CakeIcon 116×96 (a whole cake of the menu's ((n − 1) mod K)-th cake) · Meta:
   │  │     eyebrow "Up next" / "Up next · Hard" / "Up next · Super hard" (11.5 caps .12em; cs-accent / hard / super)
   │  │     title "Level N" (26 display) · sub "Bake {goal} cakes · {K} kinds[ · {stands} cake stand(s)]" (13.5 muted)
   │  ├─ MenuChips: one chip per cake on the menu: icon 28×24 + name (13 heavy muted), pill on surface-2, wrap
   │  └─ PlayButton (full width): "Play level N" / "Continue level N"; cs-accent with a 5 dp cs-accent-deep drop (hard / super styles on spikes)
   ├─ ShelfCard (radius 22, padding 14/14/16): header "Cake collection" (19 display) · "{open} of 10" (12.5 dim)
   │  └─ Grid 2 columns, gap 8: tile (radius 16, surface-2, padding 5/8/5/4, row gap 8): icon 52×44 · name (13.5 heavy) over "{n} baked" (12 dim);
   │     locked: the "?" icon, "Locked" (dim) over "Level {UnlockAt}"
   └─ Note (13.5 muted, centred): "{cakes} cake(s) baked · {won} level(s) cleared" (or the intro line for a new player) + " Levels adjust to how you play."
```

The next level's figures come from `Director.HeatFor(level)` (or the saved
attempt when resuming), so the card shows what Play will start.

### 54.3 Play screen (`CakePlayScreen`)

```
CakePlayScreen (backdrop by tier; the 3D counter renders behind the HUD)
├─ TopBar: Back (→ lobby, saves) · Level column ("Level N" 24 display; tier badge as Paint Sort) · spacer · Coin pill · Menu
├─ OrderCard (margin 2/14, padding 10/12, radius 20, surface at 82%, 2 dp line drop)
│  ├─ Row (gap 10): "Bake {goal} cakes" (14 heavy muted) · Meter (height 12, radius 999, surface-2 with an inner shadow;
│  │     fill gradient cs-accent → 70% cs-accent + #FFD45A, width = shown/goal, 450 ms) · "{shown}/{goal}" (20 display, "/goal" 15 dim)
│  └─ MenuChips: icon 28×24 + count (13 heavy muted, tabular); a chip bumps when its cake arrives (§52.5)
├─ CoachLine (level 1 only; height 46; 14 bold muted, centred)
├─ Field (flex: the counter and the tray live here, §50.1)
├─ BoosterBar (padding 6/12/12 + safe bottom; 3 columns, 84 wide): Undo (undos left) · Hammer (inventory; accent when active) · New plates (inventory)
│  counts as Paint Sort's badges ("+" on coin colour when empty); the message bar sits on top of this row:
│  MessageBar (12 from the sides, 6 above the row; radius 16, surface, shadow; rises 300 ms): text (14 heavy; bad colour when stuck) + small ghost buttons
└─ HardIntro overlay (§52.7)
```

Message bar contents: full counter → "The counter is full" with "Hammer" (or
"Hammer · 60" when none left), "Undo" (when there is a snapshot), "Restart".
Hammer mode → "Tap a plate to clear it off the counter" with "Cancel".

### 54.4 Sheets

| Sheet | Eyebrow / title / sub | Body | Actions |
| --- | --- | --- | --- |
| New cake | "New cake on the menu" / name / note (§55) | the turntable (§52.7), 260 wide, 26:19 | "Bake it" ("Bake them" when more than one is new; the sheet shows the first) |
| Pause | "Level N" / "Paused" | toggles Sound ("Clinks, whooshes and chimes"), Vibration | Resume · How to play · Restart level · Back to the bakery |
| How to play | "How to play" / "Sort the slices" | six rows (title + text): "Drag a plate onto the counter" / "Any empty spot will do. You get three plates at a time, and three more when they are all down."; "Slices of the same cake fly together" / "When plates touch side by side (not corner to corner), each kind of cake gathers on the plate that can hold the most of it. Empty plates are cleared away."; "Six slices make a whole cake" / "A whole cake is served and counts toward the order at the top. Bake the number on the order to win."; "Keep space free" / "If the counter fills up, use the hammer to clear a plate, undo, or start again."; "Boosters" / "Undo takes back a plate (3 per try). The hammer clears one plate. New plates swaps the ones in your tray."; "Hard levels" / "Levels 5 and 10 of every ten are harder, with cake stands in the way. They pay 30 and 60 coins." | Got it |
| Win | "Level N complete" (hard: "Hard level beaten", super: "Super hard level beaten") / title by tier: super "Showstopper.", hard "That was a tough bake.", else `["Order up!", "Fresh out of the oven.", "Sweet.", "Counter cleared."][n mod 4]` | chips (icon 40×34 + count) for each cake baked this level; coins "+N" (26 display) with " incl. 5 for no boosters" | "Next level" ("Next: hard level N+1" / "Next: super hard level N+1" in hard/super style) · "Back to the bakery"; not dismissable |
| Restart | "Level N" / "Start this level again?" / "The counter is cleared and you get a fresh set of plates." | | Restart · Keep playing |
| Booster buy | §49.5 | | |

### 54.5 Floats

"{Name}!" floats as Paint Sort's float label (§19.5) with an 18 display size
(24 for combos), coloured as §52.5, at the cake.

---

## 55. Cakes and strings

### 55.1 The ten cakes (`Cakes.asset`)

Layers run bottom to top as `colour share-of-height`.

| # | Name | Unlocks | Top | Side (style) | Layers | Pattern | Topping | Piping |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Strawberry | 1 | #FF8DB3 | #FF9BBD (frosted) | #FFE6AE .30 · #FFFFFF .09 · #E8364F .07 · #FFE6AE .30 · #FF8DB3 .24 | glaze | strawberry | #FFFFFF |
| 1 | Chocolate | 1 | #5E2F1A | #55291A (frosted, drip #3B1A0C) | #74402A .32 · #2F150A .10 · #74402A .32 · #5E2F1A .26 | swirl | choc | none |
| 2 | Lemon | 1 | #FFDF45 | #FFF0A8 (bare) | #FFF0B0 .30 · #FFCB12 .08 · #FFFBEA .08 · #FFF0B0 .30 · #FFDF45 .24 | glaze | lemon | #FFFBEA |
| 3 | Matcha | 3 | #8DC35F | #7DB451 (frosted) | #BCDB8E .30 · #F8F4E4 .10 · #BCDB8E .30 · #8DC35F .30 | dust | leaf | #F8F4E4 |
| 4 | Blueberry | 5 | #A887EC | #9878E2 (frosted) | #F6E7C9 .30 · #5B3FA8 .08 · #ECE3FF .08 · #F6E7C9 .30 · #A887EC .24 | none | berries | #ECE3FF |
| 5 | Birthday | 8 | #7BCFF5 | #68C2EC (frosted) | #FFF3D2 .30 · #FFFFFF .10 · #FFF3D2 .30 · #7BCFF5 .30 | sprinkles | candle | #FFFFFF |
| 6 | Mango | 12 | #FFA22C | #FFB651 (bare) | #FFE2A4 .30 · #FF9C1A .08 · #FFF5E0 .08 · #FFE2A4 .30 · #FFA22C .24 | glaze | cubes | none |
| 7 | Cookies & Cream | 16 | #F6F2EB | #3B3431 (bare) | #3B3431 .28 · #F6F2EB .12 · #3B3431 .28 · #F6F2EB .32 | crumbs #2B2523 | cookie | none |
| 8 | Red Velvet | 21 | #FFF5EC | #B5172D (bare) | #B5172D .30 · #FFF5EC .10 · #B5172D .30 · #FFF5EC .30 | crumbs #C31D35 | raspberry | none |
| 9 | Caramel | 27 | #D9933A | #CA852F (frosted, drip #9C5713) | #F2D59B .30 · #B86A1C .08 · #F2D59B .30 · #D9933A .32 | drizzle #8A4A10 | nut | none |

Notes (shown on the new-cake sheet): 0 "Pink buttercream, vanilla sponge with
jam, and a berry on every slice." · 1 "Dark sponge, ganache dripping down the
side, a square of chocolate on top." · 2 "A bare-sided sponge with lemon curd,
bright glaze and a candied wedge." · 3 "Green tea sponge dusted with matcha, a
swirl of cream and a tea leaf." · 4 "Lavender cream over berry jam, crowned with
fresh blueberries." · 5 "Sky-blue frosting, rainbow sprinkles and a candle on
every slice." · 6 "A bare-sided sponge with mango cream, glazed and topped with
fruit." · 7 "Black cookie sponge, white cream, crumbs and a whole cookie." ·
8 "Deep red sponge, cream cheese frosting, red crumbs and a raspberry." ·
9 "Golden caramel coat with drips, a salty drizzle and a hazelnut."

Cakes are told apart by more than colour: topping silhouette, frosted or bare
sides, layer stripes in the cut faces and the top pattern. Keep all four when
adjusting colours.

In Unity each row also holds the cake's `Slice` prefab and `Ink` colour (§51.3).
A slice's look comes from its model. The colours in this table drive the crumbs,
sparkles, shards and float text, and they are the design the models follow.

### 55.2 Strings (`StringTable` scope `CakeSort`)

Everything quoted in §46–§54, plus: board title "Cake Sort"; tagline "Slide
plates together until every slice joins a whole cake."; statuses (§56.1);
lobby intro line "Drag plates of cake slices onto the counter. Matching slices
fly together into whole cakes."; toasts "Nothing to undo", "No plates on the
counter", "Wait for the slices to settle", "Not enough coins ({price} needed)".

---

## 56. Save section, probe and analytics

### 56.1 Save (`games["cake-sort"]`)

```json
{
  "level": 14, "coins": 240,
  "inv": { "hammer": 2, "refresh": 2 },
  "stats": { "won": 13, "cakes": 41, "hard": 1, "super": 1 },
  "baked": { "0": 9, "1": 7, "2": 8, "3": 5 },
  "seen": { "0": true, "1": true, "2": true, "3": true },
  "tips": {},
  "skill": { "mu": 3.91, "sd": 0.52, "n": 17 },
  "tries": { "n": 14, "fails": 1 },
  "cur": {
    "n": 14, "h": 2.85, "flv": [0, 2, 3, 4],
    "cells": [null, [0, 0, 3], -1, null, "…20 entries"],
    "tray": [[2, 2], null, [4]],
    "rs": -1404925724, "baked": 3, "bakedBy": { "0": 2, "3": 1 },
    "moves": 9, "undos": 3, "clean": true, "minFree": 11, "observed": false
  }
}
```

`cur` is written after every plate, undo, hammer and new-plates; `cells` holds
`null`, `-1` (a stand) or a plate list. Undo snapshots are not saved (an undo
after a restart of the app is not offered). Defaults: level 1, 100 coins,
`inv {hammer 2, refresh 2}`, skill from §4.9.

**Board status** (`CakeSortStatus`): `level > 1 ? "Level {level} · {cakes}
cakes" : "New · 10 cakes to discover"`; Cta `level > 1 || cur != null ?
"Continue" : "Play"`.

### 56.2 Probe and simulation CLIs

- `Playbox.Editor.CakeProbeCli.Run -from 1 -to 60 -runs 16`: the typical curve
  (no model), the same columns as `node playbox/tools/cake-probe.mjs`.
- `Playbox.Editor.AdaptiveSimCli.Run -game cake -levels 60`: the adaptive
  simulation (§4.9) with the two bots, printing the table of
  `node playbox/tools/adaptive-sim.mjs cake 60`.

### 56.3 Analytics events

`level_start` (level, tier, heat, mu, sd, kinds, goal, stands),
`level_complete` (level, tier, heat, plates, clean, reward, min_free),
`level_fail` (level, heat, plates, baked), `level_restart` (level, plates),
`cake_baked` (kind, combo), `cake_unlocked` (kind), `booster_used` (id, level),
`booster_bought` (id, price), `skill_update` (§4.9). Each carries `game`.

---

# Part VI (Cake Sort): tests, milestones and generated assets

## 57. Tests (Cake Sort)

**EditMode: Cake Sort**
- `CakeEngineTests`: every value in Appendix E: the RNG stream and `SeedFor`,
  the typical-curve table and `Spec(n, h)` rows, `NewLevel` counters and trays
  for the listed levels and heats, `Place` steps, the six `Resolve` cases A–F,
  the `MakePlate` sequence and the `Playout` results.
- `CakeRulesTests`: over 200 seeded bot playouts of levels 1–60 at random heats,
  after every `Place` no plate holds more than 6 slices, no plate holds 6 of one
  cake, slices never move between diagonal cells, the counts of each cake
  (counter + tray + baked × 6) never change except by baking, and `IsStuck` is
  true exactly when no cell is empty and the order isn't filled.
- `CakeQueueTests` (the step queue on a fake clock): three placements committed
  50 ms apart play their steps in commit order; when the queue drains, every
  cell's visual plate equals the state; `StopPlayback` mid-step stops further
  steps, and the old timer firing after it does nothing (`gen` guard); a tray
  plate cannot be dropped on a cell a mover is headed to.

**PlayMode: Cake Sort**
- Live input: on level 3 at a fixed heat, drop the three tray plates 100 ms
  apart while the first one's slices are still flying: all three land, none is
  refused, the counter matches the engine when the queue drains, and the order
  card counts every cake.
- Win: level 1 along the tutorial path: the coach steps run in order, the win
  sheet opens after the last cake lands, coins go 100 → 115, level 2 unlocks,
  `skill.n = 1`.
- Full counter: with `skill = {4, 0.5}`, fill the counter on level 12: the
  full-counter bar appears once the queue drains, one lost try is read, and
  Restart makes a new attempt at a lower heat.
- Boosters during a sort: the hammer is refused with "Wait for the slices to
  settle"; undo and new plates are refused while a plate is in flight.
- Resume: place 3 plates, reload the scene, Continue: same counter, tray and
  heat.

**EditMode: Cake Sort assets** (new)
- `CakeAssetTests`: the six checks of §51.11 for all ten GLBs and prefabs.
- `CakeFrameTests`:
  - `Quaternion.Euler(0, a·Rad2Deg, 0) * Vector3.right` equals
    `(cos a, 0, −sin a)` for a = 0, π/3, 7π/6.
  - The world→screen conversion of §47 maps a counter point at web angle `a`
    from a cell centre to the screen offset `(cos a, sin a·SQ)·r` (y down)
    through the game camera.
  - A slice prefab at start angle `SLOT0 = 7π/6` covers web angles 210°–270°,
    from the back left to straight back on screen, like slot 0 in `drawSlices`.

**PlayMode: Cake Sort visuals** (new)
- Slots and spin: on level 1, along the tutorial (Appendix E's first `Place`),
  the flying slices land in the destination plate's slots 3–5, after its own
  three in slots 0–2. The plate turns clockwise on screen while they fly in
  (§52.3), like the web.
- Birthday flame: a served Birthday cake's flames flicker (`_Flicker` varies),
  while the counter's don't.

---

## 58. Milestones and acceptance checks (Cake Sort)

Build in this order. Each row's checks must pass before the next starts.

| # | Milestone | Done when |
| --- | --- | --- |
| CS1 | Cake Sort engine port, bots, `CakeProbeCli`, `AdaptiveSimCli -game cake` | CakeEngine and CakeRules tests pass; the probe prints the same table as `cake-probe.mjs`; the simulation's bot rows are within ± .05 of §0.7 |
| CS2 | Cake Sort textures and audio: cloth, doily, tray, cupcake, hand; the `cs_*` clips | The Cake Sort PNGs of §59 and the §53.1 WAVs regenerate byte-identically; AudioSynth tests pass for the `cs_*` group; audition every sound |
| CS3 | The 3D counter: pitched camera with the §47 axes, counter, plates, stands with cloches, the ten slice prefabs with `CakeSlice.shader` and `CakeLook` (§51), `CakeIconRig`, the board art (§0.6) | CakeAsset and CakeFrame tests pass. Each cake, whole on a plate, reads the same as its `renders/lod_game_cake.png`. Levels 1, 5, 20 and 45 side by side with web screenshots at 390 × 844: plates within 4 dp, slices in the right slots, cloth, doilies and tray match after Linear tuning. Every cake renders in the collection, in both themes. A full counter (20 plates) holds 60 fps on a mid-range Android |
| CS4 | Input, the step queue, spinning slice flights, serving to the order card, effects, sounds, haptics | CakeQueue tests and the Live input and Slots-and-spin PlayMode tests pass; 200 rapid random placements leave no visual desync |
| CS5 | Level flow: lobby, menu chips, order card, boosters, tutorial, hard intro, win, new-cake and unlock sheets, save and resume, `CakeDirector` | Cake Sort PlayMode tests pass; the board status shows on the Hub |

---

## 59. Appendix A: generated asset manifest (Cake Sort rows)

All PNGs are RGBA, straight alpha, written to
`Assets/_Project/Textures/Generated/` by `CakeTextureRecipes`.

| File | Size | Import | Contents |
| --- | --- | --- | --- |
| `cs_gingham.png` | 64×64 | Default, Repeat | §51.9 |
| `cs_doily.png` | 256×256 | Sprite | §51.9 |
| `cs_tray_wood.png` | 512×128 | Sprite, 9-slice, sRGB | §51.9 |
| `cs_cupcake.png` | 128×160 | Sprite | §51.9 |
| `cs_hand.png` | 128×128 | Sprite | §51.9 |
| `tex_board_cake_sort_light.png`, `tex_board_cake_sort_dark.png` | 1600×1000 | Sprite, Clamp, sRGB, no mipmaps | Cake Sort's board art, §0.6 (rendered by `CakeCardArtRig`, or live) |
| Icon `cake-sort` (`IconSet.asset`) | 128×128 | Sprite | Cake Sort's icon in §7.3 |

**Removed** from the plan's manifest: `cs_pattern_<cake>.png`,
`cs_top_<kind>.png`, `cs_pipe.png` and `cs_flame.png`. The slices carry them
(§51).

**Delivered, not generated:** the ten slices in `Assets/_Project/Art/CakeSort/`
(§51.1).

**Runtime-generated (not files):** plates, stands, cloche domes and the counter
(§51.8), and the cake icon RenderTextures (§51.10).

Audio files: §53.1, written to `Assets/_Project/Audio/Generated/` by
`GenerateAudio`, like the other games.

---

## 63. Appendix E: Cake Sort fixtures

Produced by the web engine (`cake-sort.html`, between the engine markers) with
the Node approach in §0.1 ("Making extra fixtures"). Counters list cells by index (`row × 4 + col`); in the
`newLevel` grids `.` is empty, `#` a cake stand, and a list a plate (bottom slot
first). Steps are `{d, f, from: [[cell, slices]], cake, emptied}`.

```
rngNext from {s: SeedFor(1,11)|0} first 3: 0.824639473343, 0.302575792884, 0.983872138895
SeedFor(7, 11 + 20*heat 2.35 → 58) = 3783001627  as int32 -511965669

baseHeat / heatRange / spec(n) at the typical curve:
   n  heat   range          tier K goal stands pre  mix    mix3   help   big    reward
   1     0 [0, 7.4]          0  3    3      0   0   0.28      0   0.64   0.12     10
   2   0.4 [0, 7.4]          0  3    7      0   0  0.308      0  0.616   0.14     10
   3   0.8 [0, 7.4]          0  4    8      0   2  0.336      0  0.592   0.16     10
   4   1.2 [0, 7.4]          0  4    9      0   2  0.364      0  0.568   0.18     10
   5   2.4 [0, 7.4]          1  4   10      1   3  0.413  0.028  0.526  0.215     30
  10   3.4 [0, 7.4]          2  4   11      2   3  0.448  0.063  0.496   0.24     60
  14   1.8 [0, 8]            0  4   10      0   3  0.406  0.021  0.532   0.21     10
  20     4 [0, 8]            2  5   13      2   4   0.49  0.105   0.46   0.27     60
  27   2.1 [0, 8.6]          0  4   11      0   3  0.427  0.042  0.514  0.225     10
  45   4.8 [0, 9.8]          1  5   15      1   5  0.581  0.196  0.382  0.335     30
  90   8.2 [2.3, 10]         2  7   21      3   6    0.7    0.3    0.3  0.455     60
 150   8.2 [2.3, 10]         2  7   21      3   6    0.7    0.3    0.3  0.455     60

spec(n, h):
spec(20, 0)     heat 0 tier 2 K 3 goal 6 stands 2 pre 2 mix 0.28 mix3 0 help 0.64 big 0.12
spec(20, 3.5)   heat 3.5 tier 2 K 4 goal 12 stands 2 pre 4 mix 0.455 mix3 0.07 help 0.49 big 0.245
spec(20, 6)     heat 6 tier 2 K 6 goal 17 stands 2 pre 6 mix 0.63 mix3 0.245 help 0.34 big 0.37
spec(20, 12)    heat 10 tier 2 K 7 goal 24 stands 4 pre 6 mix 0.7 mix3 0.3 help 0.3 big 0.5
spec(45, 2.5)   heat 2.5 tier 1 K 4 goal 10 stands 1 pre 3 mix 0.42 mix3 0.035 help 0.52 big 0.22
spec(45, 7.25)  heat 7.25 tier 1 K 6 goal 20 stands 2 pre 6 mix 0.7 mix3 0.3 help 0.3 big 0.4325
spec(50, 1)     heat 1 tier 2 K 3 goal 6 stands 2 pre 2 mix 0.28 mix3 0 help 0.64 big 0.12

newLevel(n, h): menu, counter (row by row, . empty, # stand, slices bottom-up), tray
newLevel(1): heat 0 flv [0,1,2] goal 3
   . . . .
   . . . .
   . [0,0,0] . .
   . . [1,1,1,1] .
   . . . .
   tray [[0,0,0],[2,2,1],[2,2]]   rs.s 472628284
newLevel(2): heat 0.4 flv [0,1,2] goal 7
   . . . .
   . . . .
   . . . .
   . . . .
   . . . .
   tray [[1,2],[2,2,1],[2,2,2]]   rs.s -169813964
newLevel(3, 1.2): heat 1.2 flv [0,1,2,3] goal 9
   . . . .
   [0] . [0] .
   . . . .
   . . . .
   . . . .
   tray [[2,2,2],[2],[0,0]]   rs.s -472808503
newLevel(5): heat 2.4 flv [0,1,3,4] goal 10
   . [0,0,0] . .
   . . [4,4,4,4,4] .
   [4,4,4] . . .
   . # . .
   . . . .
   tray [[0,0],[1,4],[4,4]]   rs.s -1404925724
newLevel(10): heat 3.4 flv [1,3,4,5] goal 11
   . # . .
   . . # .
   [4,4] . . .
   . . . .
   . [4,4,4] . [1,1,4]
   tray [[4,4],[4,4],[1,4]]   rs.s -158702755
newLevel(27, 5.4): heat 5.4 flv [1,2,3,4,8,9] goal 17
   . [1,2,2,8] . .
   . . . [2]
   [1,1,2] # . [1,4]
   . [3,3,4,1] . .
   . . . .
   tray [[9],[1],[8]]   rs.s -1973168133

place() on level 1: tray 0 onto cell 10
   steps [{"d":10,"f":0,"from":[[9,3]],"cake":true,"emptied":[9]}] dealt false baked 1

resolve(cells, start) on constructed counters (index = row*4 + col):
A: three plates share strawberry: start 6
   before {"5":[0,0],"6":[0,1],"9":[0,0,0]}
   steps  [{"d":5,"f":0,"from":[[6,1],[9,3]],"cake":true,"emptied":[9]}]
   after  {"6":[1]}
B: two plates swap two cakes: start 6
   before {"5":[0,0,1,1,1],"6":[0,0,0,1,1]}
   steps  [{"d":6,"f":0,"from":[[5,1]],"cake":false,"emptied":[]},{"d":5,"f":1,"from":[[6,2]],"cake":false,"emptied":[]},{"d":6,"f":0,"from":[[5,1]],"cake":false,"emptied":[]}]
   after  {"5":[1,1,1,1,1],"6":[0,0,0,0,0]}
C: a full mixed plate frees room: start 0
   before {"0":[0,1],"1":[1,1,1,1,1,0]}
   steps  [{"d":0,"f":0,"from":[[1,1]],"cake":false,"emptied":[]},{"d":1,"f":1,"from":[[0,1]],"cake":true,"emptied":[]}]
   after  {"0":[0,0]}
D: a chain across three plates: start 5
   before {"4":[2,2,2],"5":[2,3],"6":[3,3,3,3],"7":[2]}
   steps  [{"d":6,"f":3,"from":[[5,1]],"cake":false,"emptied":[]},{"d":4,"f":2,"from":[[5,1]],"cake":false,"emptied":[5]}]
   after  {"4":[2,2,2,2],"6":[3,3,3,3,3],"7":[2]}
E: no shared cake: start 9
   before {"8":[0,1],"9":[2,3]}
   steps  []
   after  {"8":[0,1],"9":[2,3]}
F: corner neighbours never trade: start 5
   before {"0":[4,4,4],"5":[4,4,4]}
   steps  []
   after  {"0":[4,4,4],"5":[4,4,4]}

makePlate sequence: level 20 at its typical heat, counter as dealt, five plates from its rs
   [[6,6,6,6,6],[1,1,1,3],[6,6,3],[6,6,6],[5,5,5,6,6]]   rs.s after 1131314668

playout(n, skill, seed, h) → plates used, -1 a loss:
   playout(12, 0, 1234) = 27
   playout(12, 1, 1234) = 17
   playout(30, 0, 99, 5) = -1
   playout(30, 1, 99, 5) = 38
```

---
