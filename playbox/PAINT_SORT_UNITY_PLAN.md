# Paint Sort in Unity: implementation plan

This plan is for an AI coding agent building **Paint Sort** (a water/paint sort
puzzle) in Unity. It covers the architecture, the code hierarchy, the full
engine port, and every asset the agent must **generate through code**: meshes,
shaders, textures, paintings, particles, sounds, prefabs, scenes and UI layouts.

The reference implementation is the web prototype in this repo, and the agent
gets its source alongside this plan (§0). Where the plan gives code, port it
exactly; where it gives numbers, use them as written.

---

## 0. Using this plan with the HTML source

### 0.1 Files the agent receives

| File | What it is |
| --- | --- |
| `playbox/src/games/paint-sort.html` | The whole game: CSS, engine, painting, vial drawing, sounds, game logic, lobby. **The main reference.** |
| `playbox/src/shell.html` | The hub: save store, the Web Audio synth (`tone`, `noise`, `bell`, compressor), sheets, toasts, settings, home screen. |
| `playbox/tools/probe.mjs` | Runs the engine in Node and prints the difficulty table. Use it to produce extra golden fixtures. |
| `playbox/index.html` | Built output of the two sources in one file. Open it in a browser to see and hear the target; don't read it for code (it duplicates the sources). |

### 0.2 Which one wins

1. **This plan wins** for everything it specifies: architecture, Unity
   settings, the y-up coordinate conversion, units, the C# code, shaders,
   generated asset specs, file names, save format and tests. The web version
   draws everything live on a 2D canvas; the plan deliberately replaces that
   with meshes, shaders, pre-rendered audio clips and generated textures.
2. **The HTML wins** for behaviour or look that the plan doesn't pin down (an
   animation detail, a colour in an edge case, a string). Port what the HTML
   does, converted to the plan's conventions.
3. **For engine output, the HTML is ground truth.** The golden fixtures
   (Appendix B) were produced by it. If the C# port and the plan's C# listing
   ever disagree with the HTML's output, match the HTML and report the
   difference.

### 0.3 Where each part lives in the HTML

Everything below is in `paint-sort.html` unless marked `shell`. Find code by
name; line numbers will drift.

| Plan section | HTML source |
| --- | --- |
| §5 Engine | Between the `// @engine-start` and `// @engine-end` markers: `rng32`, `seedFor`, `shuffle`, `RAMP`, `PICK`, `K_CAP`, `spec`, `isFull`, `isSolved`, `runLen`, `listMoves`, `applyMove`, `heur`, `keyOf`, `solve`, `playout`, `rateMove`, `playoutSkilled`, `deal`, `generate`, `probe` |
| §5.9 Painting composition | `makeShape`, `buildArt` |
| §6 Level state and rules | inside `mount`: `freshLevel`, `hydrate`, `persist`, `canPour`, `revealTops`, `bandsOf`, `refreshDone`, `pour`, `finishPour`, `celebrate`, `onSolved`, `winSequence` |
| §6.4 Input | `tapVial`, `hitVial`, `onKey`, the `pointerdown` listener |
| §6.5–6.7 Boosters, dead ends, tutorial | `undo`, `hint`, `addVial`, `restart`, `buy`, `checkStuckSoon`, `checkStuck`, `showStuck`, `coach` |
| §7 Layout | `layout` |
| §8 Vial geometry and drawing | `areaBelow`, `levelFor`, `makeGeom`, `capAt`, `angleFor`, `worldPoly`, `axisAt`, `interiorPath`, `outlinePath`, `drawVial`, `drawCork`, `vialOpts` |
| §8.9 Motion | `step` (lift, shake, wobble, glide), `restPose`, `busy` |
| §9 Pour | `pour`, `pourPose`, `srcUnits`, `poured`, `trimTop`, `addTop`, `surfaceY` |
| §10–11 Stream, particles, hint pointer | `draw` (stream, particles and pointer sections), `step` (splash spawning), `sparkle` |
| §12 Paintings | `tooth`, `brushIn`, `drawArt`, `paintCanvas` |
| §13 Sound | `makeSfx` (every game sound); `shell`: the `audio` object (`tone`, `noise`, `bell`, compressor settings) |
| §15 UI | `TEMPLATE` (markup), the `<style>` block (sizes, colours, animations), `renderLobby`, `renderRoad`, `showWin`, `intro`, `menu`, `howTo`, `updateHud`; `shell`: `sheet`, `toast`, `openSettings`, `renderHome` |
| §15.1 Card art | `drawCard` |
| §16 Theme and pigments | CSS custom properties at the top of both files; `PIGMENTS`, `mix`, `glyph` |
| §17 Save | `persist`, `hydrate`; `shell`: `store` |

### 0.4 Converting while you read

- **Canvas y points down; Unity y points up.** Every board formula in this plan
  is already converted. When reading one straight from the HTML, flip the sign
  of every y offset and of every rotation angle.
- **Canvas pixels = Unity world units (dp).** Velocities in the HTML are px/ms:
  multiply by 1000 for units per second, and by 1,000,000 for accelerations.
- **Sound:** the web synthesises every sound live. Unity pre-renders clips
  (§13) and plays the glug train as scheduled clips at varying pitch; the
  recipes in §13.4 are `makeSfx` translated.
- **Don't port the web-only parts:** Google Fonts links, `localStorage`,
  `history.replaceState` and the `#hash` deep link, `window.claude.hot`,
  `ResizeObserver`, DOM building, and the `window.__ps` debug hooks (the Unity
  equivalents are the tests and the probe CLI).

### 0.5 Making more golden fixtures

`probe.mjs` shows how to run the engine in Node: it reads `paint-sort.html`,
extracts the text between the engine markers, and evaluates it with `node:vm`.
Use the same approach to dump any value you want to test against, for example:

```js
// node dump.mjs 42
import { readFileSync } from 'node:fs'; import vm from 'node:vm';
const src = readFileSync('playbox/src/games/paint-sort.html', 'utf8');
const eng = src.match(/\/\/ @engine-start[^\n]*\n([\s\S]*?)\/\/ @engine-end/)[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(eng + '\nthis.e = { generate, solve, spec };', ctx);
const g = ctx.e.generate(+process.argv[2]);
console.log(JSON.stringify({ vials: g.vials, palette: g.palette, hidden: g.hidden, len: g.len, fail: g.fail }));
```

`node playbox/tools/probe.mjs 1 60` prints the difficulty table; the C# probe
CLI (§19.3) must print the same numbers.

---

## Contents

0. Using this plan with the HTML source
1. Ground rules for the agent
2. Project setup
3. Units and coordinate conventions
4. Code hierarchy
5. Engine (pure C#, full source)
6. Level state and game rules
7. Board layout
8. Vials: geometry, meshes, liquid shader
9. The pour animation
10. The paint stream
11. Particles
12. Paintings
13. Sound (synthesised at edit time)
14. Haptics
15. UI layouts
16. Theme, pigments and strings
17. Save system
18. Threading and performance
19. Editor tooling (generators, scene builder, balance probe)
20. Tests
21. Milestones and acceptance checks
22. Appendix A: generated asset manifest
23. Appendix B: golden fixtures

---

## 1. Ground rules for the agent

1. **Everything in this plan is generated by code.** Textures and audio are
   written to disk by editor scripts (`Playbox/Generate/...` menu items), and
   meshes, paintings and particle geometry are built at runtime. The game must
   run with nothing else imported.
2. **The engine must match the web prototype bit for bit.** Level *n* must
   produce the same board, palette and hidden layers in Unity as on the web.
   §5.10 lists every JavaScript-to-C# trap, and Appendix B has golden values the
   tests must reproduce.
3. **Keep the engine pure.** `Playbox.PaintSort.Engine` has no `UnityEngine`
   references, so it runs in EditMode tests, on worker threads, and from the
   command-line probe.
4. **Build in milestone order (§21).** Don't start a milestone until the
   previous one's acceptance checks pass.
5. Times in this document are **milliseconds** unless marked `s`. Distances
   marked `w` are multiples of the current vial width.

---

## 2. Project setup

| Setting | Value |
| --- | --- |
| Unity | 6 LTS (6000.0.x) |
| Render pipeline | URP, 2D Renderer |
| Colour space | **Gamma** (alpha blending then matches the browser exactly; all hex colours in this doc are sRGB and are passed to shaders unconverted) |
| Anti-aliasing | URP asset MSAA 4x |
| Orientation | Portrait only |
| Target frame rate | `Application.targetFrameRate = 60` |
| Platforms | Android (min API 24, IL2CPP, ARM64), iOS 13+ |
| Packages | `com.unity.render-pipelines.universal`, `com.unity.inputsystem`, `com.unity.ugui` (includes TextMeshPro), `com.unity.nuget.newtonsoft-json`, `com.unity.test-framework` |
| Layers | `Board` (8), `Painting` (9), `CardArt` (10) |
| Sorting layers | `Background`, `Board`, `Fx` |

Canvas Scaler on every UI canvas: *Scale With Screen Size*, reference
**390 × 844**, match **0.5**. One canvas unit is then one "dp", the same as one
CSS pixel in the web prototype, so every UI size in this document can be used
directly.

---

## 3. Units and coordinate conventions

- **Board world units = dp.** The board camera is orthographic with
  `orthographicSize = (Screen.height / canvas.scaleFactor) / 2`, so one world
  unit equals one canvas unit. Every pixel number from the web prototype (layout,
  particle speeds, stroke widths) is therefore reused 1:1 as world units.
- **Unity is y-up; the web canvas was y-down.** This document already gives
  board formulas in y-up form. "Above" means larger y.
- **Vial local space:** origin at the centre of the mouth, body extending to
  negative y. Meshes are built for width `w = 1` and the vial transform is scaled
  uniformly by `w`.
- **Tilt:** `θ ≥ 0` is how far a vial is tipped. Its z-rotation is
  `-dir * θ` (radians), where `dir = +1` when pouring to the right (clockwise)
  and `-1` when pouring to the left.
- **Painting (art) space:** 400 × 300, **y-down**, exactly like the web. The
  art builder works in this space; mesh builders convert with `y' = 300 - y`.

---

## 4. Code hierarchy

```
Assets/_Project/
├─ Scripts/
│  ├─ Core/                                   asmdef Playbox.Core
│  │  ├─ Boot/Bootstrap.cs                    creates Services, loads save, opens Hub scene
│  │  ├─ Boot/Services.cs                     DontDestroyOnLoad holder; static access to the services below
│  │  ├─ Games/GameDefinition.cs              ScriptableObject: id, title, tagline, sceneName, card art prefab
│  │  ├─ Games/GameRegistry.cs                ScriptableObject: list of GameDefinition
│  │  ├─ Games/IGameStatus.cs                 string Status(JObject save) for the home card chip
│  │  ├─ Save/SaveService.cs                  load/save playbox.json, debounced, atomic
│  │  ├─ Save/SaveData.cs                     root DTO (settings, last game, per-game JObject)
│  │  ├─ Settings/SettingsService.cs          sound, haptics, theme; raises Changed
│  │  ├─ Theme/ThemeService.cs                resolves Auto/Light/Dark; raises ThemeChanged
│  │  ├─ Theme/ThemePalette.cs                ScriptableObject of colour tokens (light + dark)
│  │  ├─ Theme/DarkModeProbe.cs               Android JNI + iOS bridge for "is system dark"
│  │  ├─ Audio/SfxPlayer.cs                   16-voice pool, PlayScheduled, volume/pitch
│  │  ├─ Audio/SfxLibrary.cs                  ScriptableObject mapping SfxId -> AudioClip[]
│  │  ├─ Audio/SfxId.cs                       enum of every generated clip family
│  │  ├─ Haptics/IHaptics.cs                  Pulse(ms), Pattern(long[])
│  │  ├─ Haptics/AndroidHaptics.cs            VibrationEffect via JNI
│  │  ├─ Haptics/IosHaptics.cs                UIImpactFeedbackGenerator via the native bridge
│  │  ├─ Haptics/NullHaptics.cs               editor / unsupported
│  │  ├─ UI/SheetHost.cs                      one bottom sheet at a time + scrim
│  │  ├─ UI/SheetBuilder.cs                   builds sheet content from a spec (eyebrow, title, sub, body, actions)
│  │  ├─ UI/Toast.cs
│  │  ├─ UI/UiSwitch.cs, UI/SegmentedControl.cs, UI/PressFeedback.cs, UI/SafeAreaFitter.cs
│  │  ├─ UI/ThemedGraphic.cs                  binds a Graphic colour to a theme token
│  │  ├─ UI/UiSkin.cs                         ScriptableObject of sprite slots; unassigned slots use the generated primitives
│  │  ├─ Hub/HubScreen.cs                     home shelf
│  │  ├─ Hub/GameCardView.cs                  card: art RT, title, tagline, status chip, play button
│  │  ├─ Util/Easing.cs                       all easing functions in §9.2
│  │  ├─ Util/MainThread.cs                   queue for results from worker threads
│  │  ├─ Util/RibbonBuilder.cs                polyline -> triangle ribbon mesh (joins, caps, dashes)
│  │  ├─ Util/Triangulator.cs                 ear clipping for simple polygons
│  │  └─ Util/Hex.cs                          "#RRGGBB"/rgba() -> Color
│  ├─ PaintSort/
│  │  ├─ Engine/                              asmdef Playbox.PaintSort.Engine (noEngineReferences: true)
│  │  │  ├─ Move.cs
│  │  │  ├─ Mulberry32.cs                     RNG + Seeds (SeedFor, Shuffle, JsRound)
│  │  │  ├─ Difficulty.cs                     RAMP, PICK, caps, Spec(n)
│  │  │  ├─ LevelSpec.cs
│  │  │  ├─ Rules.cs                          IsFull, IsSolved, RunLen, ListMoves, Apply, Heur, KeyOf
│  │  │  ├─ Solver.cs                         weighted A*
│  │  │  ├─ Playouts.cs                       casual + skilled simulated players, RateMove
│  │  │  ├─ Generator.cs                      Deal, Generate
│  │  │  ├─ GeneratedLevel.cs
│  │  │  ├─ Probe.cs                          difficulty table rows
│  │  │  └─ Art/ArtBuilder.cs                 painting composition (pure, doubles only)
│  │  ├─ Runtime/                             asmdef Playbox.PaintSort (refs Core + Engine)
│  │  │  ├─ PaintSortController.cs            state machine, owns LevelState, wires views
│  │  │  ├─ LevelState.cs                     ids model, history, reveal set (§6)
│  │  │  ├─ LevelCache.cs                     background generation of n and n+1
│  │  │  ├─ Economy.cs                        constants (§6.8)
│  │  │  ├─ BoardLayout.cs                    rows, w, slot positions (§7)
│  │  │  ├─ VialGeometry.cs                   polygon, cap table, AreaBelow, LevelFor, AngleFor (§8.1)
│  │  │  ├─ VialMeshes.cs                     interior, outline, rim, highlights, shadow meshes (§8.2)
│  │  │  ├─ VialView.cs                       per-vial motion state + renderer updates (§8.5–8.9)
│  │  │  ├─ LiquidBands.cs                    bands -> shader arrays (§8.4)
│  │  │  ├─ SymbolLayer.cs                    '?' and colour-blind glyph sprites (§8.6)
│  │  │  ├─ PourAnimation.cs                  one pour's timeline and poses (§9)
│  │  │  ├─ StreamRenderer.cs                 paint stream ribbon (§10)
│  │  │  ├─ FxPool.cs                         droplets, sparks, splats (§11)
│  │  │  ├─ HintPointer.cs                    arrow + dashed target outline
│  │  │  ├─ PaintingRenderer.cs               renders an ArtBuilder result into a RenderTexture (§12)
│  │  │  ├─ DeadEndWatcher.cs                 debounced solver check (§6.6)
│  │  │  ├─ HintService.cs                    solver-backed hint (§6.5)
│  │  │  ├─ Tutorial.cs                       level-1 coach text + pointer (§6.7)
│  │  │  ├─ BoardInput.cs                     taps, keyboard (§6.4)
│  │  │  ├─ PaintSortSfx.cs                   game events -> SfxPlayer calls (§13.6)
│  │  │  ├─ PaintSortHaptics.cs               game events -> haptic patterns (§14)
│  │  │  └─ PaintSortStatus.cs                IGameStatus for the home card
│  │  └─ UI/                                  asmdef Playbox.PaintSort.UI
│  │     ├─ LobbyScreen.cs                    wordmark, next painting card, level road, play button
│  │     ├─ LevelRoadGraphic.cs               custom Graphic drawing the sawtooth road (§15.4)
│  │     ├─ PlayHud.cs                        top bar, level + tier badge, coins
│  │     ├─ BoosterBar.cs, BoosterButton.cs
│  │     ├─ PigmentDots.cs
│  │     ├─ CoachLine.cs
│  │     ├─ StuckBar.cs
│  │     ├─ HardIntro.cs
│  │     ├─ FloatLabel.cs                     pigment name that floats up from a corked vial
│  │     └─ Sheets/WinSheet.cs, PauseSheet.cs, BuySheet.cs, HowToSheet.cs, RestartSheet.cs, MysteryTipSheet.cs, SettingsSheet.cs
│  ├─ Editor/                                 asmdef Playbox.Editor (Editor only; refs Core, Engine, Runtime)
│  │  ├─ Audio/Synth.cs                       offline Web-Audio-style synth (§13.2)
│  │  ├─ Audio/Biquad.cs
│  │  ├─ Audio/WavWriter.cs
│  │  ├─ Audio/SfxRecipes.cs                  every sound, as code (§13.4)
│  │  ├─ Audio/GenerateAudio.cs               menu: Playbox/Generate/Audio
│  │  ├─ Audio/AudioImportRules.cs            AssetPostprocessor for generated WAVs
│  │  ├─ Textures/Raster.cs                   SDF rasteriser: circles, rounded rects, polygons, capsules
│  │  ├─ Textures/TextureRecipes.cs           every texture, as code (§12, §8.6, §11, Appendix A)
│  │  ├─ Textures/GenerateTextures.cs         menu: Playbox/Generate/Textures
│  │  ├─ Build/PrefabBuilder.cs               menu: Playbox/Build/Prefabs
│  │  ├─ Build/SceneBuilder.cs                menu: Playbox/Build/Scenes
│  │  ├─ Probe/ProbeWindow.cs                 menu: Playbox/Paint Sort/Balance Probe
│  │  └─ Probe/ProbeCli.cs                    -executeMethod entry point
│  └─ Plugins/iOS/PlayboxNative.mm            dark-mode query + impact haptics (§14)
├─ Shaders/
│  ├─ UnlitColor.shader                       flat colour, alpha blend, _Tint via MPB
│  ├─ Liquid.shader                           §8.4
│  ├─ SoftStroke.shader                       ribbon with soft edges (selection glow)
│  ├─ Stream.shader                           §10
│  ├─ BrushReveal.shader                      §12.4 (writes stencil)
│  ├─ StencilColor.shader                     streaks clipped to their shape (§12.5)
│  ├─ Gradient.shader                         vertical two-colour background
│  └─ TintedSprite.shader                     sprites with alpha multiplier (particles, symbols)
├─ Materials/                                 one material per shader; all per-object values go through MaterialPropertyBlock
├─ Textures/Generated/                        written by GenerateTextures (Appendix A)
├─ Audio/Generated/                           written by GenerateAudio (§13.5)
├─ Prefabs/                                   written by PrefabBuilder (§4.1)
├─ Scenes/Boot.unity, Hub.unity, PaintSort.unity   written by SceneBuilder (§4.2)
├─ Config/
│  ├─ GameRegistry.asset
│  ├─ ThemePalette.asset                      values from §16.1
│  ├─ Pigments.asset                          values from §16.2
│  ├─ SfxLibrary.asset                        filled by GenerateAudio
│  └─ UiSkin.asset
└─ Tests/
   ├─ EditMode/                               asmdef Playbox.Tests.EditMode
   └─ PlayMode/                               asmdef Playbox.Tests.PlayMode
```

### 4.1 Prefabs (built by `PrefabBuilder`)

```
Vial.prefab                 VialView, SortingGroup (layer Board)
├─ SelectGlow               MeshRenderer  SoftStroke ribbon along the outline      order -1 (off unless selected)
├─ CompleteGlow             SpriteRenderer fx_glow                                  order -1
├─ GlassBack                MeshRenderer  interior mesh, UnlitColor (--ps-glass)    order 0
├─ Liquid                   MeshRenderer  interior mesh, Liquid                     order 1
├─ Symbols                  SymbolLayer (pooled SpriteRenderers, tex_symbols)       order 2
├─ Highlights               MeshRenderer  two capsules, UnlitColor (--ps-hi)        order 3
├─ Outline                  MeshRenderer  open ribbon, UnlitColor (--ps-edge)       order 4
├─ Rim                      MeshRenderer  rounded rect, UnlitColor (--ps-edge)      order 5
└─ Cork                     SpriteRenderer tex_cork, pivot top-centre               order 6 (inactive until full)

VialShadow.prefab           MeshRenderer ellipse, UnlitColor (--ps-floor), sorting order -10
Stream.prefab               StreamRenderer + MeshRenderer (Stream.shader), sorting order 50
BoardRig.prefab
├─ BoardCamera              Camera: orthographic, culling mask Board, base camera, clear to solid (unused: Backdrop covers it)
├─ Backdrop                 MeshRenderer full-screen quad, Gradient.shader, sorting layer Background
├─ Shadows                  VialShadow × 16 (pooled)
├─ Vials                    Vial × 16 (pooled; active count = vials in level)
├─ Streams                  Stream × 4 (pooled)
├─ Fx                       FxPool (droplets 96, sparks 96, splats 64 SpriteRenderers)
└─ HintPointer              arrow mesh + dashed outline mesh (UnlitColor, accent)
PaintingRig.prefab          at world (10000, 0); layer Painting
├─ PaintingCamera           orthographic size 150, centred on (200,150), culling Painting, disabled (rendered manually)
├─ Ground                   quad 400×300, UnlitColor #F3F0E8
├─ Tooth                    quad 400×300, tex_canvas_tooth tiled 50 × 37.5
└─ Shapes                   ShapeSlot × 12 (Fill + Streaks + Pencil renderers each)
CardArtRig.prefab           at world (20000, 0); layer CardArt; camera -> card RenderTexture (§15.1)
UI prefabs                  Sheet, Toast, GameCard, TopBar, BoosterButton, PigmentDot, StuckBar, HardIntro, FloatLabel
```

### 4.2 Scenes (built by `SceneBuilder`)

| Scene | Contents |
| --- | --- |
| `Boot` | `Bootstrap` object. Creates `Services` (DontDestroyOnLoad: SaveService, SettingsService, ThemeService, SfxPlayer, Haptics, MainThread), loads the save, loads `Hub`. |
| `Hub` | UI canvas with `HubScreen`, `CardArtRig`. |
| `PaintSort` | `BoardRig`, `PaintingRig`, UI canvas (Screen Space - Overlay) with `LobbyScreen` and `PlayScreen` panels, `SheetHost`, `Toast`, and `PaintSortController` wiring it all. |

Navigation: Hub → PaintSort with `SceneManager.LoadSceneAsync(single)`; the
lobby's back button returns to Hub. `SaveData.last` records the game id so the
Hub can say "Welcome back".

---

## 5. Engine (pure C#, full source)

Namespace `Playbox.PaintSort.Engine`. Use `double` everywhere a number is not
an index. Port this code as written; it reproduces the web engine exactly.

### 5.1 `Move.cs`

```csharp
namespace Playbox.PaintSort.Engine
{
    public readonly struct Move
    {
        public readonly int From, To, Count;
        public Move(int from, int to, int count) { From = from; To = to; Count = count; }
        public override string ToString() => $"[{From},{To},{Count}]";
    }
}
```

### 5.2 `Mulberry32.cs` (RNG and seeding)

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.PaintSort.Engine
{
    /// Port of the web rng32(). Bit-exact with the JavaScript version.
    public sealed class Mulberry32
    {
        uint _a;
        public Mulberry32(uint seed) { _a = seed; }
        public double Next()
        {
            unchecked
            {
                _a += 0x6D2B79F5u;
                uint t = (_a ^ (_a >> 15)) * (1u | _a);
                t = (t + ((t ^ (t >> 7)) * (61u | t))) ^ t;
                return (t ^ (t >> 14)) / 4294967296.0;
            }
        }
    }

    public static class Seeds
    {
        /// Port of seedFor(n, salt).
        public static uint SeedFor(int n, int salt)
        {
            unchecked
            {
                uint h = 0x9E3779B9u ^ ((uint)n * 0x85EBCA6Bu) ^ ((uint)(salt + 1) * 0xC2B2AE35u);
                h ^= h >> 16; h *= 0x7FEB352Du;
                h ^= h >> 15; h *= 0x846CA68Bu;
                h ^= h >> 16;
                return h;
            }
        }

        /// Fisher-Yates from the end, exactly like the web shuffle().
        public static void Shuffle<T>(IList<T> a, Mulberry32 r)
        {
            for (int i = a.Count - 1; i > 0; i--)
            {
                int j = (int)(r.Next() * (i + 1));
                (a[i], a[j]) = (a[j], a[i]);
            }
        }

        /// JavaScript Math.round (half rounds up). Never use Math.Round here.
        public static int JsRound(double x) => (int)Math.Floor(x + 0.5);
    }
}
```

### 5.3 `LevelSpec.cs` and `Difficulty.cs`

```csharp
namespace Playbox.PaintSort.Engine
{
    public sealed class LevelSpec
    {
        public int N, Block, Pos, Tier, K, E, Cap, Cands, Reward;
        public double Heat, Mystery, Pick;
    }
}
```

```csharp
using System;

namespace Playbox.PaintSort.Engine
{
    /// The sawtooth. Levels come in blocks of ten: heat climbs, spikes at the 5th
    /// (hard) and 10th (super hard) level, drops back after each spike, and every
    /// block starts BlockStep above the last.
    public static class Difficulty
    {
        public const int Cap = 4;                       // paint units per vial
        public const int MaxColours = 12;
        public const double BlockStep = 1.15;
        public static readonly double[] Ramp = { 0, .45, .9, 1.35, 2.5, .6, 1.05, 1.5, 1.95, 3.6 };
        public static readonly double[] PickAt = { 0, .35, .55, .7, 1, 0, .45, .6, .75, 1 };
        public static readonly int[] KCap = { 10, 11, 12 };   // colour ceiling: normal, hard, super hard

        public static LevelSpec Spec(int n)
        {
            n = Math.Max(1, n);
            int block = (n - 1) / 10, pos = (n - 1) % 10;
            int tier = pos == 9 ? 2 : pos == 4 ? 1 : 0;
            double heat = block * BlockStep + Ramp[pos];
            int k = n == 1 ? 3 : Math.Min(KCap[tier], Seeds.JsRound(3 + heat));
            bool mysteryOn = n >= 13 && (tier > 0 || pos == 2 || pos == 7 || (block >= 6 && pos != 0 && pos != 5));
            double mystery = mysteryOn ? Math.Min(.7, .3 + block * .04 + tier * .12) : 0;
            return new LevelSpec
            {
                N = n, Block = block, Pos = pos, Tier = tier, Heat = heat, K = k, E = 2, Cap = Cap,
                Mystery = mystery, Pick = PickAt[pos],
                Cands = tier == 2 ? 14 : tier == 1 ? 9 : 4,
                Reward = tier == 2 ? 60 : tier == 1 ? 30 : 10
            };
        }
    }
}
```

### 5.4 `Rules.cs`

A board is `int[][]`: one array per vial, bottom to top, values are colour
indices. Arrays are treated as immutable; `Apply` creates new arrays for the two
vials it touches and shares the rest.

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.PaintSort.Engine
{
    public static class Rules
    {
        public static bool IsFull(int[] v, int C)
        {
            if (v.Length != C) return false;
            for (int i = 1; i < C; i++) if (v[i] != v[0]) return false;
            return true;
        }

        public static bool IsSolved(int[][] s, int C)
        {
            foreach (var v in s) if (v.Length > 0 && !IsFull(v, C)) return false;
            return true;
        }

        public static int RunLen(int[] v)
        {
            int c = v[v.Length - 1], k = 1;
            for (int i = v.Length - 2; i >= 0 && v[i] == c; i--) k++;
            return k;
        }

        /// Moves worth considering, in the exact order the web version yields them
        /// (source ascending, then target ascending). Skips pouring a single-colour
        /// vial into an empty one; with prune, tries only the first empty target.
        public static List<Move> ListMoves(int[][] s, int C, bool prune)
        {
            var result = new List<Move>();
            for (int i = 0; i < s.Length; i++)
            {
                var v = s[i];
                if (v.Length == 0 || IsFull(v, C)) continue;
                int c = v[v.Length - 1], k = RunLen(v);
                bool whole = k == v.Length, emptySeen = false;
                for (int j = 0; j < s.Length; j++)
                {
                    if (j == i) continue;
                    var w = s[j];
                    if (w.Length >= C) continue;
                    if (w.Length == 0)
                    {
                        if (whole) continue;
                        if (prune) { if (emptySeen) continue; emptySeen = true; }
                    }
                    else if (w[w.Length - 1] != c) continue;
                    result.Add(new Move(i, j, Math.Min(k, C - w.Length)));
                }
            }
            return result;
        }

        public static int[][] Apply(int[][] s, Move m)
        {
            var ns = (int[][])s.Clone();
            var src = s[m.From];
            int c = src[src.Length - 1];
            var nsrc = new int[src.Length - m.Count];
            Array.Copy(src, nsrc, nsrc.Length);
            var dst = s[m.To];
            var ndst = new int[dst.Length + m.Count];
            Array.Copy(dst, ndst, dst.Length);
            for (int k = 0; k < m.Count; k++) ndst[dst.Length + k] = c;
            ns[m.From] = nsrc; ns[m.To] = ndst;
            return ns;
        }

        /// Runs of colour minus distinct colours; 0 exactly when solved.
        public static int Heur(int[][] s)
        {
            int segs = 0; var seen = new HashSet<int>();
            foreach (var v in s)
            {
                int prev = -1;
                foreach (int c in v) if (c != prev) { segs++; seen.Add(c); prev = c; }
            }
            return segs - seen.Count;
        }

        /// Canonical key: vial order does not matter. Ordinal sort == JS default sort.
        public static string KeyOf(int[][] s)
        {
            var parts = new string[s.Length];
            for (int i = 0; i < s.Length; i++)
            {
                var ch = new char[s[i].Length];
                for (int k = 0; k < ch.Length; k++) ch[k] = (char)(97 + s[i][k]);
                parts[i] = new string(ch);
            }
            Array.Sort(parts, string.CompareOrdinal);
            return string.Join("|", parts);
        }

        public static int[][] Clone(int[][] s)
        {
            var o = new int[s.Length][];
            for (int i = 0; i < s.Length; i++) o[i] = (int[])s[i].Clone();
            return o;
        }
    }
}
```

### 5.5 `Solver.cs` (weighted A*)

The heap must be ported exactly; a different heap changes tie-breaking, which
changes path lengths and which candidates survive the node budget.

```csharp
using System.Collections.Generic;

namespace Playbox.PaintSort.Engine
{
    public sealed class SolveResult
    {
        public bool Ok;            // a solution was found
        public List<Move> Path;    // null unless Ok
        public int Nodes;
        public bool Exhausted;     // true with Ok=false means the position is PROVEN dead
    }

    public static class Solver
    {
        sealed class Node { public int[][] S; public int G; public double F; public Node Parent; public Move Mv; }

        public static SolveResult Solve(int[][] start, int C, int budget = 40000, double weight = 2.5)
        {
            var s0 = Rules.Clone(start);
            if (Rules.IsSolved(s0, C)) return new SolveResult { Ok = true, Path = new List<Move>(), Nodes = 0, Exhausted = true };
            var heap = new List<Node>();
            var seen = new HashSet<string> { Rules.KeyOf(s0) };

            void Push(Node node)
            {
                heap.Add(node);
                int i = heap.Count - 1;
                while (i > 0)
                {
                    int p = (i - 1) >> 1;
                    if (heap[p].F <= node.F) break;
                    heap[i] = heap[p]; i = p;
                }
                heap[i] = node;
            }
            Node Pop()
            {
                var top = heap[0];
                var last = heap[heap.Count - 1];
                heap.RemoveAt(heap.Count - 1);
                if (heap.Count > 0)
                {
                    int i = 0, n = heap.Count;
                    for (;;)
                    {
                        int l = 2 * i + 1, r = l + 1, m = i;
                        if (l < n && heap[l].F < (m == i ? last.F : heap[m].F)) m = l;
                        if (r < n && heap[r].F < (m == i ? last.F : heap[m].F)) m = r;
                        if (m == i) break;
                        heap[i] = heap[m]; i = m;
                    }
                    heap[i] = last;
                }
                return top;
            }

            Push(new Node { S = s0, G = 0, F = weight * Rules.Heur(s0) });
            int nodes = 0;
            while (heap.Count > 0)
            {
                var cur = Pop();
                if (++nodes > budget) return new SolveResult { Ok = false, Nodes = nodes, Exhausted = false };
                foreach (var m in Rules.ListMoves(cur.S, C, true))
                {
                    var ns = Rules.Apply(cur.S, m);
                    if (!seen.Add(Rules.KeyOf(ns))) continue;
                    var node = new Node { S = ns, G = cur.G + 1, Parent = cur, Mv = m };
                    if (Rules.IsSolved(ns, C))
                    {
                        var path = new List<Move>();
                        for (var x = node; x.Parent != null; x = x.Parent) path.Add(x.Mv);
                        path.Reverse();
                        return new SolveResult { Ok = true, Path = path, Nodes = nodes, Exhausted = true };
                    }
                    node.F = node.G + weight * Rules.Heur(ns);
                    Push(node);
                }
            }
            return new SolveResult { Ok = false, Nodes = nodes, Exhausted = true };
        }
    }
}
```

### 5.6 `Playouts.cs` (the simulated players)

```csharp
using System.Collections.Generic;

namespace Playbox.PaintSort.Engine
{
    public static class Playouts
    {
        static List<Move> Candidates(int[][] s, int C, int li, int lj)
        {
            var ms = Rules.ListMoves(s, C, false);
            ms.RemoveAll(m => m.From == lj && m.To == li);   // never undo the previous pour
            return ms;
        }

        /// No lookahead: always finishes a vial if it can, usually stacks onto
        /// matching paint, otherwise pours at random. Returns moves used or -1.
        public static int Casual(int[][] start, int C, Mulberry32 r, int maxSteps)
        {
            var s = Rules.Clone(start); int li = -1, lj = -1;
            for (int step = 0; step < maxSteps; step++)
            {
                if (Rules.IsSolved(s, C)) return step;
                var ms = Candidates(s, C, li, lj);
                if (ms.Count == 0) return -1;
                Move? pick = null;
                foreach (var x in ms)
                {
                    var w = s[x.To];
                    if (w.Length + x.Count == C && (w.Length == 0 ? Rules.RunLen(s[x.From]) == C : Rules.RunLen(w) == w.Length))
                    { pick = x; break; }
                }
                if (pick == null)
                {
                    var cur = s;
                    var onto = ms.FindAll(x => cur[x.To].Length > 0);
                    // the RNG is only consumed when onto is non-empty (JS short-circuit)
                    pick = (onto.Count > 0 && r.Next() < .8) ? onto[(int)(r.Next() * onto.Count)] : ms[(int)(r.Next() * ms.Count)];
                }
                var mv = pick.Value;
                s = Rules.Apply(s, mv); li = mv.From; lj = mv.To;
            }
            return -1;
        }

        /// One-move-deep judgement of a pour.
        public static double RateMove(int[][] s, int C, Move x)
        {
            var v = s[x.From]; var w = s[x.To]; int k = Rules.RunLen(v);
            double sc = 0;
            if (w.Length > 0)
            {
                sc += 2;
                if (x.Count == k) sc += 1;
                if (Rules.RunLen(w) == w.Length && w.Length + x.Count == C) sc += 3;
            }
            else
            {
                sc -= 1.5;
                if (k == v.Length) sc -= 3;
            }
            if (x.Count == k && v.Length > k)
            {
                int under = v[v.Length - k - 1];
                for (int j = 0; j < s.Length; j++)
                {
                    if (j == x.From || j == x.To) continue;
                    var u = s[j];
                    if (u.Length > 0 && u.Length < C && u[u.Length - 1] == under) { sc += .8; break; }
                }
            }
            return sc;
        }

        /// Takes the best-rated pour plus noise.
        public static int Skilled(int[][] start, int C, Mulberry32 r, int maxSteps)
        {
            var s = Rules.Clone(start); int li = -1, lj = -1;
            for (int step = 0; step < maxSteps; step++)
            {
                if (Rules.IsSolved(s, C)) return step;
                var ms = Candidates(s, C, li, lj);
                if (ms.Count == 0) return -1;
                Move best = default; double bestScore = -1e9;
                foreach (var x in ms)
                {
                    double sc = RateMove(s, C, x) + r.Next() * 1.6;
                    if (sc > bestScore) { bestScore = sc; best = x; }
                }
                s = Rules.Apply(s, best); li = best.From; lj = best.To;
            }
            return -1;
        }
    }
}
```

### 5.7 `Generator.cs`

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

namespace Playbox.PaintSort.Engine
{
    public sealed class GeneratedLevel
    {
        public LevelSpec Spec;
        public int[][] Vials;        // colour indices 0..K-1, K full vials then E empty
        public int[] Palette;        // Palette[colour] = pigment index 0..11 (§16.2)
        public bool[][] Hidden;      // per unit: starts hidden under a '?'
        public double Fail, Casual, Skilled;
        public int Len, Pool;
    }

    public static class Generator
    {
        sealed class Cand { public int[][] S; public double Casual, Skilled, Fail; public int Len; }

        public static int[][] Deal(int K, int E, int C, Mulberry32 r)
        {
            var pool = new List<int>();
            for (int c = 0; c < K; c++) for (int u = 0; u < C; u++) pool.Add(c);
            int[][] s = null;
            for (int tries = 0; tries < 60; tries++)
            {
                Seeds.Shuffle(pool, r);                 // the same pool is reshuffled each try
                s = new int[K][];
                for (int i = 0; i < K; i++) s[i] = pool.GetRange(i * C, C).ToArray();
                if (s.Any(v => Rules.IsFull(v, C))) continue;
                int pairs = 0;
                foreach (var v in s) for (int i = 1; i < C; i++) if (v[i] == v[i - 1]) pairs++;
                if (pairs > Math.Max(1, K / 2)) continue;
                break;
            }
            var full = new int[K + E][];
            for (int i = 0; i < K; i++) full[i] = s[i];
            for (int e = 0; e < E; e++) full[K + e] = Array.Empty<int>();
            return full;
        }

        /// Deterministic: the same n gives the same level on every device.
        public static GeneratedLevel Generate(int n)
        {
            var sp = Difficulty.Spec(n); int C = sp.Cap;
            var r = new Mulberry32(Seeds.SeedFor(n, 7));
            var cands = new List<Cand>();
            int attempts = 0;
            while (cands.Count < sp.Cands && attempts < sp.Cands * 6)
            {
                attempts++;
                var s = Deal(sp.K, sp.E, C, r);
                var sol = Solver.Solve(s, C, 25000);
                if (!sol.Ok) continue;
                int R = sp.Tier > 0 ? 20 : 14, steps = 60 + sp.K * 14;
                var pr = new Mulberry32(Seeds.SeedFor(n, 100 + attempts));
                int casual = 0, skilled = 0;
                for (int i = 0; i < R; i++)
                {
                    if (Playouts.Casual(s, C, pr, steps) < 0) casual++;
                    if (Playouts.Skilled(s, C, pr, steps) < 0) skilled++;
                }
                cands.Add(new Cand { S = s, Casual = (double)casual / R, Skilled = (double)skilled / R,
                                     Fail = (double)(casual + skilled) / (2 * R), Len = sol.Path.Count });
            }
            while (cands.Count == 0)   // practically unreachable; keeps Generate total
            {
                var s = Deal(sp.K, sp.E, C, r);
                var sol = Solver.Solve(s, C, 300000);
                if (sol.Ok) cands.Add(new Cand { S = s, Len = sol.Path.Count });
            }
            // LINQ OrderBy is stable, like JS Array.prototype.sort
            cands = cands.OrderBy(c => c.Fail).ThenBy(c => c.Len).ToList();
            var pick = cands[Seeds.JsRound(sp.Pick * (cands.Count - 1))];

            var pr2 = new Mulberry32(Seeds.SeedFor(n, 3));
            var pal = Enumerable.Range(0, Difficulty.MaxColours).ToList();
            Seeds.Shuffle(pal, pr2);
            var hidden = new bool[pick.S.Length][];
            for (int vi = 0; vi < pick.S.Length; vi++)
            {
                var v = pick.S[vi];
                int keep = v.Length > 0 ? Rules.RunLen(v) : 0;
                hidden[vi] = new bool[v.Length];
                for (int i = 0; i < v.Length; i++)
                    hidden[vi][i] = sp.Mystery > 0 && i < v.Length - keep && pr2.Next() < sp.Mystery;
            }
            return new GeneratedLevel
            {
                Spec = sp, Vials = pick.S, Palette = pal.Take(sp.K).ToArray(), Hidden = hidden,
                Fail = pick.Fail, Casual = pick.Casual, Skilled = pick.Skilled, Len = pick.Len, Pool = cands.Count
            };
        }
    }
}
```

### 5.8 `Probe.cs`

```csharp
using System.Collections.Generic;
using System.Diagnostics;

namespace Playbox.PaintSort.Engine
{
    public struct ProbeRow { public int N, Tier, K, Hidden, Len, Pool; public double Heat, Fail, Casual, Skilled; public long Ms; }

    public static class Probe
    {
        public static List<ProbeRow> Run(int from, int to)
        {
            var rows = new List<ProbeRow>();
            for (int n = from; n <= to; n++)
            {
                var sw = Stopwatch.StartNew();
                var g = Generator.Generate(n);
                int hid = 0; foreach (var v in g.Hidden) foreach (var h in v) if (h) hid++;
                rows.Add(new ProbeRow { N = n, Tier = g.Spec.Tier, K = g.Spec.K, Heat = g.Spec.Heat, Fail = g.Fail,
                    Casual = g.Casual, Skilled = g.Skilled, Len = g.Len, Hidden = hid, Pool = g.Pool, Ms = sw.ElapsedMilliseconds });
            }
            return rows;
        }
    }
}
```

### 5.9 `Art/ArtBuilder.cs` (painting composition)

Pure: returns path commands in art space (400 × 300, y-down). Rendering is §12.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

namespace Playbox.PaintSort.Engine.Art
{
    public enum PathOp { MoveTo, LineTo, Arc, Quad, Close }

    /// MoveTo/LineTo: A,B = x,y. Arc: A,B = centre, C = radius, D = start, E = end, Ccw.
    /// Quad: A,B = control point, C,D = end point. Semantics are HTML canvas Path2D.
    public struct PathCmd { public PathOp Op; public double A, B, C, D, E; public bool Ccw; }

    public struct Streak { public double U, V, Len, Width; public bool Light; }

    public sealed class ArtShape
    {
        public string Kind;
        public readonly List<PathCmd> Path = new List<PathCmd>();
        public double X, Y, W, H;                       // bounding box (art space)
        public bool EvenOdd, Ground;
        public int Slot;                                // which of the level's colours paints this shape
        public Streak[] Streaks;
    }

    public static class ArtBuilder
    {
        public const double ArtW = 400, ArtH = 300;

        public static List<ArtShape> Build(int n, int K)
        {
            var r = new Mulberry32(Seeds.SeedFor(n, 11));
            double R(double a, double b) => a + r.Next() * (b - a);

            var shapes = new List<ArtShape>();
            var ground = new ArtShape { Kind = "ground", Ground = true, X = 0, Y = 0, W = ArtW, H = ArtH };
            Poly(ground, new double[] { 0, 0, ArtW, 0, ArtW, ArtH, 0, ArtH });
            shapes.Add(ground);

            var big = new List<string> { "hill", "arch", "stripe", "block", "peak", "wave" };
            Seeds.Shuffle(big, r);
            var small = new List<string> { "sun", "ring", "leaf", "dots", "blob", "sun2" };
            Seeds.Shuffle(small, r);
            int nBig = Math.Min(K - 1, 1 + (int)Math.Floor((K - 1) * .45));
            var kinds = new List<string>();
            for (int i = 0; i < nBig; i++) kinds.Add(big[i % big.Count]);
            for (int i = 0; kinds.Count < K - 1; i++) kinds.Add(small[i % small.Count]);
            foreach (var k in kinds) shapes.Add(MakeShape(k, R));

            var slots = Enumerable.Range(0, K).ToList();
            Seeds.Shuffle(slots, r);
            for (int i = 0; i < shapes.Count; i++)
            {
                shapes[i].Slot = slots[i];
                shapes[i].Streaks = new Streak[10];
                for (int k = 0; k < 10; k++)
                {
                    double u = r.Next(), v = r.Next(), len = R(.35, .9), lw = R(1.2, 3.4);
                    bool light = r.Next() < .5;
                    shapes[i].Streaks[k] = new Streak { U = u, V = v, Len = len, Width = lw, Light = light };
                }
            }
            return shapes;
        }

        static void Poly(ArtShape s, double[] p)
        {
            s.Path.Add(new PathCmd { Op = PathOp.MoveTo, A = p[0], B = p[1] });
            for (int i = 2; i < p.Length; i += 2) s.Path.Add(new PathCmd { Op = PathOp.LineTo, A = p[i], B = p[i + 1] });
            s.Path.Add(new PathCmd { Op = PathOp.Close });
        }
        static void BB(ArtShape s, double[] p)
        {
            double x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
            for (int i = 0; i < p.Length; i += 2)
            { x0 = Math.Min(x0, p[i]); x1 = Math.Max(x1, p[i]); y0 = Math.Min(y0, p[i + 1]); y1 = Math.Max(y1, p[i + 1]); }
            x0 = Math.Max(0, x0); y0 = Math.Max(0, y0); x1 = Math.Min(ArtW, x1); y1 = Math.Min(ArtH, y1);
            s.X = x0; s.Y = y0; s.W = x1 - x0; s.H = y1 - y0;
        }
        static double[] Rot(double cx, double cy, double a, double[] p)
        {
            double c = Math.Cos(a), sn = Math.Sin(a); var o = new double[p.Length];
            for (int i = 0; i < p.Length; i += 2) { o[i] = cx + p[i] * c - p[i + 1] * sn; o[i + 1] = cy + p[i] * sn + p[i + 1] * c; }
            return o;
        }
        static void Arc(ArtShape s, double cx, double cy, double rad, double a0, double a1, bool ccw = false)
            => s.Path.Add(new PathCmd { Op = PathOp.Arc, A = cx, B = cy, C = rad, D = a0, E = a1, Ccw = ccw });
        static void Move(ArtShape s, double x, double y) => s.Path.Add(new PathCmd { Op = PathOp.MoveTo, A = x, B = y });
        static void Line(ArtShape s, double x, double y) => s.Path.Add(new PathCmd { Op = PathOp.LineTo, A = x, B = y });
        static void Quad(ArtShape s, double cx, double cy, double x, double y) => s.Path.Add(new PathCmd { Op = PathOp.Quad, A = cx, B = cy, C = x, D = y });

        // The order of R() calls below is part of the determinism contract.
        static ArtShape MakeShape(string kind, Func<double, double, double> R)
        {
            var s = new ArtShape { Kind = kind };
            switch (kind)
            {
                case "hill":
                {
                    double y0 = R(170, 228), amp = R(12, 30), f = R(.8, 2.2) * Math.PI * 2 / ArtW, ph = R(0, 6.3);
                    var p = new List<double> { 0, ArtH };
                    for (int x = 0; x <= ArtW; x += 10) { p.Add(x); p.Add(y0 + amp * Math.Sin(x * f + ph)); }
                    p.Add(ArtW); p.Add(ArtH);
                    Poly(s, p.ToArray());
                    s.X = 0; s.Y = y0 - amp; s.W = ArtW; s.H = ArtH - y0 + amp;
                    return s;
                }
                case "wave":
                {
                    double y0 = R(80, 190), amp = R(10, 22), t = R(18, 30), f = R(1, 2.4) * Math.PI * 2 / ArtW, ph = R(0, 6.3);
                    var p = new List<double>();
                    for (int x = -10; x <= ArtW + 10; x += 10) { p.Add(x); p.Add(y0 + amp * Math.Sin(x * f + ph)); }
                    for (int x = (int)ArtW + 10; x >= -10; x -= 10) { p.Add(x); p.Add(y0 + t + amp * Math.Sin(x * f + ph)); }
                    Poly(s, p.ToArray());
                    s.X = 0; s.Y = y0 - amp; s.W = ArtW; s.H = t + amp * 2;
                    return s;
                }
                case "arch":
                {
                    double cx = R(70, 330), rad = R(46, 78), bs = R(232, 300);
                    Move(s, cx - rad, ArtH); Line(s, cx - rad, bs); Arc(s, cx, bs, rad, Math.PI, 0); Line(s, cx + rad, ArtH);
                    s.Path.Add(new PathCmd { Op = PathOp.Close });
                    s.X = cx - rad; s.Y = bs - rad; s.W = rad * 2; s.H = ArtH - bs + rad;
                    return s;
                }
                case "stripe":
                {
                    double a = R(-.55, .55), cx = R(90, 310), cy = R(70, 220), t = R(24, 46);
                    var p = Rot(cx, cy, a, new[] { -420, -t / 2, 420, -t / 2, 420, t / 2, -420, t / 2 });
                    Poly(s, p); BB(s, p); return s;
                }
                case "block":
                {
                    double w = R(70, 140), h = R(55, 110), a = R(-.28, .28), cx = R(90, 310), cy = R(90, 210);
                    var p = Rot(cx, cy, a, new[] { -w / 2, -h / 2, w / 2, -h / 2, w / 2, h / 2, -w / 2, h / 2 });
                    Poly(s, p); BB(s, p); return s;
                }
                case "peak":
                {
                    double bs = R(236, 300), px = R(80, 320), ht = R(100, 170), hw = R(80, 150);
                    var p = new[] { px - hw, ArtH, px - hw, bs, px, bs - ht, px + hw, bs, px + hw, ArtH };
                    Poly(s, p); BB(s, p); return s;
                }
                case "sun":
                case "sun2":
                {
                    double rad = kind == "sun" ? R(28, 46) : R(16, 26), cx = R(40 + rad, 360 - rad), cy = R(30 + rad, 170);
                    Arc(s, cx, cy, rad, 0, Math.PI * 2);
                    s.X = cx - rad; s.Y = cy - rad; s.W = rad * 2; s.H = rad * 2;
                    return s;
                }
                case "ring":
                {
                    double ro = R(30, 48), ri = ro * R(.48, .64), cx = R(60, 340), cy = R(60, 220);
                    Arc(s, cx, cy, ro, 0, Math.PI * 2); Move(s, cx + ri, cy); Arc(s, cx, cy, ri, 0, Math.PI * 2, true);
                    s.EvenOdd = true;
                    s.X = cx - ro; s.Y = cy - ro; s.W = ro * 2; s.H = ro * 2;
                    return s;
                }
                case "leaf":
                {
                    double len = R(80, 130), wid = len * R(.3, .44), a = R(0, Math.PI), cx = R(80, 320), cy = R(70, 230);
                    var p = Rot(cx, cy, a, new[] { -len / 2, 0, 0, -wid, len / 2, 0, 0, wid });
                    Move(s, p[0], p[1]); Quad(s, p[2], p[3], p[4], p[5]); Quad(s, p[6], p[7], p[0], p[1]);
                    s.Path.Add(new PathCmd { Op = PathOp.Close });
                    BB(s, p); return s;
                }
                case "dots":
                {
                    double cx = R(70, 330), cy = R(60, 230); int cnt = 5 + (int)R(0, 4);
                    var p = new List<double>();
                    for (int i = 0; i < cnt; i++)
                    {
                        double a = R(0, 6.3), d = R(0, 46), rr = R(6, 12), x = cx + Math.Cos(a) * d, y = cy + Math.Sin(a) * d;
                        Move(s, x + rr, y); Arc(s, x, y, rr, 0, Math.PI * 2);
                        p.AddRange(new[] { x - rr, y - rr, x + rr, y + rr });
                    }
                    BB(s, p.ToArray()); return s;
                }
                default: // blob
                {
                    double cx = R(80, 320), cy = R(70, 220); const int n = 9; var p = new double[n * 2];
                    for (int i = 0; i < n; i++) { double a = (double)i / n * Math.PI * 2, rr = R(26, 54); p[i * 2] = cx + Math.Cos(a) * rr; p[i * 2 + 1] = cy + Math.Sin(a) * rr; }
                    (double, double) Mid(int i) => ((p[i * 2] + p[(i + 1) % n * 2]) / 2, (p[i * 2 + 1] + p[(i + 1) % n * 2 + 1]) / 2);
                    var m0 = Mid(n - 1); Move(s, m0.Item1, m0.Item2);
                    for (int i = 0; i < n; i++) { var m = Mid(i); Quad(s, p[i * 2], p[i * 2 + 1], m.Item1, m.Item2); }
                    s.Path.Add(new PathCmd { Op = PathOp.Close });
                    BB(s, p); return s;
                }
            }
        }
    }
}
```

### 5.10 JavaScript-to-C# parity rules

| JavaScript | C# | Why it matters |
| --- | --- | --- |
| `Math.round(x)` | `Seeds.JsRound(x)` = `floor(x + 0.5)` | `Math.Round` is banker's rounding; `Math.Round(6.5) == 6` but JS gives 7. |
| `Array.prototype.sort` (stable) | LINQ `OrderBy(...).ThenBy(...)` | `List.Sort` is unstable and reorders equal candidates. |
| default string sort | `string.CompareOrdinal` | Culture comparison sorts differently. |
| `Math.imul`, `>>>`, `\|0` on hashes | `uint` arithmetic in `unchecked` | Must wrap at 32 bits. |
| `(x * n) \| 0` for indices | `(int)(x * n)` | Truncation; values are non-negative. |
| `a && r() < p` | `a && r.Next() < p` | The RNG must not be consumed when `a` is false. |
| `filter` | `FindAll` / `RemoveAll` | Both keep order. |
| numbers | `double` | Never `float` in the engine. |

### 5.11 Engine usage rules

- `Generator.Generate(n)` takes up to ~350 ms at level 120 on a desktop core and
  more on phones. **Always call it on a worker thread** (§18).
- The expected difficulty curve is Appendix B.2. The probe CLI (§19.3) must print
  identical numbers.

---

## 6. Level state and game rules

### 6.1 The ids model

Every unit of paint gets an id at level start. The board stores ids, so the
reveal state follows the paint when it moves, and undo never re-hides anything.

```csharp
public sealed class LevelState
{
    public int N;
    public LevelSpec Spec;
    public int[] ColorOf;               // id -> pigment index 0..11
    public int[] Palette;               // colour slot -> pigment (from GeneratedLevel.Palette)
    public List<List<int>> Vials;       // ids, bottom to top
    public HashSet<int> Revealed;       // ids whose colour is visible
    public List<List<int>> Init;        // starting vials (for Restart)
    public List<int> Rev0;              // starting revealed ids (for Restart)
    public List<HistoryEntry> Hist;     // snapshots for Undo, max 40
    public int Undos = 5, Moves;
    public bool Extra, Help, Won, Clean;
    public HashSet<int> DoneSet;        // pigments currently sitting in a corked vial
}
public sealed class HistoryEntry { public List<List<int>> V; public int M; }
```

**Fresh level** from a `GeneratedLevel g`: walk `g.Vials` vial by vial, unit by
unit; each unit gets the next id; `ColorOf[id] = g.Palette[colour]`; the id goes
in `Revealed` unless `g.Hidden[vi][ui]`. Copy `Vials` to `Init` and `Revealed` to
`Rev0`.

### 6.2 Rules on ids

- `Col(id) = ColorOf[id]`; `Colors()` maps `Vials` to `int[][]` of pigments for the engine.
- `VialFull(i)`: 4 units, all the same pigment.
- `TopRun(i)`: count of same-pigment units from the top.
- `CanPour(i, j)`: `i != j`, source non-empty and not full, target has fewer
  than 4 units, and the target is empty or its top pigment equals the source's.
- `RevealTops()`: for every vial, add every id in its top run to `Revealed`.
  Return the ids newly revealed (with their vial index).
- `BandsOf(i)`: merge consecutive units into bands `{pigment, units, hidden}`.
  Two visible units merge when they have the same pigment; **all consecutive
  hidden units merge into one hidden band whatever their colour**, so a seam
  never gives away hidden paint.

### 6.3 A pour

1. Snapshot the source and target bands (for the animation).
2. Push `{V: copy of Vials, M: Moves}` to `Hist` (drop the oldest past 40).
3. `n = min(TopRun(i), 4 - target count)`; move the top `n` ids from `i` to `j`.
4. `Moves++`; `fresh = RevealTops()`; `completes = VialFull(j)`.
5. Clear the selection and any hint pointer; hide the stuck bar.
6. If `Rules.IsSolved(Colors(), 4)` → `OnSolved()` immediately (the level counts
   as won even if the app closes mid-animation).
7. Save. Start a `PourAnimation` (§9).

When the pour animation ends: reset the source's lift; set wobble (source
`0.07w`, target `max(current, 0.06w)`); play the plop; if `fresh` has ids in the
source, play the reveal sound and a white sparkle at the source's new surface;
if `completes`, run **Celebrate** (§6.9); recompute `DoneSet` and the painting;
if the level is won and no other pours are animating, start the win sequence
after 250 ms, otherwise schedule the dead-end check.

`OnSolved`: `Won = true`; coins += `Spec.Reward`; stats (`won`, `hard` for tier
1, `super` for tier 2); `Clean = !Help`, and if clean coins += 5; if `N == 1` set
`tips.tut = true`; `level = max(level, N + 1)`; `cur = null`; save now; start
generating level `N + 1` in the background.

### 6.4 Input

Tapping vial `i` (hit test in §7.3):

| State | Tap | Result |
| --- | --- | --- |
| any | level won, or vial `i` is animating | ignore |
| nothing selected | empty vial | shake `i`, tink |
| nothing selected | full (corked) vial | shake `i` at 0.6, tink |
| nothing selected | otherwise | select `i`, pick sound, haptic 6 |
| `i` selected | same vial | deselect, drop sound |
| `s` selected | `CanPour(s, i)` | pour `s → i` |
| `s` selected | not pourable | shake `i`, bonk, haptic [18,30,18], deselect |
| something selected | empty space | deselect, drop sound |

Other vials stay tappable while pours are animating; only the vials in a pour
are locked. Keyboard (editor and desktop builds): `1..9, 0, -, =` pick vials
1–12; ←/→ move a focus ring, Enter/Space taps it; `U` undo, `H` hint, `R`
restart (asks first), `Esc` deselects.

### 6.5 Boosters

- **Undo**: ignored while any pour animates. No history → toast "Nothing to
  undo yet". `Undos == 0` → Buy sheet. Otherwise restore the last snapshot,
  `Undos--`, `Help = true`, set every vial's wobble to 0.06w, recompute the
  painting (a pigment that is no longer corked loses its paint instantly), undo
  sound, haptic 10.
- **Hint**: inventory 0 → Buy sheet. Otherwise run `Solver.Solve(Colors(), 4,
  30000)` on a worker. `Ok` → show the pointer on `Path[0]`, `inv.hint--`,
  `Help = true`, hint sound. Proven dead (`!Ok && Exhausted`) → show the stuck
  bar and toast "No pour wins from here. Undo or restart.", and **don't** spend
  the hint. Budget ran out → sort `ListMoves(prune:false)` by `RateMove`
  descending and show the best.
- **Add vial**: once per level ("One extra vial per level" toast). Inventory 0 →
  Buy sheet. Otherwise `inv.vial--`, `Extra = Help = true`; append an empty list
  to `Vials`, `Init` and every `Hist` snapshot; re-layout; the new vial pops in;
  vial sound; white sparkle ×12.
- **Restart**: ignored while animating. If `Moves > 0` ask first (Restart
  sheet). Resets `Vials = Init`, `Revealed = Rev0`, clears history, `Undos = 5`,
  `Moves = 0`, keeps an added vial, wobble 0.08w, hop stagger 30 ms, undo sound.

### 6.6 Dead-end watcher

380 ms after the last pour finishes (debounced), on a worker thread: if
`ListMoves(Colors(), 4, false)` is empty, or `Solver.Solve(Colors(), 4, 5000)`
returns `!Ok && Exhausted`, the board is dead: show the stuck bar ("No way out
from here" with Undo, Add vial (hidden if already used), Restart) and play the
bonk. Tag each check with a state version and drop stale results.

### 6.7 Tutorial and coach line

Level 1, while `tips.tut` is false:
- While `Moves < 3` and nothing is animating, solve (budget 4000) and point at
  `Path[0]`. From move 3 on, no pointer.
- Coach text: selected → "Now tap where it goes. Paint lands only on its own
  colour, or in an empty vial."; `Moves == 0` → "Tap a vial to pick it up.";
  nothing corked yet → "Keep going until a vial holds a single colour.";
  otherwise → "Every finished vial paints part of the picture above."
- After the win: "That is the whole painting. Nicely done."

Any level with hidden paint, before the first move with nothing selected:
"Grey paint shows its colour once it reaches the top." While a level is
generating: "Mixing paint…".

### 6.8 Economy (`Economy.cs`)

| Constant | Value |
| --- | --- |
| Starting coins | 120 |
| Starting inventory | 3 hints, 2 vials |
| Undos per try | 5 |
| Reward normal / hard / super hard | 10 / 30 / 60 |
| Bonus for no undo, hint or extra vial | +5 |
| Price: hint | 40 |
| Price: extra vial | 90 |
| Price: 5 more undos | 30 |
| History cap | 40 |

### 6.9 Celebrate (a vial is corked)

`k` = number of full vials − 1. Start the cork drop and the glow. Show the float
label with the pigment name. After 150 ms: complete sound `k` (clamped to 12),
haptic [12,30,16], sparkles (pigment colour ×16 at power 1.2, white ×8 at power
0.9) at 0.2w above the mouth. The painting starts revealing that pigment 120 ms
after the pour ends.

### 6.10 Win sequence

All vials hop (stagger 55 ms); 46 splats in palette colours (§11); win sound;
haptic [20,60,20,60,40]; after 1250 ms open the Win sheet (§15.8).

---

## 7. Board layout

Input: the field rectangle (the UI `FieldArea` between the coach line and the
booster bar) converted to world units: width `W`, height `H`, and its top-left
corner. All numbers are world units (= dp).

```
count   = number of vials
rows    = (count <= 6 || (W > 540 && count <= 8)) ? 1 : 2
perRow  = ceil(count / rows)
slotW   = (W - 16) / perRow
byW     = slotW * (rows == 1 ? 0.66 : 0.62)
byH     = (H - 12) / (rows * 3.95 + (rows - 1) * 1.2 + 1.6)
w       = clamp(min(byW, byH), 14, 60)
vialH   = Hgeo * w + 0.1w              // Hgeo = 3.807301 (§8.1)
gap     = 1.2w
used    = rows * vialH + (rows - 1) * gap + 1.6w
top     = max(0, (H - used) / 2) + 1.25w      // distance from the field top to the first row's mouth
counts  = rows == 1 ? [count] : [ceil(count/2), floor(count/2)]
mouth x = fieldCentreX + (k - (cnt - 1) / 2) * slotW
mouth y = fieldTopY - top - row * (vialH + gap)          // y-up
```

Re-layout on field resize and when a vial is added. Vials glide to new slots:
`dx += (x - dx) * min(1, dt * 0.014)` (same for y).

### 7.3 Hit testing

A tap belongs to the vial whose slot column contains it (`|x - dx| < slotW/2`,
nearest wins) and whose vertical band contains it: from `mouthY + lift + 0.9w`
down to `mouthY - Hgeo*w - 0.35w`.

---

## 8. Vials: geometry, meshes, liquid shader

### 8.1 Geometry (`VialGeometry.cs`, w = 1)

```
r = 0.5, head = 0.5, unitH = 0.8, unitA = 0.8 (area of one paint unit)
Hgeo = head + r + (4 * unitH - PI * r * r / 2) = 3.807301
```

Interior polygon (convex, y-up, 20 points): `(-0.5, 0)`, `(0.5, 0)`,
`(0.5, -(Hgeo - r))`, then for `k = 1..15`, `a = k/16 * PI`:
`(r*cos a, -(Hgeo - r) - r*sin a)`, then `(-0.5, -(Hgeo - r))`.

```csharp
public static class VialGeometry
{
    public const double R = .5, Head = .5, UnitH = .8, UnitA = .8;
    public static readonly double Hgeo = Head + R + (4 * UnitH - Math.PI * R * R / 2);
    public static readonly double[] Poly = BuildPoly();          // flat x,y pairs, w = 1
    public static readonly double[] CapTable = BuildCapTable();  // index = degrees 0..125

    static double[] BuildPoly()
    {
        var p = new List<double> { -.5, 0, .5, 0, .5, -(Hgeo - R) };
        for (int k = 1; k < 16; k++) { double a = k / 16.0 * Math.PI; p.Add(R * Math.Cos(a)); p.Add(-(Hgeo - R) - R * Math.Sin(a)); }
        p.Add(-.5); p.Add(-(Hgeo - R));
        return p.ToArray();
    }

    /// Area of the polygon at or below height Y (y-up).
    public static double AreaBelow(double[] p, double Y)
    {
        var o = new List<double>(p.Length + 4); int n = p.Length / 2;
        for (int i = 0; i < n; i++)
        {
            double ax = p[2 * i], ay = p[2 * i + 1]; int j = (i + 1) % n; double bx = p[2 * j], by = p[2 * j + 1];
            bool ain = ay <= Y, bin = by <= Y;
            if (ain) { o.Add(ax); o.Add(ay); }
            if (ain != bin) { double t = (Y - ay) / (by - ay); o.Add(ax + (bx - ax) * t); o.Add(Y); }
        }
        double s = 0; int m = o.Count / 2;
        for (int i = 0; i < m; i++) { int j = (i + 1) % m; s += o[2 * i] * o[2 * j + 1] - o[2 * j] * o[2 * i + 1]; }
        return Math.Abs(s) / 2;
    }

    /// Height of a flat surface that encloses area V. 22 bisection steps.
    public static double LevelFor(double[] p, double V, double lo, double hi)
    {
        for (int k = 0; k < 22; k++) { double mid = (lo + hi) / 2; if (AreaBelow(p, mid) > V) hi = mid; else lo = mid; }
        return (lo + hi) / 2;
    }

    /// What the vial still holds when tipped d degrees clockwise about its right lip.
    static double[] BuildCapTable()
    {
        var t = new double[126];
        for (int d = 0; d <= 125; d++)
        {
            double a = d * Math.PI / 180, c = Math.Cos(a), s = Math.Sin(a);
            var q = new double[Poly.Length];
            for (int i = 0; i < Poly.Length; i += 2)
            {
                double x = Poly[i] - .5, y = Poly[i + 1];     // lip at the origin
                q[i] = x * c + y * s; q[i + 1] = -x * s + y * c;   // rotate by -a (clockwise)
            }
            t[d] = AreaBelow(q, 0);
        }
        return t;
    }

    public static double CapAt(double theta)
    {
        double d = Math.Abs(theta) * 180 / Math.PI;
        if (d >= 125) return 0;
        int i = (int)Math.Floor(d); double f = d - i;
        return CapTable[i] * (1 - f) + CapTable[i + 1] * f;
    }

    public static double AngleFor(double V)
    {
        if (V >= CapTable[0]) return 0;
        for (int d = 0; d < CapTable.Length - 1; d++)
            if (CapTable[d + 1] <= V) { double f = (CapTable[d] - V) / ((CapTable[d] - CapTable[d + 1]) == 0 ? 1 : (CapTable[d] - CapTable[d + 1])); return (d + f) * Math.PI / 180; }
        return 125 * Math.PI / 180;
    }
}
```

World polygon for a pose (§9.1): `world = P + Rot(phi) * ((local - L) * w)`,
where `phi` is the z-rotation in radians. World areas scale by `w²`: a vial
holding `u` units encloses `u * UnitA * w²`.

### 8.2 Meshes (`VialMeshes.cs`, built at runtime, w = 1)

| Mesh | Construction | Colour |
| --- | --- | --- |
| Interior | triangle fan from the centroid of `Poly` | GlassBack: `--ps-glass`; Liquid uses the same mesh |
| Outline | open ribbon along `(-0.5,0) → (-0.5,-(Hgeo-r)) → bottom arc (48 segments) → (0.5,-(Hgeo-r)) → (0.5,0)`, width `lw = max(1.6/w, 0.075)`, round joins, butt caps | `--ps-edge` |
| Rim | rounded rect x ∈ [−0.5 − 1.15lw, 0.5 + 1.15lw], y ∈ [−0.9lw, +1.1lw], corner radius `lw`, 6 segments per corner | `--ps-edge` |
| Highlight A | capsule from (−0.27, −0.35) to (−0.27, −(Hgeo − 0.55)), width 0.10 | `--ps-hi` × alpha 0.70 |
| Highlight B | capsule from (−0.10, −0.40) to (−0.10, −1.05), width 0.05 | `--ps-hi` × alpha 0.45 |
| Shadow | ellipse, 32 segments, rx 0.62, ry 0.13 | `--ps-floor` |
| Select glow | SoftStroke ribbon along the outline path, width `1.8lw + 0.5` | `--accent` |

Rebuild Outline and Rim when `w` changes (their width has a dp minimum). The
shadow is **not** a child of the vial: it stays on the floor at
`(dx, mouthY - (Hgeo + 0.16) * w)` while the vial lifts, with alpha
`clamp(1 - lift / 1.2w, 0.3, 1)`.

`RibbonBuilder` (in Core/Util) handles polylines → triangle strips: miter joins
with a limit of 2 (fall back to bevel), optional round caps (6-segment fans),
optional dash pattern (list of on/off lengths), and `uv.y` = 0 on one edge and 1
on the other (for SoftStroke and Stream).

### 8.3 Draw order inside a vial

Sorting order within the vial's `SortingGroup`: SelectGlow/CompleteGlow −1,
GlassBack 0, Liquid 1, Symbols 2, Highlights 3, Outline 4, Rim 5, Cork 6.
Between vials: resting vials sort 0; a vial being poured from sorts 100 so it
draws over its neighbours; streams sort 50; FX sort on the `Fx` layer.

### 8.4 Liquid shader (`Shaders/Liquid.shader`)

The CPU computes band tops in world space (§8.5) and the shader colours the
interior mesh by world height, so the surface stays flat whatever the tilt.

```hlsl
Shader "PaintSort/Liquid"
{
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "RenderPipeline"="UniversalPipeline" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off Cull Off
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #define MAX_BANDS 8

            float  _BandCount;
            float  _BandTop[MAX_BANDS];     // world y of each band's top edge, bottom to top
            float4 _BandColor[MAX_BANDS];
            float  _BandHidden[MAX_BANDS];
            float4 _Primer;
            float  _Wob;                    // surface wave amplitude (world units)
            float  _WaveK;                  // 2*PI / (1.15 w)
            float  _WavePhase;              // time_ms * 0.011
            float4 _GlossAxis;              // xy: world pos of local (-0.5,-H/2); zw: local (0.5,-H/2)
            float  _W;                      // vial width in world units
            float  _SeamW;                  // 1.2 world units
            float  _MeniscusW;              // max(1.2, 0.045 w)

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings  { float4 positionCS : SV_POSITION; float3 positionWS : TEXCOORD0; };

            Varyings vert(Attributes v)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(v.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                return o;
            }

            // CSS gradient: 0 white .30 | .24 white .10 | .55 transparent | 1 black .20
            float4 Gloss(float g)
            {
                if (g < .24) return float4(1, 1, 1, lerp(.30, .10, g / .24));
                if (g < .55) return float4(1, 1, 1, lerp(.10, 0, (g - .24) / .31));
                return float4(0, 0, 0, lerp(0, .20, (g - .55) / .45));
            }

            half4 frag(Varyings i) : SV_Target
            {
                int n = (int)_BandCount;
                if (n <= 0) discard;
                float2 p = i.positionWS.xy;
                float top = _BandTop[n - 1] + _Wob * sin(p.x * _WaveK + _WavePhase);
                float fw = max(fwidth(p.y), 1e-4);
                float edge = saturate((top - p.y) / fw + .5);          // anti-aliased surface
                if (edge <= 0) discard;

                int band = n - 1;
                [unroll] for (int k = 0; k < MAX_BANDS - 1; k++)
                    if (k < n - 1 && p.y <= _BandTop[k] && band == n - 1) band = k;

                float4 col = _BandColor[band];
                if (_BandHidden[band] > .5)
                {
                    col = _Primer;                                       // grey primer with a 45° hatch
                    float h = frac((p.x - p.y) / (.28 * _W));
                    if (h < .25) col.rgb = lerp(col.rgb, 1, .12);
                }
                float2 L = _GlossAxis.xy, R = _GlossAxis.zw, ax = R - L;
                float4 gl = Gloss(saturate(dot(p - L, ax) / dot(ax, ax)));
                col.rgb = lerp(col.rgb, gl.rgb, gl.a);

                [unroll] for (int s = 0; s < MAX_BANDS - 1; s++)          // seams between colours
                    if (s < n - 1 && abs(p.y - _BandTop[s]) < _SeamW * .5) col.rgb *= (1 - .13);

                if (abs((top - p.y) - 1) < _MeniscusW * .5)               // bright meniscus 1 unit under the surface
                    col.rgb = lerp(col.rgb, 1, .42);

                col.a = edge;
                return col;
            }
            ENDHLSL
        }
    }
}
```

Set the arrays every frame through a `MaterialPropertyBlock` with
`SetFloatArray`/`SetVectorArray`, **always with length 8** (Unity fixes an
array's size on first use).

### 8.5 Per-frame band upload (`LiquidBands.cs`)

For each visible vial:

1. Get the pose (resting §8.9 or pouring §9) and the bands: `BandsOf(i)` at
   rest; during a pour the source uses `TrimTop(srcBands, poured)` and the target
   uses `AddTop(dstBands, pigment, received)`. `TrimTop` removes an amount from
   the top bands (dropping emptied bands); `AddTop` merges into a visible
   top band of the same pigment or pushes a new band.
2. `poly = world polygon`, `minY`, `maxY`.
3. `acc = 0`; for each band `acc += units`;
   `top[b] = LevelFor(poly, acc * UnitA * w², minY - 1, maxY + 1)`.
4. Colours: pigment hex (§16.2), or `_Primer` for hidden bands.
5. Wobble: `_Wob = min(0.09w, wob)`, `_WaveK = 2π / (1.15w)`,
   `_WavePhase = timeMs * 0.011`.
6. `_GlossAxis`: world positions of local `(-0.5, -Hgeo/2)` and `(0.5, -Hgeo/2)`.

### 8.6 Symbols and question marks (`SymbolLayer.cs`)

One pooled SpriteRenderer per paint unit that needs a mark, using
`tex_symbols.png` (Appendix A).
- Hidden unit: cell 12 (question mark), world size `0.46w`, colour white α .82.
- Colour-blind mode on: visible units get the pigment's glyph (cell = pigment
  index), world size `1.3 × 0.34w`, colour = pigment ink (§16.2).
- Only whole units get a mark; skip everything when `|cos(phi)| < 0.4`.
- Position of the unit `u` (0-based from the bottom, counting all units below
  it): `Y = LevelFor(poly, (before + u + 0.5) * UnitA * w², ...)` and `X` = where
  the vial's centre line crosses `Y`:

```
s = Ly + (Y - P.y + Lx*w*sin(phi)) / (w*cos(phi))        // local y on the axis
X = P.x - Lx*w*cos(phi) - (s - Ly)*w*sin(phi)
```

### 8.7 Cork

`tex_cork` sprite, world size `0.8w × 0.6w`, pivot top-centre, local
position `y = +0.36w + drop` (so it sits from 0.36w above the mouth to 0.24w
inside). Shown only on full vials that are not animating. Drop animation over
520 ms from the moment the vial corks: `drop = (1 - easeOutBounce(t/520)) * 1.8w`.

### 8.8 Glows

- **Selected**: SelectGlow on, colour accent.
- **Corked**: `CompleteGlow` (fx_glow) sized `2.2w × (Hgeo + 0.6)w`, centred on
  the body, pigment colour, alpha `0.9 * sin(π t/1200)` for 1200 ms.

### 8.9 Motion (per vial, `dt` in ms)

| Property | Update |
| --- | --- |
| lift (target 0.5w when selected) | `lift += (target - lift) * min(1, dt * 0.022)`; frozen while the vial is in a pour |
| slot glide | `dx += (x - dx) * min(1, dt * 0.014)` (and y) |
| shake (0..1) | `shake = max(0, shake - dt / 320)`; offset `sx = sin(shake * 42) * shake * 0.22w`, rotation `-sx * 0.012` rad |
| wobble | `wob *= exp(-dt / 420)` |
| hop (win, restart) | `y += sin(π * t / 420) * 0.6w` for t in [0, 420] from its start time |
| pop-in (level start, add vial) | scale about the vial bottom, `easeOutBack(t / 380)`; level start staggers 35 ms per vial |

Rest pose: `P = (dx + sx, dy + lift + hop)`, `L = (0,0)`, `phi = -sx * 0.012`.

---

## 9. The pour animation

### 9.1 Timeline (`PourAnimation.cs`)

```
tA  = 230                    lift and swing over the target
tB  = 190 + 105 * n          pouring (n = units moved)
tC  = 280                    swing back
lag = 85                     stream travel time
v0  = source units before, v1 = v0 - n, d0 = target units before
dir = +1 if target.x > source.x + 1, -1 if target.x < source.x - 1, else (i < j ? +1 : -1)
thS = AngleFor(v0 * UnitA)
thE = v1 > 0 ? AngleFor(v1 * UnitA) : min(AngleFor(0.02 * UnitA) + 0.1, 2.05)
```

Poses (y-up; the pivot `L` is the lip, `(dir * 0.5, 0)` in local units):

```
home = (a.dx + dir*w/2, a.dy + lift0)       lift0 = source lift when tapped
rest = (a.x  + dir*w/2, a.y)
at   = (b.x  - dir*0.1w, b.y + 1.05w)       b = target mouth

A: t < tA          u = t/tA;           e = easeInOutCubic(u)
                   P = lerp(home, at, e) + (0, sin(π e) * 0.5w);   θ = thS * easeInOutSine(u)
B: t < tA + tB     u = (t - tA)/tB
                   P = at;                                         θ = thS + (thE - thS) * easeInOutSine(u)
C: otherwise       u = clamp((t - tA - tB)/tC, 0, 1);  e = easeInOutCubic(u)
                   P = lerp(at, rest, e) + (0, sin(π e) * 0.3w);   θ = thE * (1 - easeOutBack(u))
phi = -dir * θ
transform.position = P - Rot(phi) * (L * w);  transform.rotation = z(phi)
```

Paint amounts:

```
srcUnits(t) = t <= tA ? v0 : t >= tA + tB ? v1
            : clamp(CapAt(thS + (thE - thS) * easeInOutSine((t - tA)/tB)) / UnitA, v1, v0)
poured(t)   = v0 - srcUnits(t)
received(t) = clamp(poured(t - lag), 0, n)
```

The pour ends at `t >= tA + tB + tC`. Lock both vials until then. Several pours
may run at once on different vials.

### 9.2 Easing (`Easing.cs`)

```
easeInOutSine(t)  = -(cos(π t) - 1) / 2
easeInOutCubic(t) = t < .5 ? 4t³ : 1 - (-2t + 2)³ / 2
easeOutBack(t)    = 1 + 2.9 (t - 1)³ + 1.9 (t - 1)²
easeOutBounce(t)  = standard (n = 7.5625, d = 2.75)
```

### 9.3 Sound and haptics at pour time

At the tap: haptic 8, and schedule the glug train to start at `tA + lag` and
last `tB` (§13.6). At the end of the pour: plop for fill `d0 + n`.

---

## 10. The paint stream (`StreamRenderer.cs`, `Stream.shader`)

Active while `tA < e < tA + tB + lag` (`e` = time since the pour started).

```
lip       = pose P at min(e, tA + tB - 1)
end       = (b.x - dir*0.08w, sy)      sy = SurfaceY(target, d0 + received(e))
head      = clamp((e - tA) / lag, 0, 1)
tail      = e > tA + tB ? clamp((e - tA - tB) / lag, 0, 1) : 0
flow      = poured(e) - poured(e - 40)
width     = w * clamp(0.07 + flow * 1.05, 0.07, 0.27) * (e > tA + tB ? 1 - tail * 0.5 : 1)
ya        = lip.y + (sy - lip.y) * tail          yb = lip.y + (sy - lip.y) * head
xa        = lerp(lip.x, end.x, tail²)            xb = lerp(lip.x, end.x, head)
sway      = sin(timeMs * 0.03) * 0.015w
curve     = quadratic Bézier (xa, ya) → control (lip.x + dir*0.07w + sway, lerp(ya, yb, 0.3)) → (xb + sway, yb)
draw only when ya - yb > 1
```

`SurfaceY(j, units)` = `LevelFor(world poly of j at rest, units * UnitA * w²)`,
or the polygon's `minY` when `units <= 0.001`.

Mesh: 20 samples along the curve, ribbon of `width`, round caps (6-segment
fans), `uv.y` across (0 = left edge in screen space). `Stream.shader`: pigment
colour; where `0.17 < uv.y < 0.39`, blend white at α 0.38 (the highlight line);
alpha 1.

While the stream is flowing, the target's wobble stays at least 0.065w and
splashes spawn (§11).

---

## 11. Particles (`FxPool.cs`)

Pooled SpriteRenderers with `TintedSprite.shader`, updated by one script
(`ParticleSystem` isn't needed). All speeds are world units (= dp) per second,
converted from the web's px/ms. "Up" is +y.

| Kind | Texture | Spawn | Velocity | Gravity | Life | Size (radius) | Rotation / fade |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Splash burst | fx_droplet | 7 when the stream first lands, at `(end.x, sy)` | vx ±80, vy +120..+320 | −1200 | 380 | `w·(0.04..0.08)` | alpha `1 - q²`; dies when it falls below `sy` |
| Splash spray | fx_droplet | 1 per 38 ms on average while flowing, at `end.x ± 0.1w` | vx ±60, vy +70..+190 | −1200 | 300 | `w·(0.03..0.06)` | as above |
| Spark | fx_spark | `Sparkle(x, y, colour, count, power)` | random direction, speed `(80..300) · power`, plus vy +80 | −400; velocity × `0.985^(dt/16.67)` | 500..900 | `w·(0.07..0.15)`, shrinking to 40% | rotation `spin + 6 rad/s`; alpha `1 - q²` |
| Splat (win) | fx_splat | 46 at `(W/2 ± 0.15W, 0.45H below the field top)` | vx ±450, vy +450..+1000 | −1100 | 1300..2000 | `w·(0.08..0.20)` | rotation `spin + 4 rad/s`; alpha `min(1, (1 - q)·2.2)`; palette colours in turn |

`q` = life fraction. Sparkle calls: corking (§6.9); reveal (white ×8, power
0.7, at the source's new surface); add vial (white ×12, power 1, at the vial's
centre). Halve the counts when the device reports reduced motion.

The hint pointer (`HintPointer.cs`): a filled arrow pointing down, outlined
3 dp in `--surface`, fill `--accent`. Local points: `(0, −0.42w)`,
`(−0.34w, 0.02w)`, `(−0.13w, 0.02w)`, `(−0.13w, 0.42w)`, `(0.13w, 0.42w)`,
`(0.13w, 0.02w)`, `(0.34w, 0.02w)`. It sits at
`(dx, mouthY + lift + 0.95w + sin(timeMs·0.008)·0.14w)` over the source (over the
target once the source is selected). The target also gets a dashed rounded rect
(dash 4/5, width 2.5, radius 12, alpha `0.35 + 0.2·sin(timeMs·0.008)`) spanning
`slotW - 8` wide, from `mouthY + 0.5w` down by `(Hgeo + 0.9)w`.

---

## 12. Paintings

Every level has a small abstract painting with one shape per colour. It
starts as a pencil underdrawing, and each pigment brushes into its shape when
its vial is corked. Finished paintings are the win screen's centrepiece.

### 12.1 Pipeline

`ArtBuilder.Build(n, K)` (§5.9) → flatten paths into contours → build meshes in
`PaintingRig` → render with `PaintingCamera` into a RenderTexture (800 × 600,
ARGB32, MSAA 4, depth+stencil 24) → shown by a `RawImage` inside the frame.

`PaintingRenderer.Render(RenderTexture rt, List<ArtShape> art, int[] palette, float[] progress)`
applies the state and calls `PaintingCamera.Render()` manually. It is used for
the easel (every frame during a reveal, otherwise on change), the lobby preview
(all progress 0), the win sheet (all progress 1) and nowhere else.

### 12.2 Flattening (`PathFlattener`)

- Split into contours at each `MoveTo`; `Close` closes the current contour.
- `Arc`, with HTML canvas semantics: if not `Ccw` and `end - start >= 2π`, a full
  circle; otherwise the sweep is `(end - start) mod 2π` going clockwise in art
  space (increasing angle). With `Ccw`, sweep negative. Points:
  `(cx + r cos a, cy + r sin a)`. Segments: `max(12, ceil(|sweep| · r / 3))`.
  An arc following a current point on the same contour connects with a line
  (for `arch` that point already coincides).
- `Quad`: 16 segments.
- Convert every point to rig space: `(x, 300 - y)`.

### 12.3 Meshes per shape

- **Fill**: `ring` (even-odd) → build the annulus directly as a strip between its
  two circles. `dots` → one fan per circle. Everything else → ear-clip the single
  contour (`Triangulator`). `uv0` = art-space `(x, y)` (y-down) for the shader.
- **Streaks**: 10 quads (rounded caps) from `(sx, sy)` to
  `(sx + len·W·0.5, sy + (v − 0.5)·3)`, with `sx = X + u·W·0.7`, `sy = Y + v·H`
  (X, Y, W, H = the shape's bbox), width `lw`, colour pigment light or dark
  (§16.2).
- **Pencil**: closed ribbon along each contour, width 1.5, colour `#5F6474`.
  None for the ground.

### 12.4 `BrushReveal.shader` (fill)

Each shape's fill writes stencil ref `shapeIndex + 1` (Comp Always, Pass
Replace). Uniforms: `_Color`, `_Progress` (0..1), `_BB` (x, y, w, h in art space).
Renders in shape order so later shapes cover earlier ones.

```hlsl
// fragment; i.art = art-space position (y-down) from uv0
if (_Progress <= 0) discard;
if (_Progress >= 1) return _Color;
float x = _BB.x, y = _BB.y, w = _BB.z, h = _BB.w;
int   N = clamp((int)floor(h / 34.0 + .5), 2, 7);
float band = h / N, d = .55 / N, rad = (band * 1.4 + 6) * .5;
float cover = 0;
for (int k = 0; k < 7; k++)
{
    if (k >= N) break;
    float q = saturate((_Progress - k * d) / (1 - (N - 1) * d));
    if (q <= 0) continue;
    float e  = 1 - pow(1 - q, 2.2);
    float yy = y + (k + .5) * band;
    bool  ltr = (k % 2) == 0;
    float x0 = ltr ? x - 14 : x + w + 14;
    float x1 = x0 + (ltr ? 1 : -1) * (w + 28) * e;
    float t  = saturate((i.art.x - x0) / (x1 - x0 + 1e-5));
    float cy = yy + 2 * t * (1 - t) * (ltr ? -5 : 5);        // the brush sags slightly mid-stroke
    float dx = max(max(min(x0, x1) - i.art.x, 0), i.art.x - max(x0, x1));
    float dist = sqrt(dx * dx + (i.art.y - cy) * (i.art.y - cy));
    cover = max(cover, saturate(rad - dist + .5));
}
if (cover <= 0) discard;
return float4(_Color.rgb, _Color.a * cover);
```

### 12.5 Streaks, pencil, ground

- **Streaks** (`StencilColor.shader`): stencil Comp Equal to their shape's ref,
  alpha `0.28 · min(1, 1.2 · progress)`; hidden when progress is 0. Draw each
  shape's streaks right after its fill.
- **Pencil** (`UnlitColor`): drawn after all fills, alpha `0.55 · (1 − progress)`,
  hidden at progress 1.
- **Ground**: quad `#F3F0E8`; over it the `tex_canvas_tooth` quad tiled so one
  tile is 8 art units.
- **Reveal timing**: progress for a pigment goes 0 → 1 linearly over 900 ms,
  starting 120 ms after the pour that corked it ends. Un-corking (undo, restart)
  sets it back to 0 at once.

### 12.6 Frame

UI `Image` with `tex_frame_{light,dark}` (9-slice), 5 dp border, the RawImage
inset 5 dp; behind it `tex_frame_shadow` (9-slice), offset 12 dp down. Easel
frame height `clamp(76, 15.5% of screen height, 142)` dp, aspect 4:3.

---

## 13. Sound (synthesised at edit time)

All sounds are generated by `Playbox/Generate/Audio` into
`Assets/_Project/Audio/Generated/` as 44.1 kHz mono 16-bit WAV. The recipes
reproduce the web prototype's Web Audio synth.

### 13.1 Primitives (semantics to reproduce exactly)

**Tone** `{f, f1?, glide?, dur=.12, gain=.25, attack=.004, at=0, type=sine, filter?, ff=1200, q=.8}`
- Frequency: `f` at `at`; if `f1`, exponential glide to `f1` over `glide`
  (default `dur`), then holds `f1`.
- Gain envelope: `0.0001` at `at` → exponential to `gain` at `at + attack` →
  exponential to `0.0001` at `at + dur`; silent after. Voice ends at `dur + .05`.
- Oscillators: sine; triangle; square and sawtooth with PolyBLEP anti-aliasing.
- Optional biquad (lowpass/bandpass/highpass) at `ff` with `q`.

**Noise** `{dur=.15, gain=.15, filter=bandpass, f=1000, f1?, q=1, at=0, attack=.004, rate=1}`
- Seeded white noise read at `rate` samples per sample with linear
  interpolation (Web Audio `playbackRate`).
- Filter frequency `f` → exponential to `f1` over `dur` (coefficients refreshed
  every 32 samples). Same envelope as Tone.

**Bell** `(f, at, gain=.18)` = Tone(f, dur 1.1, gain, attack .003) +
Tone(f·2.76, dur .45, gain·.35, attack .002) + Tone(f·5.4, dur .2, gain·.12,
attack .002).

**Biquad** (Web Audio formulas): `w0 = 2π f / sr`;
lowpass/highpass `α = sin w0 / (2·10^(q/20))` (Q in dB); bandpass
`α = sin w0 / (2q)` (0 dB peak).
- lowpass: `b = [(1−cos)/2, 1−cos, (1−cos)/2]`
- highpass: `b = [(1+cos)/2, −(1+cos), (1+cos)/2]`
- bandpass: `b = [α, 0, −α]`
- `a = [1+α, −2cos, 1−α]`, normalise by `a0`.

**Master**: mix × 0.7 → compressor (threshold −16 dB, knee 14 dB, ratio 5,
attack 2 ms, release 160 ms, peak detector, soft knee) → trim to the last voice's
end + 50 ms, 5 ms fade-out. After rendering **all** clips, scale every clip by one
global factor so the loudest clip in the library peaks at −1 dBFS (keeps relative
loudness).

**Determinism**: each clip's noise and jitter use `Mulberry32(fnv1a(clipName))`,
so regenerating produces identical files.

### 13.2 `Synth.cs` (core)

```csharp
public enum Wave { Sine, Triangle, Square, Saw }
public enum Filt { None, Lowpass, Bandpass, Highpass }

public sealed class Synth
{
    public const int SR = 44100;
    readonly float[] _mix = new float[SR * 4];
    int _end;
    readonly Mulberry32 _rng;
    public Synth(string clipName) { _rng = new Mulberry32(Fnv1a(clipName)); }
    public double Rand() => _rng.Next();

    static double Env(double t, double peak, double attack, double dur)
    {
        if (t < attack) return 1e-4 * Math.Pow(peak / 1e-4, t / attack);
        if (t < dur) return peak * Math.Pow(1e-4 / peak, (t - attack) / (dur - attack));
        return 0;
    }
    static double PolyBlep(double t, double dt)
    {
        if (t < dt) { t /= dt; return t + t - t * t - 1; }
        if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; }
        return 0;
    }
    static double Osc(Wave w, double ph, double dt) => w switch
    {
        Wave.Sine => Math.Sin(2 * Math.PI * ph),
        Wave.Triangle => 1 - 4 * Math.Abs(ph - .5),
        Wave.Square => (ph < .5 ? 1 : -1) + PolyBlep(ph, dt) - PolyBlep((ph + .5) % 1, dt),
        _ => 2 * ph - 1 - PolyBlep(ph, dt),
    };
    void Add(int i, double s) { if (i < 0 || i >= _mix.Length) return; _mix[i] += (float)s; if (i + 1 > _end) _end = i + 1; }

    public void Tone(double f, double f1 = 0, double glide = 0, double dur = .12, double gain = .25, double attack = .004,
                     double at = 0, Wave type = Wave.Sine, Filt filter = Filt.None, double ff = 1200, double q = .8)
    {
        int start = (int)(at * SR), len = (int)((dur + .05) * SR);
        double gl = glide > 0 ? glide : dur, ph = 0;
        var bq = filter == Filt.None ? null : new Biquad(filter, q, SR);
        bq?.SetFreq(ff);
        for (int n = 0; n < len; n++)
        {
            double t = (double)n / SR;
            double fr = f1 > 0 ? (t < gl ? f * Math.Pow(f1 / f, t / gl) : f1) : f;
            double dt = fr / SR, s = Osc(type, ph, dt);
            ph += dt; if (ph >= 1) ph -= 1;
            if (bq != null) s = bq.Process(s);
            Add(start + n, s * Env(t, gain, attack, dur));
        }
    }

    public void Noise(double dur = .15, double gain = .15, Filt filter = Filt.Bandpass, double f = 1000, double f1 = 0,
                      double q = 1, double at = 0, double attack = .004, double rate = 1)
    {
        int start = (int)(at * SR), len = (int)((dur + .05) * SR);
        var bq = new Biquad(filter, q, SR);
        double pos = 0, a = Rand() * 2 - 1, b = Rand() * 2 - 1;
        for (int n = 0; n < len; n++)
        {
            double t = (double)n / SR;
            if (n % 32 == 0) bq.SetFreq(f1 > 0 ? (t < dur ? f * Math.Pow(f1 / f, t / dur) : f1) : f);
            pos += rate; while (pos >= 1) { pos -= 1; a = b; b = Rand() * 2 - 1; }
            double s = bq.Process(a + (b - a) * pos);
            Add(start + n, s * Env(t, gain, attack, dur));
        }
    }

    public void Bell(double f, double at, double gain = .18)
    {
        Tone(f, dur: 1.1, gain: gain, attack: .003, at: at);
        Tone(f * 2.76, dur: .45, gain: gain * .35, attack: .002, at: at);
        Tone(f * 5.4, dur: .2, gain: gain * .12, attack: .002, at: at);
    }

    /// Master gain, compressor, trim, fade. Library-wide normalisation happens afterwards.
    public float[] Render()
    {
        int len = Math.Min(_mix.Length, _end + (int)(.05 * SR));
        var o = new float[len];
        for (int i = 0; i < len; i++) o[i] = _mix[i] * .7f;
        Compressor.Apply(o, SR, thresholdDb: -16, kneeDb: 14, ratio: 5, attack: .002, release: .16);
        int fade = (int)(.005 * SR);
        for (int i = 0; i < fade && i < len; i++) o[len - 1 - i] *= (float)i / fade;
        return o;
    }

    static uint Fnv1a(string s) { uint h = 2166136261; foreach (char c in s) { h ^= c; h = unchecked(h * 16777619); } return h; }
}
```

`Compressor.Apply`: peak envelope follower (`attack`/`release` one-pole
coefficients `exp(-1/(τ·sr))`), level in dB, soft-knee gain computer
(`over ≤ −knee/2 → 0 dB`; `over ≥ knee/2 → over/ratio − over`; in between
`(1/ratio − 1)·(over + knee/2)²/(2·knee)`), apply the gain per sample.
`WavWriter`: RIFF/WAVE, PCM 16-bit, mono, 44100, samples clamped to [−1, 1].

### 13.3 Import settings (`AudioImportRules`)

For `Audio/Generated/*.wav`: Force To Mono, Load In Background off, Load Type
Decompress On Load, Compression PCM, Preload Audio Data on.

### 13.4 Recipes (`SfxRecipes.cs`)

`note(base, semitones) = base · 2^(semitones/12)`.
`PENTA = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28]`.

| File | Recipe |
| --- | --- |
| `sfx_click.wav` | Tone(f 900, f1 1300, dur .05, gain .08, triangle) |
| `sfx_pick.wav` | Tone(f 1568, dur .06, gain .05, triangle) + Tone(f 480, f1 860, dur .10, gain .13) |
| `sfx_drop.wav` | Tone(f 720, f1 430, dur .09, gain .09) |
| `sfx_bonk.wav` | Tone(f 190, f1 105, dur .18, gain .22, square, lowpass ff 650) + Tone(f 2400, dur .05, gain .04, triangle) |
| `sfx_tink.wav` | Tone(f 2093, dur .14, gain .07, triangle) + Tone(f 3136, dur .10, gain .03, triangle, at .04) |
| `sfx_bubble_00..11.wav` | one glug: Tone(f = 210·2^(1.45·k/11), f1 = f·1.95, glide .045, dur .09, gain .215, attack .003) for k = 0..11 |
| `sfx_pour_hiss_1..4.wav` | the pour bed for n units: Noise(lowpass, f 700, f1 1500, dur = (190 + 105n)/1000 + .1, gain .045, attack .06, rate .55) |
| `sfx_plop_1..4.wav` | fill m = 1..4: f = 260·2^(m/4); Tone(f, f1 f·.55, dur .11, gain .12) |
| `sfx_complete_00..12.wav` | corked vial k: Noise(bandpass f 1700, q 2.2, dur .05, gain .30) + Tone(f 640, f1 170, dur .08, gain .20) + Bell(note(523.25, PENTA[k]), at .07, gain .15) + Bell(2·that, at .15, gain .06) |
| `sfx_reveal.wav` | Tone(f 990, f1 1480, dur .12, gain .07, triangle) + Tone(f 1480, dur .10, gain .04, triangle, at .06) |
| `sfx_undo.wav` | Noise(bandpass f 2600, f1 480, q 1.4, dur .22, gain .12) + Tone(f 700, f1 420, dur .14, gain .06) |
| `sfx_hint.wav` | Bell(note(880, s), at i·.06, gain .07) for (i, s) in [0, 4, 7, 12] |
| `sfx_vial.wav` | Bell(1318.5, 0, .10) + Bell(1975.5, .08, .06) + Tone(f 280, f1 900, dur .28, gain .07) |
| `sfx_win.wav` | Bell(note(523.25, s), at i·.085, gain .15) for s in [0, 4, 7, 12, 16, 19] + Noise(highpass f 5500, dur .9, gain .04, at .4, attack .1) + Tone(f 130.8, f1 131, dur .9, gain .12, triangle, at .5) |
| `sfx_coin.wav` | Tone(f 1318.5, dur .06, gain .05, square, lowpass ff 3800) + Tone(f 1975.5, dur .12, gain .05, square, lowpass ff 3800, at .05) |
| `sfx_hard_intro.wav` | Tone(f 140, f1 48, dur .4, gain .40) + Noise(lowpass f 400, dur .2, gain .20) + Tone(f 140, f1 48, dur .4, gain .35, at .22) + Noise(lowpass f 400, dur .2, gain .18, at .22) + for (i, s) in [0, 3, 7]: Tone(note(196, s), dur 1.1, gain .07, saw, lowpass ff 900, at .44 + i·.02, attack .08) |
| `sfx_superhard_intro.wav` | same as above with chord [0, 3, 6, 10] |

### 13.5 Generated audio files

46 files: `sfx_click`, `sfx_pick`, `sfx_drop`, `sfx_bonk`, `sfx_tink`,
`sfx_bubble_00`–`11`, `sfx_pour_hiss_1`–`4`, `sfx_plop_1`–`4`,
`sfx_complete_00`–`12`, `sfx_reveal`, `sfx_undo`, `sfx_hint`, `sfx_vial`,
`sfx_win`, `sfx_coin`, `sfx_hard_intro`, `sfx_superhard_intro`. `GenerateAudio`
also fills `SfxLibrary.asset` (SfxId → clips).

### 13.6 Runtime playback (`SfxPlayer.cs`, `PaintSortSfx.cs`)

`SfxPlayer`: 16 pooled 2D `AudioSource`s; `Play(id, variant, volume, pitch,
delaySeconds)`. Delayed sounds use
`PlayScheduled(AudioSettings.dspTime + delay)`. Muted when sound is off.

**Glug train** (the pour sound) at the tap:

```
count = max(3, round(tB / 58))
for k in 0..count-1:
    frac   = (d0 + n * (k + .5) / count) / 4            // how full the target will be
    fWant  = 210 * 2^(frac * 1.45) * rand(.93, 1.07)
    kClip  = round(11 * log2(fWant / 210) / 1.45) clamped 0..11
    pitch  = fWant / (210 * 2^(1.45 * kClip / 11))
    volume = rand(.19, .24) / .215
    delay  = (tA + lag + k * tB / count + rand(0, 16)) / 1000
    play sfx_bubble_kClip
play sfx_pour_hiss_n at delay (tA + lag) / 1000
```

Pitch rises through the pour because the target is filling, which is what
makes it sound like a bottle filling up.

| Game event | Sound |
| --- | --- |
| UI button | click |
| select / deselect | pick / drop |
| tap empty or corked vial | tink |
| illegal pour | bonk |
| pour | glug train + hiss (above) |
| pour ends | plop `d0 + n` |
| hidden paint revealed | reveal (at pour end) |
| vial corked | complete `k` (150 ms after the pour ends) |
| undo, restart | undo |
| hint shown | hint |
| extra vial | vial |
| stuck bar appears | bonk |
| win | win |
| coin count-up | coin per tick (every 55 ms); buying: coin ×3 at 0, 55, 110 ms |
| hard / super hard intro | hard_intro / superhard_intro |

---

## 14. Haptics

`IHaptics.Pulse(ms)` / `Pattern(long[] onOff)`; no-op when vibration is off.

- **Android** (`AndroidHaptics`): `Vibrator` from the activity;
  API 26+: `VibrationEffect.createOneShot(ms, DEFAULT_AMPLITUDE)` /
  `createWaveform(timings, -1)`; older: `vibrate(ms)` / `vibrate(pattern, -1)`.
- **iOS** (`Plugins/iOS/PlayboxNative.mm`, generated): `_PlayboxImpact(int style)`
  using `UIImpactFeedbackGenerator` (0 light, 1 medium, 2 heavy) and
  `_PlayboxIsDarkMode()` returning `UITraitCollection.currentTraitCollection.userInterfaceStyle == UIUserInterfaceStyleDark`.
  Map a pulse to light (< 10 ms), medium (< 20 ms) or heavy; a pattern fires one
  impact per "on" segment on a timer.

| Event | Pattern |
| --- | --- |
| select | 6 |
| pour | 8 |
| illegal pour | [18, 30, 18] |
| undo | 10 |
| extra vial | 12 |
| vial corked | [12, 30, 16] |
| hard intro | [30, 60, 30] |
| win | [20, 60, 20, 60, 40] |

---

## 15. UI layouts

uGUI + TextMeshPro. Sizes are dp (§2). Display text uses the display font
style (heavy, rounded); body text the body style. Colours are theme tokens
(§16.1) bound through `ThemedGraphic`, so light/dark switches live. All Images
take their sprite from `UiSkin`; any empty slot uses the generated primitives
(`ui_round_24`, `ui_circle`, `ui_soft_shadow`).

### 15.1 Hub

```
HubScreen (safe area, padding 18, scroll)
├─ TopRow: Wordmark "Playbox" (34, display) · spacer · Settings icon button (42×42, radius 14, surface)
├─ Greeting: title (clamp 28–36, display) + subtitle (15, muted)
├─ Label "GAMES" (12, letter-spacing .14em, dim)
├─ Shelf (vertical, gap 14)
│  └─ GameCard (radius 26, surface, shadow)
│     ├─ Art (height 190): RawImage of the card RenderTexture
│     └─ Body (padding 16/18): Title (26 display) · Tagline (14 muted) · Status chip (accent-soft pill) · Play button (54×54, radius 18, accent)
└─ Note (13.5, dim, centred): "More games will land on this shelf. Your progress in each one is saved on this device."
```

**Card art** (`CardArtRig`, rendered once per theme change into a
394 × 190 dp RT at device scale). Uses Vial prefabs on the CardArt layer and
the wall gradient. `w = min(36, W/11)`; mouths at `y = 0.55w + Hgeo·w` above the
bottom; vials at `x/W` = 0.10 `[Ultramarine, Cadmium Red, Hansa Yellow, Ultramarine]`,
0.24 `[Hansa Yellow, Quinacridone Rose, Cadmium Red]`,
0.62 `[Cadmium Red ×2, Hansa Yellow ×1.35]`, 0.78 `[Ultramarine ×4, corked]`,
0.91 `[Quinacridone Rose ×2, Sap Green]`; a fifth vial tipped 1.18 rad clockwise
with its lip at `(0.62W − 0.1w, mouth + 0.62w)` holding
`[Sap Green, Hansa Yellow ×0.7]`, and a Hansa Yellow stream (width 0.2w) from
that lip into the 0.62 vial's surface with three droplets.

### 15.2 Paint Sort lobby

```
LobbyScreen (safe area; wall gradient behind)
├─ TopBar (padding 12/16): Back · spacer · Coin pill (coin count) · Settings
└─ Body (scroll, padding 8/18, gap 18)
   ├─ Wordmark "Paint " + "S","o","r","t" in Cadmium Red, Hansa Yellow, Cerulean, Sap Green (54 display, each letter with a 3 dp darker drop)
   ├─ NextCard (radius 22, padding 14, surface, shadow; horizontal gap 16)
   │  ├─ Frame (44% width, 4:3) → RawImage: next level's painting at progress 0
   │  └─ Meta: eyebrow "Up next" / "Up next · Hard" / "Up next · Super hard" (11.5, tier colour)
   │           title "Study No. N" (24 display) · sub "K colours · K+2 vials[ · some hidden]" (13.5 muted)
   │           pigment dots (blank rings until the level has started)
   ├─ RoadCard (radius 22, padding 14): header "Levels a–b" (19 display) + key (Hard ● Super hard ●) · LevelRoadGraphic (width 100%, aspect 340:136)
   ├─ PlayButton (full width, 19 display): "Play level N" or "Continue level N"; style primary / hard / super by tier
   └─ Note (13.5 muted, centred): stats line, or "Every level is mixed fresh on your device. Levels 5 and 10 of each ten are the hard ones."
```

### 15.3 Play screen

```
PlayScreen (wall gradient by tier)
├─ TopBar: Back · Level column ("Level N" 24 display; tier badge under it: 10 bold caps, white on hard/super, radius 999) · spacer · Coin pill · Menu
├─ Easel: Frame (§12.6) + PigmentDots (11 dp rings, 2 dp pigment ring + 1 dp edge outline; filled and scaled 1.15 when corked, 300 ms)
├─ CoachLine (min height 40, 14.5 bold muted, centred, balanced wrap)
├─ FieldArea (flex; the board renders here; FloatLabels live here)
├─ StuckBar (hidden; radius 16, surface, shadow; rises in 300 ms): "No way out from here" (bad colour, 14 bold) · Undo · Add vial · Restart (small ghost buttons)
├─ BoosterBar (padding 6/12 + bottom safe area; 4 columns)
│  └─ BoosterButton ×4 (72 wide): icon tile 56×56 radius 19 surface with a 4 dp line-coloured drop; label (12 bold muted);
│     count badge top-right (23 high, accent; shows "+" on a coin-coloured badge when empty and buyable); "used" state at 45% opacity
│     order: Restart · Undo (undos left) · Hint (inventory) · Add vial (inventory; "used" after one this level)
└─ HardIntro overlay (§15.6)
```

### 15.4 `LevelRoadGraphic`

Custom `Graphic` drawing in a 340 × 136 box, scaled to its rect:
- `X(p) = 22 + p·296/9`, `Y(p) = 104 − Ramp[p]/3.6·76` (y-down in the box).
- Polyline through all ten nodes (4 dp, `--line`, round joins); overlay polyline
  through completed nodes plus the current one (4 dp, `--accent`).
- Node radius 9 (normal), 11.5 (hard), 13 (super). Done: filled in accent (hard:
  `--hard`, super: `--super`) with a white check. Current: surface fill, 4 dp
  accent ring (tier colour on hard/super), plus a pulse ring (radius + 6, 2 dp,
  scale 0.7 → 1.25 and alpha 0.7 → 0 over 1.6 s, looping). Upcoming: surface fill,
  3 dp ring in `--line` (tier colour on hard/super).
- Level numbers under nodes (`Y + 24`, +3 on hard/super), 11 bold, dim; the
  current one in ink, 800 weight.

### 15.5 Sheets

`SheetHost`: one sheet at a time; the scrim fades over 260 ms to `--scrim`; the
sheet slides up over 360 ms (cubic-bezier .2, .9, .25, 1). Radius 28 on top,
padding 12/20 + bottom safe area, max height 92%, scrolls. Layout: grab handle
(42×5) · eyebrow (11.5, caps, .14em, accent or tone colour) · title (30 display)
· sub (15 muted) · body · actions (vertical, gap 10; primary 19 display with a
5 dp darker drop; ghost 16). Tapping the scrim closes it unless the sheet is
non-dismissable.

### 15.6 Hard intro

Full-screen overlay: background `--hard` darkened 12% (super: `--super` darkened
15%) with `ui_stripes` tiled at 5% black (7% for super). Card centred: kicker
"Hard level" / "Super hard level" (clamp 40–56 display, white, 4 dp dark drop),
"LEVEL N" (13 bold caps .14em, 85% white), "K colours[, some hidden]. Worth R
coins." (16). Animation: the card scales 2.2 → 1 and rotates −6° → 0 over 550 ms
with overshoot; the overlay's alpha is 0 → 1 over the first 8% of 2.1 s, holds to
85%, fades to 0. Tap or 2.1 s dismisses. Plays the intro sound and haptic.

### 15.7 Float label

At `(vial x, mouth y + 1.1w)` projected to the canvas: pigment name, 17 display,
pigment colour, 5 dp outline in `--surface`. Over 1.5 s: 0% alpha 0, scale 0.6,
y +10%; 15% alpha 1, scale 1.08, y −60%; 75% alpha 1, scale 1, y −120%; 100%
alpha 0, y −160% (percent of its own height, upward).

### 15.8 Sheets content

| Sheet | Eyebrow / title / body | Actions |
| --- | --- | --- |
| Win | eyebrow "Level N complete" (or "Hard level beaten" / "Super hard level beaten" in tier colour); title by tier (§16.3); body: framed painting (height min(25% screen, 210)), caption "Study No. N · K pigments · M pours", coin row counting up to the reward in steps of `max(1, round(total/12))` every 55 ms starting after 350 ms, plus " incl. 5 for no boosters" when clean. Not dismissable. | "Next level" (or "Next: hard level N+1" / "Next: super hard level N+1", styled by tier) · "Back to levels" |
| Pause (menu) | "Level N" / "Paused"; toggles: Colour symbols, Sound, Vibration | Resume · How to play · Restart level · Back to levels |
| Restart | "Level N" / "Start this level again?" / "The board goes back to how it started. Your 5 undos come back too." | Restart level · Keep playing |
| Buy | "Boosters" / "Out of undos" · "Out of hints" · "Out of spare vials" / description (§16.3); if short of coins append "It costs P coins and you have C. Levels pay 10, hard ones 30 and super hard ones 60." | "Buy 5 undos · 30 coins" / "Buy a hint · 40 coins" / "Buy a vial · 90 coins" (disabled if short) · Not now |
| How to play | "How to play" / "Sort the paint" / five rows (§16.3) | Got it |
| Hidden paint tip (first level with hidden paint, after the intro) | "New" / "Hidden paint" / "Grey layers with a question mark are paint you can’t see yet. Pour off whatever sits on top and the colour shows." | Got it |
| Settings | "Settings" / "Options"; rows: Sound ("Every sound is synthesised live"), Vibration ("On phones that support it"), Theme segmented Auto/Light/Dark ("Auto follows your device"), Colour symbols ("Adds a shape to every colour of paint"); "Erase all saved progress" (bad colour) → confirm sheet "Erase progress" / "Start every game from scratch?" / "Levels, coins and boosters in every Playbox game go back to zero. Settings stay." with "Erase everything" / "Keep my progress" | Done |

Toast: pill at the top (76 dp + safe area), ink background, bg-coloured text,
14 bold, visible 1.9 s, fades 200 ms.

---

## 16. Theme, pigments and strings

### 16.1 Theme tokens (`ThemePalette.asset`)

| Token | Light | Dark |
| --- | --- | --- |
| bg | #EEF1F6 | #0E1220 |
| bg-2 | #E1E6EF | #080B15 |
| surface | #FFFFFF | #181E31 |
| surface-2 | #F4F6FA | #1F2740 |
| ink | #141A2B | #EDF0F8 |
| muted | #586079 | #A2AAC4 |
| dim | #8E96AE | #6B7494 |
| line | #D9DFEA | #2A3350 |
| accent | #2B59F0 | #7090FF |
| accent-ink | #FFFFFF | #0B1024 |
| accent-deep | #1B3FB8 | #4A63C9 |
| accent-soft | #E3EAFE | #1F2A52 |
| good | #16935D | #3DCB8B |
| bad | #D92F45 | #FF6275 |
| hard / hard-deep | #E0413F / #A92A2B | #FF5E5B / #B83533 |
| super / super-deep | #8646E0 / #5E2BA6 | #B07CFF / #7446BD |
| coin / coin-edge | #F4B31B / #C27F06 | #FFC83D / #B98609 |
| scrim | rgba(16,22,40,.46) | rgba(0,0,0,.60) |
| ps-wall-a / ps-wall-b | #EEF3F9 / #D3DDEA | #1B2442 / #0B0F1C |
| ps-hard-a / ps-hard-b | #FCECE9 / #F1C5C0 | #3B1620 / #15080D |
| ps-super-a / ps-super-b | #F3EAFD / #D8C3F3 | #2C1A4B / #110A21 |
| ps-glass | rgba(214,227,243,.60) | rgba(160,186,232,.10) |
| ps-edge | rgba(48,64,100,.62) | rgba(198,216,250,.62) |
| ps-hi | rgba(255,255,255,.90) | rgba(255,255,255,.50) |
| ps-floor | rgba(30,44,80,.16) | rgba(0,0,0,.40) |
| ps-primer | #7A8294 | #5F677B |
| ps-frame / ps-frame-2 | #8A5B36 / #5C3A20 | #8F633F / #4C301B |

The board backdrop (`Gradient.shader`) runs from wall-a at the top to wall-b at
the bottom; hard levels use the hard pair, super hard the super pair.
**Auto** theme: Android reads `Configuration.uiMode & UI_MODE_NIGHT_MASK` via
JNI, iOS calls `_PlayboxIsDarkMode()`; re-check on application focus.

### 16.2 Pigments (`Pigments.asset`)

| # | Name | Hex | Glyph (colour-blind symbol) |
| --- | --- | --- | --- |
| 0 | Cadmium Red | #E23A3F | circle |
| 1 | Cadmium Orange | #F5862B | triangle |
| 2 | Hansa Yellow | #F7CF36 | square |
| 3 | Sap Green | #45A646 | diamond |
| 4 | Viridian | #10A08F | 5-point star |
| 5 | Cerulean | #3AAEEA | plus |
| 6 | Ultramarine | #3448D0 | 4-point star |
| 7 | Dioxazine Violet | #7D44CF | 6-point star (blunt) |
| 8 | Quinacridone Rose | #E0489B | ring |
| 9 | Burnt Sienna | #9A5431 | bar |
| 10 | Titanium White | #F3F1EA | two dots |
| 11 | Payne's Grey | #343B4D | half disc |

Derived per pigment:
- `light` = mix toward white by 0.32, `dark` = mix toward black by 0.28
  (`c + (target − c)·amount` per channel, rounded).
- `ink` (glyph colour) = `rgba(30,30,40,.72)` when `0.299r + 0.587g + 0.114b > 150`,
  otherwise `rgba(255,255,255,.9)`.

### 16.3 Strings

- Win titles: normal `["Lovely.", "Clean pours.", "Framed.", "Gallery ready."][N % 4]`;
  hard "That was a tough one."; super hard "Masterpiece."
- Buy descriptions: undos "Take back 5 more pours on this try."; hint "A hint
  points at one pour that still leads to a finished board."; vial "An empty vial
  gives you room to park paint. One per level."
- How to play rows:
  1. "Tap a vial, then tap another" — "The top colour pours across. It lands only on the same colour, or in an empty vial, and only as much as fits."
  2. "Fill a vial with one colour" — "It gets corked, and that pigment paints its part of the picture above."
  3. "Grey paint is hidden" — "A question mark hides a colour until the paint above it has been poured off."
  4. "Boosters" — "Undo takes back a pour (5 per try). A hint points at a pour that still wins. An extra vial gives you room, once per level."
  5. "Hard levels" — "Levels 5 and 10 of every ten are harder, then the next level eases off. They pay 30 and 60 coins."
- Toasts: "Nothing to undo yet", "One extra vial per level", "No pour wins from
  here. Undo or restart.", "5 more undos", "Progress erased".
- Lobby stats line: "X painting(s) finished · Y hard level(s) beaten".
- Home card status: `level > 1 ? "Level L · C coins" : "New · 120 coins to start"`.
  Home greeting: after a game has been played "Welcome back" / "Paint Sort is
  right where you left it."; otherwise "Pick a game" / "Short puzzles that
  remember where you left off."
- Game tagline: "Pour paint between vials until each one holds a single colour."

---

## 17. Save system (`SaveService.cs`)

One JSON file, `Application.persistentDataPath/playbox.json`, serialised with
Newtonsoft. Writes are debounced by 150 ms and atomic (write `playbox.json.tmp`,
then replace). Flush immediately on a win, on `OnApplicationPause(true)` and on
`OnApplicationQuit`. A corrupt or missing file loads defaults.

```json
{
  "v": 1,
  "settings": { "sound": true, "haptics": true, "theme": "system" },
  "last": "paint-sort",
  "games": {
    "paint-sort": {
      "level": 14, "coins": 185,
      "inv": { "hint": 3, "vial": 2 },
      "symbols": false,
      "tips": { "tut": true, "mystery": false },
      "stats": { "won": 13, "hard": 1, "super": 1 },
      "cur": {
        "n": 14, "colorOf": [10, 2], "palette": [10, 2, 4],
        "vials": [[0, 1, 2, 3]], "rev": [3], "init": [[0, 1, 2, 3]], "rev0": [3],
        "hist": [ { "v": [[0, 1, 2, 3]], "m": 0 } ],
        "undos": 5, "moves": 3, "extra": false, "help": false
      }
    }
  }
}
```

The current board (`cur`) is saved after every pour, undo, restart and booster,
so a killed app resumes on the same board. The Play button says "Continue level
N" when `cur.n == level`. "Erase all saved progress" clears `games` and `last`
and keeps `settings`.

---

## 18. Threading and performance

- `LevelCache` generates levels on the thread pool (`Task.Run`) and caches
  `GeneratedLevel` by n. Request `level` when the lobby opens and `level + 1`
  900 ms after a win. If Play is tapped before the result is ready, show the
  play screen with "Mixing paint…" and start when it arrives.
- Solver calls (hint 30000, dead end 5000, tutorial 4000) run on the thread
  pool with a state version; results come back through `MainThread` and are
  dropped if the version changed.
- The engine is allocation-heavy but short-lived; never call it in `Update`.
- Budget per frame on a mid Android phone: ≤ 16 ms with 15 vials and 2 pours
  animating. `LevelFor` is 22 bisections over a 20-point polygon; only recompute
  bands for vials whose pose or contents changed, or that are wobbling.
- Stop redrawing the painting RT when no reveal is running.

---

## 19. Editor tooling

### 19.1 Generators (`Playbox/Generate/...`)

- **All** — runs Textures then Audio, then refreshes `SfxLibrary.asset`.
- **Textures** — writes every PNG in Appendix A with import settings (sprite or
  default, wrap, filter bilinear, no mipmaps for UI, 9-slice borders set in the
  sprite meta).
- **Audio** — renders §13.4, normalises the library (§13.1), writes WAVs.

`Raster.cs`: an anti-aliased signed-distance rasteriser. For each pixel centre,
compute the signed distance `d` to the shape in pixels and set coverage
`clamp(0.5 − d, 0, 1)`. Shapes: circle, ellipse, rounded rect, capsule
(segment + radius), convex/concave polygon (winding test + edge distance),
annulus. Composite layers with straight alpha "over". Gaussian blur (separable)
for shadows and glows.

### 19.2 Builders (`Playbox/Build/...`)

- **Prefabs** — creates every prefab in §4.1 with materials, sorting orders,
  layers and pool sizes.
- **Scenes** — creates Boot, Hub and PaintSort (§4.2), with canvases, the
  hierarchies in §15, references wired, and adds them to Build Settings in that
  order.

### 19.3 Balance probe

- **Window** `Playbox/Paint Sort/Balance Probe`: from/to fields, Run, a table
  (level, tier, colours, hidden, moves, casual, skilled, difficulty bar, ms),
  "all solvable" check (re-solve each board with budget 400000), CSV export.
- **CLI**: `Unity -batchmode -quit -projectPath . -executeMethod
  Playbox.Editor.ProbeCli.Run -from 1 -to 60`, printing the same columns as
  Appendix B.2, then `all solvable: yes|NO (count)` and the mean difficulty per
  tier. Exit code 1 if any level is unsolvable.

---

## 20. Tests

**EditMode**
- `EngineParityTests`: every value in Appendix B.1 (seeds, RNG streams,
  `Spec`, `Generate` vials/palette/hidden/len for the listed levels, first solver
  moves, painting kinds/slots/bbox).
- `CurveTests`: Appendix B.2 rows reproduce exactly (colours, hidden count,
  moves, casual, skilled) for levels 1–30.
- `SolvabilityTests`: levels 1–200 all solve with budget 400000; no level
  starts solved; every vial holds ≤ 4 units; each colour appears exactly 4 times.
- `SawtoothTests`: for every block of ten in levels 1–200, the hard level's
  difficulty (pos 4) > the mean of positions 0–3, the super hard level's (pos 9)
  > the mean of positions 5–8, and position 5 has fewer colours than position 4.
  (Verified against the web engine: all 20 blocks pass.)
- `GeometryTests`: `Hgeo = 3.807301`; total interior area `AreaBelow(Poly, 1)`
  = 3.697482 (the 16-segment bottom is slightly smaller than a true semicircle,
  exactly as on the web); `CapAt(0)` equals it; the table never increases;
  `CapAt(90°) = 0`; `AngleFor(CapAt(x)) ≈ x`; 4 units upright fill to
  `y = −0.497482` and 1 unit to `y = −2.897482` (± 1e-5).
- `LevelStateTests`: pour moves the top run; hidden runs reveal as a group;
  undo restores ids but keeps reveals; restart re-hides; add-vial survives undo
  and restart; merged hidden bands never expose a seam.
- `AudioSynthTests`: each recipe renders the expected length (± 5 ms), no NaN,
  peak ≤ 1 after normalisation, identical bytes on two runs.
- `SaveTests`: round trip; corrupt file → defaults; erase keeps settings.

**PlayMode**
- Pour flow: tap source + target → animation completes within
  `tA + tB + tC + 50` ms and the board matches the engine.
- Win flow: start from a fresh save with `level` set to 4, play the solver's
  path through `BoardInput`; the Win sheet appears and the save shows level 5
  and 135 coins (120 + 10 + 5 for no boosters). Continue into level 5: the hard
  intro plays; winning it gives 170 coins.
- Resume: play 3 moves of a level, reload the scene, "Continue level N", same
  board.

---

## 21. Milestones and acceptance checks

| # | Milestone | Done when |
| --- | --- | --- |
| M1 | Project setup, asmdefs, full engine port, probe CLI | All EngineParity, Curve, Solvability and Sawtooth tests pass; CLI output equals Appendix B.2 |
| M2 | Texture and audio generators | Appendix A PNGs and §13.5 WAVs regenerate byte-identically; AudioSynth tests pass; audition every sound in the editor |
| M3 | Static board: layout, vial meshes, liquid shader, symbols, cork | Levels 1, 13, 20 and 60 render in light and dark themes; hidden layers show hatched primer with '?' |
| M4 | Input, pour animation, stream, particles, glug sounds, haptics | Paint stays level while tipping; stream lands on the rising surface; pitch rises as the target fills; concurrent pours work |
| M5 | Level flow: corking, painting reveal, win sequence, save and resume | Win flow and Resume PlayMode tests pass; paintings match the web for levels 1, 5 and 20 |
| M6 | Boosters, buy sheet, dead-end watcher, hint, tutorial, hard intro, hidden-paint tip | Stuck bar appears on a proven dead end within ~0.5 s; hints never spent on dead boards |
| M7 | Lobby, level road, hub, settings, theme switching, erase progress | Road matches §15.4; Auto theme follows the OS |
| M8 | Performance and device pass | 60 fps on a mid-range Android with 15 vials; generation never blocks the main thread; probe run for levels 1–120 recorded |

---

## 22. Appendix A: generated asset manifest

All PNGs are RGBA, straight alpha, written to
`Assets/_Project/Textures/Generated/`.

| File | Size | Import | Contents |
| --- | --- | --- | --- |
| `tex_cork.png` | 256×192 | Sprite, pivot top-centre, PPU so it is 1 unit wide | Rounded rect (radius 38) filling the image; horizontal gradient #DDAE78 → #C68D57 (45%) → #94623A; highlight band x 19..237, y 16..48 from the top, radius 16, rgba(255,236,200,.45); five pores radius 8, rgba(90,50,20,.35), centres (px from left, px from top) = (64,96), (166,70), (198,134), (112,144), (51,160) |
| `tex_frame_light.png` / `tex_frame_dark.png` | 64×64 | Sprite, 9-slice border 16, Clamp | Rounded rect radius 10; linear gradient at 145° from ps-frame to ps-frame-2 (§16.1); 2 px highlight along the top edge rgba(255,255,255,.25); horizontal grain: 40 seeded 1-px streaks of random length, alpha .05, light and dark alternating |
| `tex_frame_shadow.png` | 128×128 | Sprite, 9-slice border 48 | Black rounded rect 64×64 centred, radius 10, Gaussian blur σ 11 px, alpha .55 |
| `tex_canvas_tooth.png` | 8×8 | Default, Repeat, Point | Transparent; pixels on rows 0 and 4 and columns 2 and 6 = rgba(90,80,60,.07) |
| `tex_symbols.png` | 1664×128 (13 cells) | Sprite (multiple, 13 slices), Clamp | White glyphs on transparent. A cell spans ±0.65 s with s = 98 px. 0 circle r .46s · 1 triangle (0,.55)(.55,−.42)(−.55,−.42) · 2 square .8s · 3 diamond (0,±.6)(±.48,0) · 4 star 5 pts ro .6 ri .26 first point up · 5 plus: rects .32×1.1 and 1.1×.32 · 6 star 4 pts ro .62 ri .18 · 7 star 6 pts ro .55 ri .48 · 8 ring ro .5 ri .26 · 9 bar 1.1×.32 · 10 two dots r .22 at x ±.3 · 11 half disc r .5, upper half · 12 question mark: stroke width .13 with round caps through (−.22,.20) (−.18,.31) (−.09,.38) (.03,.40) (.15,.36) (.23,.26) (.22,.14) (.14,.05) (.04,−.02) (0,−.10) (0,−.17), dot r .085 at (0,−.33) (y-up, units of s) |
| `fx_droplet.png` | 64×64 | Sprite | White disc r 30 |
| `fx_spark.png` | 64×64 | Sprite | White 4-point star: 8 vertices alternating radius 30 and 9.6, first on +x |
| `fx_splat.png` | 128×128 | Sprite | White union of: ellipse rx 40 ry 28.8 at (60,66); disc r 11.2 at (98,78); disc r 8 at (32,42) |
| `fx_glow.png` | 128×128 | Sprite | White, alpha `exp(−(d/28.8)²)` from the centre |
| `ui_stripes.png` | 100×100 | Default, Repeat | Black where `(x + y) mod 100 < 50`, else transparent (tint alpha at runtime) |
| `ui_round_24.png` | 64×64 | Sprite, 9-slice border 26 | White rounded rect radius 24 |
| `ui_circle.png` | 128×128 | Sprite | White disc r 63 |
| `ui_soft_shadow.png` | 128×128 | Sprite, 9-slice border 52 | Black rounded rect 48×48 radius 20, blur σ 14, alpha .45 |

Runtime-generated (not files): vial meshes (§8.2), paint stream ribbons (§10),
hint pointer meshes (§11), painting meshes and RenderTextures (§12), level road
geometry (§15.4), card art RenderTexture (§15.1), backdrop gradient (§16.1).

Audio files: §13.5.

---

## 23. Appendix B: golden fixtures

Produced by the web engine. The C# port must reproduce them exactly.

### B.1 Values

```
SeedFor(1,7)  = 3950780609
SeedFor(20,3) = 755098534
SeedFor(0,0)  = 1802543397
Mulberry32(SeedFor(1,7)) first 4: 0.154533308232, 0.378489000723, 0.221675909357, 0.806769933086
Mulberry32(12345) first 3:        0.979728267761, 0.306752264500, 0.484205421526

Spec(n)   K  tier  heat    mystery  pick  cands  reward
   1      3   0    0.0000  0.0000   0     4      10
   5      6   1    2.5000  0.0000   1     9      30
  10      7   2    3.6000  0.0000   1     14     60
  15      7   1    3.6500  0.4600   1     9      30
  47      9   0    5.6500  0.0000   0.45  4      10
  50     11   2    8.2000  0.7000   1     14     60
  55     11   1    8.2500  0.6200   1     9      30
  60     12   2    9.3500  0.7000   1     14     60
  61     10   0    6.9000  0.0000   0     4      10
  63     10   0    7.8000  0.5400   0.55  4      10
 100     12   2   13.9500  0.7000   1     14     60

Generate(1):  vials   [[0,1,2,2],[0,1,2,1],[1,0,2,0],[],[]]
              palette [10,2,4]   hidden all 0   len 9   pool 4   fail 0
              solve(budget 400000) first moves [[0,3,2],[1,0,1],[1,3,1],[0,1,2]]
              art kinds ["wave","sun"]   slots [1,2,0]   shape[1] bbox [0,167.1956,400,57.1835]

Generate(2):  vials   [[2,0,1,0],[1,0,2,0],[2,1,2,1],[],[]]
              palette [5,11,10]   len 10
              first moves [[0,3,1],[1,3,1],[2,0,1],[1,2,1]]
              art kinds ["hill","sun2"]   slots [0,1,2]   shape[1] bbox [0,198.7899,400,101.2101]

Generate(5):  vials   [[3,2,1,2],[4,5,3,1],[0,3,4,1],[0,0,4,5],[4,3,1,2],[2,5,5,0],[],[]]
              palette [9,0,4,1,10,11]   len 20   pool 9   casual 0.5   skilled 0.2   fail 0.35
              first moves [[0,6,1],[1,0,1],[4,6,1],[2,4,1]]
              art kinds ["wave","block","arch","sun","dots"]   slots [1,5,4,3,0,2]   shape[1] bbox [0,163.5554,400,66.9693]

Generate(10): vials   [[0,3,6,0],[1,0,3,1],[4,3,2,6],[2,2,5,6],[4,5,6,1],[4,5,1,0],[2,3,4,5],[],[]]
              palette [8,3,9,10,5,6,0]   len 25   pool 14   casual 0.75   skilled 0.6   fail 0.675
              first moves [[0,7,1],[2,0,1],[5,7,1],[4,5,1]]
              art kinds ["stripe","hill","wave","ring","blob","leaf"]   slots [0,2,3,6,5,4,1]

Generate(13): vials   [[4,0,1,2],[4,2,3,4],[1,3,3,2],[3,0,1,0],[0,1,2,4],[],[]]
              palette [10,8,5,11,3]   len 16
              hidden  [[0,0,0,0],[0,0,0,0],[1,0,0,0],[0,0,0,0],[0,0,1,0],[],[]]
              first moves [[0,5,1],[2,5,1],[0,6,1],[3,0,1]]
              art kinds ["peak","hill","sun","blob"]   slots [0,4,2,1,3]   shape[1] bbox [175.3173,164.7517,200.7875,135.2483]

Generate(20): vials   [[3,5,5,0],[1,4,6,1],[3,1,5,7],[7,4,2,7],[2,4,1,4],[3,6,6,7],[3,6,5,0],[2,0,2,0],[],[]]
              palette [6,2,8,3,7,11,5,10]   len 28   casual 0.95   skilled 1   fail 0.975
              hidden  [[0,1,0,0],[1,1,1,0],[1,1,0,0],[1,1,1,0],[1,1,0,0],[0,1,1,0],[1,1,0,0],[0,0,1,0],[],[]]
              first moves [[0,8,1],[6,8,1],[6,0,1],[7,8,1]]
              art kinds ["arch","peak","block","stripe","blob","dots","ring"]   slots [1,7,2,5,0,6,3,4]
              shape[1] bbox [85.7874,187.4683,130.4856,112.5317]

Generate(37): vials   [[7,6,4,2],[6,4,3,3],[5,4,7,1],[5,6,7,6],[0,5,4,5],[3,7,2,1],[0,2,1,0],[1,3,0,2],[],[]]
              palette [6,11,10,3,5,4,1,2]   len 25   casual 0.6428571428571429   skilled 0.2857142857142857
              first moves [[0,8,1],[7,8,1],[6,7,1],[5,6,1]]

Generate(60): vials   [[10,2,8,2],[7,8,1,4],[4,6,11,8],[7,11,10,3],[0,10,5,9],[5,9,2,11],[7,1,7,6],[6,9,8,9],[0,11,1,0],[10,2,5,3],[4,6,5,3],[1,3,4,0],[],[]]
              palette [10,3,2,9,4,0,7,1,11,5,8,6]   len 46   fail 1
              hidden  [[1,0,1,0],[1,1,0,0],[1,0,1,0],[1,0,1,0],[0,1,1,0],[0,0,1,0],[0,1,1,0],[1,1,0,0],[1,0,1,0],[0,0,1,0],[1,0,0,0],[1,0,0,0],[],[]]
              first moves [[0,12,1],[2,0,1],[5,2,1],[5,12,1]]
              art kinds ["hill","stripe","wave","arch","peak","ring","blob","sun","leaf","dots","sun2"]
              slots [8,10,0,6,3,9,7,2,1,5,4,11]
```

"art kinds" lists the shapes after the ground, in build order; "slots" includes
the ground first; bboxes are `[x, y, w, h]` rounded to 4 decimals.

### B.2 Difficulty curve, levels 1–30

`casual` and `skilled` are the two simulated players' failure rates;
difficulty is their mean; moves is the solver's path length.

```
 lvl  tier  colours hidden moves  casual skilled  difficulty
   1             3       0      9     0.00    0.00    0.00
   2             3       0     10     0.00    0.00    0.00
   3             4       0     12     0.00    0.00    0.00
   4             4       0     13     0.00    0.00    0.00
   5   HARD      6       0     20     0.50    0.20    0.35
   6             4       0     13     0.00    0.00    0.00
   7             4       0     13     0.00    0.00    0.00
   8             5       0     16     0.36    0.14    0.25
   9             5       0     15     0.07    0.14    0.11
  10   SUPER     7       0     25     0.75    0.60    0.68
  11             4       0     12     0.00    0.00    0.00
  12             5       0     17     0.21    0.00    0.11
  13             5       2     16     0.07    0.07    0.07
  14             6       0     21     0.43    0.00    0.21
  15   HARD      7      10     25     0.90    0.80    0.85
  16             5       0     16     0.00    0.00    0.00
  17             5       0     16     0.07    0.00    0.04
  18             6       5     20     0.57    0.00    0.29
  19             6       0     18     0.29    0.29    0.29
  20   SUPER     8      16     28     0.95    1.00    0.97
  21             5       0     16     0.00    0.00    0.00
  22             6       0     20     0.36    0.14    0.25
  23             6       4     22     0.43    0.43    0.43
  24             7       0     25     0.57    0.29    0.43
  25   HARD      8      16     25     0.90    0.55    0.72
  26             6       0     17     0.07    0.21    0.14
  27             6       0     22     0.14    0.21    0.18
  28             7       9     23     0.71    0.43    0.57
  29             7       0     24     0.43    0.64    0.54
  30   SUPER     9      16     35     1.00    0.95    0.97

mean difficulty   normal 0.16 · hard 0.64 · super 0.87
```
