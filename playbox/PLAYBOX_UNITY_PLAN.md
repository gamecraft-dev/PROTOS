# Playbox in Unity: the build plan for the app and all three games

This plan is for an AI coding agent building **Playbox** in Unity: one app whose
home screen shows every game as a board, with three games inside it.

| Game | What it is | Part |
| --- | --- | --- |
| **Paint Sort** | Pour paint between glass vials until each holds one colour. Levels are generated on the device with a sawtooth difficulty curve, and a painting fills in as colours are sorted. | II |
| **Hex Tile Sort** | Drop stacks of hex tiles onto a 19-cell board; matching colours flip across, ten of a colour clear. Endless, with a best score. Built in 3D. | III |
| **Car Loop** | Tap to merge your cars into a busy roundabout before the clock runs out. 300 baked levels, boosters, a garage, ads and a shop. | IV |

Part I is the app every game sits in: project setup, code hierarchy, shared
services (save, settings, audio, haptics, ads, purchases, analytics), the home
screen of boards, theme and tooling. Part V covers tests, milestones and the
manifest of every generated asset.

The plan covers the rules of each game, the architecture, the code, and every
asset the agent **generates through code**: meshes, shaders, textures,
paintings, car sprites, icons, particles, sounds, music, prefabs, scenes and UI
layouts. The only gameplay assets the agent cannot make are the fonts, listed per
game in **`PLAYBOX_ASSETS.md`**. Store art, accounts and ad/store ids come from
whoever publishes the app; nothing in this plan waits on them except where §1
says so.

The reference implementations are the web prototypes in this repo, and the
agent gets their source alongside this plan (§0). Where the plan gives code,
port it exactly; where it gives numbers, use them as written.

---

## 0. Using this plan with the HTML sources

### 0.1 Files the agent receives

| File | What it is |
| --- | --- |
| `playbox/src/shell.html` | The hub: save store, the Web Audio synth (`tone`, `noise`, `bell`, compressor), sheets, toasts, settings, the home screen of game boards. |
| `playbox/src/games/paint-sort.html` | The whole of Paint Sort: CSS, engine, painting, vial drawing, sounds, game logic, lobby. **The main reference for Part II.** |
| `playbox/src/games/hex-tile-sort.html`, `playbox/src/games/car-loop.html` | The boards for the other two games (artwork, colours, text, status chip) and how the web embeds their pages. |
| `hexa-stack/index.html` | The whole of Hex Tile Sort ("Hexa Stack"). **The main reference for Part III.** |
| `roundabout/src/app.html` | The whole of Car Loop ("Roundabout Rush"): track geometry, level generator and bots, simulation, rendering, boosters, economy, ads, shop, garage. **The main reference for Part IV.** |
| `roundabout/DESIGN.md` | Why Car Loop works the way it does, with measured balance. Background reading; where it disagrees with this plan, this plan wins. |
| `playbox/tools/probe.mjs` | Runs the Paint Sort engine in Node and prints the difficulty table. Use it to produce extra golden fixtures. |
| `playbox/index.html`, `roundabout/index.html` | Built outputs. Open them in a browser to see and hear the target; don't read them for code (they duplicate the sources). |

### 0.2 Which one wins

1. **This plan wins** for everything it specifies: architecture, Unity
   settings, coordinate conversions, units, the C# code, shaders, generated
   asset specs, file names, save format and tests. The web versions draw
   everything live on a 2D canvas; the plan deliberately replaces that with
   meshes, shaders, pre-rendered audio clips, baked textures and, for Hex Tile
   Sort, real 3D.
2. **The HTML wins** for behaviour or look that the plan doesn't pin down (an
   animation detail, a colour in an edge case, a string). Port what the HTML
   does, converted to the plan's conventions.
3. **For engine output, the HTML is ground truth.** The golden fixtures
   (Appendices B, C and D) were produced by it. If the C# port and the plan's
   listing ever disagree with the HTML's output, match the HTML and report the
   difference.

### 0.3 Where each part lives in the HTML

Find code by name; line numbers will drift.

**Shell and home screen** (`playbox/src/shell.html`)

| Plan section | HTML source |
| --- | --- |
| §4.1 Save | `store` |
| §4.3 Audio | the `audio` object (`tone`, `noise`, `bell`, compressor settings) |
| §4.8 Sheets, toasts | `sheet`, `closeSheet`, `toast` |
| §4.2 Settings | `openSettings` |
| §5 Home screen and boards | `renderHome`, `boardFor`, the `.board*` rules in its `<style>`; board art: `drawCard` in `paint-sort.html`, `draw` in `hex-tile-sort.html` and in `car-loop.html` |
| §6.1 Theme tokens | CSS custom properties at the top of the file |

**Paint Sort** (`playbox/src/games/paint-sort.html`)

| Plan section | HTML source |
| --- | --- |
| §10 Engine | Between the `// @engine-start` and `// @engine-end` markers: `rng32`, `seedFor`, `shuffle`, `RAMP`, `PICK`, `K_CAP`, `spec`, `isFull`, `isSolved`, `runLen`, `listMoves`, `applyMove`, `heur`, `keyOf`, `solve`, `playout`, `rateMove`, `playoutSkilled`, `deal`, `generate`, `probe` |
| §10.9 Painting composition | `makeShape`, `buildArt` |
| §11 Level state and rules | inside `mount`: `freshLevel`, `hydrate`, `persist`, `canPour`, `revealTops`, `bandsOf`, `refreshDone`, `pour`, `finishPour`, `celebrate`, `onSolved`, `winSequence` |
| §11.4 Input | `tapVial`, `hitVial`, `onKey`, the `pointerdown` listener |
| §11.5–11.7 Boosters, dead ends, tutorial | `undo`, `hint`, `addVial`, `restart`, `buy`, `checkStuckSoon`, `checkStuck`, `showStuck`, `coach` |
| §12 Layout | `layout` |
| §13 Vial geometry and drawing | `areaBelow`, `levelFor`, `makeGeom`, `capAt`, `angleFor`, `worldPoly`, `axisAt`, `interiorPath`, `outlinePath`, `drawVial`, `drawCork`, `vialOpts` |
| §13.9 Motion | `step` (lift, shake, wobble, glide), `restPose`, `busy` |
| §14 Pour | `pour`, `pourPose`, `srcUnits`, `poured`, `trimTop`, `addTop`, `surfaceY` |
| §15–16 Stream, particles, hint pointer | `draw` (stream, particles and pointer sections), `step` (splash spawning), `sparkle` |
| §17 Paintings | `tooth`, `brushIn`, `drawArt`, `paintCanvas` |
| §18 Sound | `makeSfx` (every game sound) |
| §19 UI | `TEMPLATE` (markup), the `<style>` block (sizes, colours, animations), `renderLobby`, `renderRoad`, `showWin`, `intro`, `menu`, `howTo`, `updateHud`; icons: the `ICONS` object |
| §20 Pigments | `PIGMENTS`, `mix`, `glyph` |
| §21.1 Save section | `persist`, `hydrate` |

**Hex Tile Sort** (`hexa-stack/index.html`)

| Plan section | HTML source |
| --- | --- |
| §22 Rules, §24 Engine | config block (`CLEAR_AT` … `COLOURS`), `buildBoard`, `neighbours`, `topColour`, `topRunLen`, `takeTopRun`, `boardTopColours`, `pickColour`, `stackHeight`, `genStack`, `checkTier`, `scoreMerge`, `bestMerge`, `newGame` (seeding) |
| §25 Resolver | `place`, `pump`, `pumpResolver`, `maybeRefill`, `refillTray`, `maybeGameOver`, `gameOver` |
| §23 Camera and layout | `layout`, `applyRotation`, `rotateBoard` |
| §26 Tile and socket look | `makeTileSprite`, `makeSocketSprite`, `drawContactShadow`, `drawBadge` |
| §27 Animations and effects | `flipIn`, `flyerPose`, `drawFlipTile`, `popRun`, `drawPopTile`, `squash`, `stepFX`, `draw` (glow, ring, primed, particles, floats, banner sections), `drawTray` |
| §28 Input | `cellUnder`, `slotUnder`, `previewGlow`, the pointer listeners, `endPointer`, the `keydown` listener |
| §29 UI | the markup in `<body>` and the `<style>` block; `syncHUD`, `tickScore`, `hideHint` |
| §30 Sound | the `Sound` object |

**Car Loop** (`roundabout/src/app.html`)

| Plan section | HTML source |
| --- | --- |
| §33–34 Track geometry | `roundedPoly`, `resample`, `poseAt`, `circDist`, `SHAPES`, `loopPoints`, `makeFeeder`, `candPose`, `computeDanger`, `getTrack` |
| §35 Levels | `HAND`, `trafficPositions`, `rawDef`, `loopLength`, `REF`, `CAUTIOUS`, `levelDef`, `planTap`, `refSolve`, `greedySolve` |
| §36 Simulation | `worldSpeed`, `mkCar`, `createScene`, `addQueueCar`, `phaseOf`, `safeAt`, `lightState`, `updatePose`, `release`, `stepWorld`, `checkCollisions` |
| §37 Game flow | `startLevel`, `trafficColorsFor`, `tutorial`, `coach`, `showIntro`, `tap`, `onReleased`, `onMerged`, `onSettled`, `checkWin`, `onWin`, `onCrash`, `onTimeUp`, `doRevive`, `update`, `demoTick`, `startDemo`, `gamePause` |
| §38 Boosters | `BOOSTERS`, `useBooster`, `consume`, `enterTow`, `exitTow`, `towAt`, `hudTick` (booster rings) |
| §39 Economy | `ECON`, `RARITY`, `CARS`, `DAILY`, `openComplete`, `afterLevel`, `nextGiftCar`, `openCarReward`, `openDaily`, `dailyState`, `renderGarage`, `renderShop`, `addCoins`, `spend`, `flyCoins` |
| §40 Ads and store | `ADS`, `IAP`, the `Ads` object (`rewarded`, `interstitial`, `maybe`, `banner`), `openIAP`, `grantIAP`, `track` |
| §41 Rendering | `layout`, `scenePaths`, `buildStatic`, `render`, `drawZone`, `drawSignal`, `drawArmed`, `drawTow`, `drawTowTargets`, the effects section (`part`, `fxPuff`, `fxRing`, `fxCrash`, `fxConfetti`, `makeWreck`, `updateFx`) |
| §42 Car art | `drawCarShape`, `sprite`, `SHADOW`, `BEAM`, `skinFor`, `playerColor`, `drawThumb`, `drawTurntable`, `signSVG` |
| §43 UI | the `<style>` block, the `<svg>` symbol sheet (icons), the markup, every `open…` panel function, `renderLevels`, `renderBoosters`, `renderCarsLeft`, `toast`, `Modal` |
| §44 Sound and music | the `AU` object (`fx`, music `PROG`/`ARP`/`sched`), `buzz` calls |
| §45 Save section | `SAVE_KEY`, `defaults`, `save` |

### 0.4 Converting while you read

- **Canvas y points down; Unity y points up.**
  - *Paint Sort:* every board formula in Part II is already converted. When
    reading one straight from the HTML, flip the sign of every y offset and of
    every rotation angle.
  - *Car Loop:* the pure simulation keeps the web's y-down coordinates and
    angles exactly (so ported code and fixtures match number for number); only
    the presentation layer converts, with `unity = (x, −y)` and z-rotation
    `−a` (§33).
  - *Hex Tile Sort:* the board is 3D; web screen y maps to world −z (§23).
- **Canvas pixels = Unity world units (dp)** for Paint Sort's board and for
  every screen-space effect. Velocities in the HTML are px/ms or px/s as noted:
  multiply px/ms by 1000 for units per second, and px/ms² by 1,000,000.
- **Sound:** the web synthesises every sound live. Unity pre-renders clips with
  one offline synth (§4.3); each game's recipes (§18, §30, §44) are its web
  sound code translated.
- **Don't port the web-only parts:** Google Fonts links, `localStorage`,
  `history.replaceState` and the `#hash` deep links, `window.claude.hot`,
  `window.storage`, `ResizeObserver`, DOM building, the debug hooks
  (`window.__ps`, `window.__rr`; the Unity equivalents are the tests and the
  probe CLIs), `framedGame`/`exitButton` and the build's `@embed-base64` step
  (the web runs Hex Tile Sort and Car Loop by embedding their finished pages; in
  Unity they are ordinary scenes), Car Loop's splash screen (Playbox has one
  boot screen), and Car Loop's mock ad creatives and mock store sheet outside
  development builds (§4.5, §4.6).

### 0.5 Running the web engines in Node (golden fixtures)

All three engines run in Node with `node:vm`, which is how the appendices were
produced. Use the same approach to dump any value you want to test against.

*Paint Sort* (`probe.mjs` does this): read `paint-sort.html`, take the text
between the engine markers, evaluate it.

```js
// node dump-ps.mjs 42
import { readFileSync } from 'node:fs'; import vm from 'node:vm';
const src = readFileSync('playbox/src/games/paint-sort.html', 'utf8');
const eng = src.match(/\/\/ @engine-start[^\n]*\n([\s\S]*?)\/\/ @engine-end/)[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(eng + '\nthis.e = { generate, solve, spec };', ctx);
const g = ctx.e.generate(+process.argv[2]);
console.log(JSON.stringify({ vials: g.vials, palette: g.palette, hidden: g.hidden, len: g.len, fail: g.fail }));
```

`node playbox/tools/probe.mjs 1 60` prints the difficulty table; the C# probe
CLI (§21.3) must print the same numbers.

*Car Loop:* everything from `// ---------- utils ----------` up to
`// ---------- car art` is DOM-free (the save loader is wrapped in `try`, the
audio only starts on a call). This script also **bakes the level set** the
Unity build ships (§35.5):

```js
// node carloop-levels.mjs 1 300 > Assets/_Project/Config/CarLoop/CarLoopLevels.json   (about 30 s, 87 KB)
import { readFileSync } from 'node:fs'; import vm from 'node:vm';
const src = readFileSync('roundabout/src/app.html', 'utf8');
const a = src.indexOf('// ---------- utils ----------'), b = src.indexOf('// ---------- car art');
const ctx = { Math, Date, performance }; vm.createContext(ctx);
vm.runInContext(src.slice(a, b) + '\nthis.e = { levelDef, getTrack, rawDef };', ctx);
const [from, to] = process.argv.slice(2).map(Number), out = [];
for (let n = from; n <= to; n++) {
  const d = ctx.e.levelDef(n);
  out.push({ n, shape: d.shape, dir: d.dir, pattern: d.pattern, hard: d.hard ? 1 : 0, dual: d.dual ? 1 : 0,
    tutorial: d.tutorial || null, teach: d.teach ? 1 : 0, pulse: d.pulse || null, speed: d.speed,
    traffic: d.traffic, player: d.player, feeders: d.feeders, seed: d.seed, time: d.time });
}
console.log(JSON.stringify({ version: 1, levels: out }, null, 1));
```

*Hex Tile Sort:* the config, utils, hex maths, state and board sections (from
`/* ----- config` up to `/* ----- layout`) plus `scoreMerge` and `bestMerge`
run in a context with `window = { matchMedia: () => ({ matches: false }) }`.
Build a board by filling `G.cells[i].stack`, set `G.lastPlaced`, and call
`bestMerge()`; Appendix D was made this way.

---

## Contents

0. Using this plan with the HTML sources

**Part I: the Playbox app**
1. Ground rules for the agent
2. Project setup
3. Code hierarchy, scenes and navigation
4. Core services (save, settings, audio, haptics, ads, purchases, analytics, shared UI)
5. Home screen: game boards
6. Theme tokens and app strings
7. Editor tooling (generators, builders, RasterCanvas, icons)

**Part II: Paint Sort**
8. Rules
9. Units, prefabs and scene
10. Engine (pure C#, full source)
11. Level state and game rules
12. Board layout
13. Vials: geometry, meshes, liquid shader
14. The pour animation
15. The paint stream
16. Particles
17. Paintings
18. Sound and haptics
19. UI layouts
20. Pigments and strings
21. Save section, threading and the balance probe

**Part III: Hex Tile Sort**
22. Rules
23. World, camera and layout
24. Engine (pure C#)
25. The resolver and its timings
26. Meshes and shaders
27. Animations and effects
28. Input
29. UI
30. Sound and haptics
31. Save section and board status

**Part IV: Car Loop**
32. Rules
33. Units, coordinates and scene
34. Track geometry
35. Levels: hand-made, generated, validated, baked
36. Simulation
37. Game flow
38. Boosters
39. Economy, garage, daily reward
40. Ads, store and analytics
41. Rendering
42. Generated car art
43. UI screens and panels
44. Sound, music and haptics
45. Save section, board status and performance

**Part V: Shipping**
46. Tests
47. Milestones and acceptance checks
48. Appendix A: generated asset manifest
49. Appendix B: Paint Sort golden fixtures
50. Appendix C: Car Loop golden fixtures
51. Appendix D: Hex Tile Sort fixtures

---

# Part I: the Playbox app

## 1. Ground rules for the agent

1. **Everything in this plan is generated by code.** Textures and audio are
   written to disk by editor scripts (`Playbox/Generate/...` menu items);
   meshes, paintings, roads and particle geometry are built at runtime. Every
   game must run with nothing else imported. The only outside inputs are the
   fonts (`PLAYBOX_ASSETS.md`), the ad, store and analytics SDKs with their ids,
   and any optional art added later, and the build works without each of them:
   - **Fonts:** until the TTFs are imported, TextMeshPro uses its default font
     asset through the `FontSet` indirection (§4.8).
   - **Ad, purchase and analytics SDKs:** until they are imported and
     configured, the mock services run (§4.5–4.7).
   - **Optional art** (UI skin, illustrations, car art, music): every slot has a
     generated stand-in, and the user's file replaces it when assigned.
2. **Each engine must match its web prototype.** Paint Sort level *n* must
   produce the same board, palette and hidden layers as on the web (§10.10,
   Appendix B). Car Loop's level generator and bots must reproduce the web's
   level definitions (Appendix C); the shipped levels 1–300 are baked from the
   web engine itself (§35.5). Hex Tile Sort's merge choice and scoring must
   reproduce Appendix D.
3. **Keep engines pure.** `Playbox.PaintSort.Engine`, `Playbox.HexTileSort.Engine`
   and `Playbox.CarLoop.Engine` have no `UnityEngine` references, so they run in
   EditMode tests, on worker threads and from command-line probes.
4. **Build in milestone order (§47).** Don't start a milestone until the
   previous one's acceptance checks pass.
5. Times are **milliseconds** unless marked `s`. Distances marked `w` are
   multiples of the current vial width (Paint Sort), `s` multiples of the hex
   size on screen (Hex Tile Sort), and plain numbers in Car Loop are track
   units.
6. **One project, one app.** All three games ship in one binary, share one save
   file, one settings model, one audio mixer and one set of store products.
   A game never reads or writes another game's save section.

---

## 2. Project setup

| Setting | Value |
| --- | --- |
| Unity | 6 LTS (6000.0.x), created from the **Universal 3D** template |
| Render pipeline | URP with the **Universal Renderer** (Forward). Not the 2D Renderer: no game uses 2D lights, and Hex Tile Sort needs the 3D renderer |
| Colour space | **Linear** (see "Colour rules" below) |
| HDR | Off in the URP asset (every game is unlit) |
| Anti-aliasing | URP asset MSAA 4x |
| Orientation | Portrait only |
| Target frame rate | `Application.targetFrameRate = 60` |
| Platforms | Android (min API 24, IL2CPP, ARM64), iOS 13+ |
| Packages | `com.unity.render-pipelines.universal`, `com.unity.inputsystem`, `com.unity.ugui` (includes TextMeshPro), `com.unity.nuget.newtonsoft-json`, `com.unity.test-framework`, `com.unity.purchasing` (Unity IAP, §4.6) |
| Layers | `Board` (8), `Painting` (9), `CardArt` (10), `HexBoard` (11), `CarLoop` (12), `Fx2D` (13), `HexHeld` (14) |
| Sorting layers | `Background`, `Board`, `Fx` |

Canvas Scaler on every UI canvas: *Scale With Screen Size*, reference
**390 × 844**, match **0.5**. One canvas unit is then one "dp", the same as one
CSS pixel in the web prototypes, so every UI size in this document can be used
directly.

**One project, many games.** Each game is its own scene with its own camera and
its own assemblies, sharing the Core services (§4):

| Game | Camera | World |
| --- | --- | --- |
| Paint Sort | orthographic, 1 world unit = 1 dp | y-up 2D board of meshes (§9) |
| Hex Tile Sort | perspective, 30° FOV, pitched 60° down | 3D: hex prisms on a ground plane (§23) |
| Car Loop | orthographic, fitted to the track | track units, web coordinates flipped at the view (§33) |

Sprites, sorting layers, sorting groups and uGUI all work with the Universal
Renderer. Screen-space effects that the web draws in canvas pixels (Hex Tile
Sort's particles, floats and banner; Car Loop's vignettes) render through an
overlay camera on layer `Fx2D` whose orthographic size makes 1 unit = 1 dp.

**Colour rules (Linear colour space).** Every colour in this document is an
sRGB hex value, as on the web. In Linear space:

- `Material.SetColor` / `MaterialPropertyBlock.SetColor` and uGUI `Graphic.color`
  convert sRGB to linear automatically. Use them wherever possible.
- `SetVector`, `SetVectorArray`, vertex colours and colours computed by hand are
  **not** converted: pass `color.linear`, except to the shaders listed next.
- `Liquid.shader`, `Gradient.shader`, `HexTile.shader`, `HexSocket.shader` and
  `RadialFill.shader` take **sRGB** values and do their blending maths in sRGB
  (gloss, seams, meniscus, hatch, gradient stops, lighten/darken), then convert
  with `SRGBToLinear` on output, so colours match the browser exactly.
- Colour textures (cork, frame, board art, car sprites, icons with colour)
  import with sRGB on; masks and white-only shapes (symbols, particles, tooth,
  stripes, single-colour icons) can stay sRGB on too, since only their alpha
  matters.
- Hardware alpha blending happens in linear space, so see-through layers
  (glass, edge, highlights, scrims, glows) look slightly stronger than on the
  web. Compare against web screenshots at each game's first visual milestone
  and adjust those alpha values in the game's palette asset until they match;
  record the final values there rather than in shader code.
- RenderTextures that are shown in UI (painting, board art, garage turntable)
  use an sRGB format (`RenderTextureReadWrite.sRGB`).

---

## 3. Code hierarchy, scenes and navigation

```
Assets/_Project/
├─ Scripts/
│  ├─ Common/                                 asmdef Playbox.Common (noEngineReferences: true)
│  │  ├─ Mulberry32.cs                        the shared RNG (§10.2), used by every engine and by the editor synth
│  │  └─ JsMath.cs                            JsRound (JavaScript Math.round), JsMod, Clamp, Lerp, Imul helpers
│  ├─ Core/                                   asmdef Playbox.Core (refs Common)
│  │  ├─ Boot/Bootstrap.cs                    creates Services, loads save, initialises ads/IAP/analytics, opens Hub
│  │  ├─ Boot/Services.cs                     DontDestroyOnLoad holder; static access to the services below
│  │  ├─ Boot/Navigator.cs                    OpenGame(id), BackToHub(); scene loading + transition fade (§3.2)
│  │  ├─ Games/GameDefinition.cs              ScriptableObject: id, title, tagline, order, soon, sceneName, board colours, board art, status provider (§5)
│  │  ├─ Games/GameRegistry.cs                ScriptableObject: the three GameDefinitions
│  │  ├─ Games/IGameStatus.cs                 Status(save) for the board chip, Cta(save) for the big board's button
│  │  ├─ Games/GameScene.cs                   base MonoBehaviour for each game's root: OnEnter, OnPause(bool), OnExit, RequestExit()
│  │  ├─ Save/SaveService.cs                  load/save playbox.json, debounced, atomic, migration (§4.1)
│  │  ├─ Save/SaveData.cs                     root DTO (settings, purchases, last game, per-game JObject)
│  │  ├─ Settings/SettingsService.cs          sound, music, haptics, theme; raises Changed (§4.2)
│  │  ├─ Settings/SettingsSheet.cs            the app settings sheet (§4.2)
│  │  ├─ Theme/ThemeService.cs                resolves Auto/Light/Dark; raises ThemeChanged
│  │  ├─ Theme/ThemePalette.cs                ScriptableObject of colour tokens (light + dark)
│  │  ├─ Theme/DarkModeProbe.cs               Android JNI + iOS bridge for "is system dark"
│  │  ├─ Audio/SfxPlayer.cs                   24-voice pool, PlayScheduled, volume/pitch, per-game groups (§4.3)
│  │  ├─ Audio/MusicPlayer.cs                 one looping source with fade and ducking (§4.3)
│  │  ├─ Audio/SfxLibrary.cs                  ScriptableObject mapping SfxId -> AudioClip[] (one per game + one shared)
│  │  ├─ Audio/SfxId.cs                       enum of every generated clip family, prefixed by game
│  │  ├─ Haptics/IHaptics.cs                  Pulse(ms), Pattern(long[])
│  │  ├─ Haptics/AndroidHaptics.cs            VibrationEffect via JNI
│  │  ├─ Haptics/IosHaptics.cs                UIImpactFeedbackGenerator via the native bridge
│  │  ├─ Haptics/NullHaptics.cs               editor / unsupported
│  │  ├─ Ads/IAdService.cs                    rewarded, interstitial, banner (§4.5)
│  │  ├─ Ads/MockAdService.cs                 port of Car Loop's mock ads (editor and development builds)
│  │  ├─ Ads/MediationAdService.cs            thin adapter over the chosen mediation SDK (compiled with PLAYBOX_ADS)
│  │  ├─ Ads/AdPolicy.cs                      frequency caps, gates, pause/duck bookkeeping
│  │  ├─ Store/IPurchaseService.cs            buy, restore, prices (§4.6)
│  │  ├─ Store/UnityPurchaseService.cs        Unity IAP implementation
│  │  ├─ Store/MockPurchaseService.cs         confirm sheet, nothing charged (editor and development builds)
│  │  ├─ Store/ProductCatalog.cs              ScriptableObject: product ids, types, store ids, fallback prices
│  │  ├─ Store/Entitlements.cs                applies purchases to SaveData (noads app-wide; game grants via callbacks)
│  │  ├─ Analytics/IAnalytics.cs              Track(name, params) (§4.7)
│  │  ├─ Analytics/LogAnalytics.cs            ring buffer of the last 300 events (debug overlay)
│  │  ├─ Analytics/FirebaseAnalytics.cs       compiled with PLAYBOX_FIREBASE
│  │  ├─ UI/SheetHost.cs                      one bottom sheet at a time + scrim (§4.8)
│  │  ├─ UI/SheetBuilder.cs                   builds sheet content from a spec (eyebrow, title, sub, body, actions)
│  │  ├─ UI/Toast.cs
│  │  ├─ UI/UiSwitch.cs, UI/SegmentedControl.cs, UI/PressFeedback.cs, UI/SafeAreaFitter.cs
│  │  ├─ UI/ThemedGraphic.cs                  binds a Graphic colour to a theme token
│  │  ├─ UI/UiGradient.cs                     vertical gradient on any Image via vertex colours (§4.8)
│  │  ├─ UI/UiSkin.cs                         ScriptableObject of sprite slots; unassigned slots use the generated primitives
│  │  ├─ UI/IconSet.cs                        ScriptableObject: icon id -> Sprite (generated by IconGenerator, §7.3)
│  │  ├─ UI/FontSet.cs                        ScriptableObject: font role -> TMP_FontAsset, with fallback to the TMP default
│  │  ├─ Hub/HubScreen.cs                     home screen: greeting, featured board, board grid (§5)
│  │  ├─ Hub/BoardView.cs                     one board: art, title, tagline, chip, play button; featured/small/wide; soon state; press, entrance and shake
│  │  ├─ Hub/BoardArt.cs                      shows a board's art (RenderTexture or texture) with envelope fit
│  │  ├─ Util/Easing.cs                       all easing functions in §14.2 plus Hex Tile Sort's easeOutBack(1.9) and smooth
│  │  ├─ Util/MainThread.cs                   queue for results from worker threads
│  │  ├─ Util/RibbonBuilder.cs                polyline -> triangle ribbon mesh (joins, caps, dashes, offsets)
│  │  ├─ Util/Triangulator.cs                 ear clipping for simple polygons
│  │  ├─ Util/ScreenFx.cs                     the Fx2D overlay camera: dp <-> screen <-> world helpers
│  │  └─ Util/Hex.cs                          "#RRGGBB"/rgba() -> Color; Shade(hex, k) in both web variants (§6.1)
│  ├─ PaintSort/                              Part II (Engine, Runtime and UI assemblies; full tree in §9.3)
│  ├─ HexTileSort/
│  │  ├─ Engine/                              asmdef Playbox.HexTileSort.Engine (noEngineReferences; refs Common)
│  │  │  ├─ HexConfig.cs                      constants and the colour table (§24.1)
│  │  │  ├─ HexBoard.cs                       cells, axial map, neighbours, top-run helpers (§24.2)
│  │  │  ├─ MergeChooser.cs                   ScoreMerge, BestMerge (§24.3)
│  │  │  ├─ StackFactory.cs                   StackHeight, PickColour, GenStack, SeedBoard (§24.4)
│  │  │  └─ Tiers.cs                          tier and colour count from clears (§24.5)
│  │  ├─ Runtime/                             asmdef Playbox.HexTileSort (refs Core, Common, Engine)
│  │  │  ├─ HexController.cs                  run lifecycle, HUD wiring, game over, best score (§25)
│  │  │  ├─ HexResolver.cs                    the resolver coroutine and Pump (§25)
│  │  │  ├─ HexTray.cs                        three slots, refill slide (§27.8)
│  │  │  ├─ HexLayout.cs                      dp layout, camera fit, tray placement (§23)
│  │  │  ├─ HexMeshes.cs                      prism, socket, outline meshes (§26)
│  │  │  ├─ CellView.cs, StackView.cs, TileView.cs   pooled tiles, squash, drop, badges
│  │  │  ├─ FlipAnimator.cs                   hinge flips (§27.3)
│  │  │  ├─ PopAnimator.cs                    clears (§27.4)
│  │  │  ├─ HexFx.cs                          particles, score floats, banner, shake on the Fx2D overlay (§27.5–27.7)
│  │  │  ├─ HexInput.cs                       drag, tap-tap, rotation (§28)
│  │  │  ├─ HexSfx.cs, HexHaptics.cs          (§30)
│  │  │  └─ HexStatus.cs                      IGameStatus for the board (§31)
│  │  └─ UI/                                  asmdef Playbox.HexTileSort.UI
│  │     ├─ HexHud.cs                         header, tier ribbon, bottom bar (§29)
│  │     └─ GameOverVeil.cs
│  ├─ CarLoop/
│  │  ├─ Engine/                              asmdef Playbox.CarLoop.Engine (noEngineReferences; refs Common)
│  │  │  ├─ Geom.cs                           GEOM constants (§34.1)
│  │  │  ├─ PathTable.cs                      Resample, PoseAt (§34.2)
│  │  │  ├─ Shapes.cs                         SHAPES, LoopPoints, RoundedPoly (§34.3)
│  │  │  ├─ Feeder.cs                         MakeFeeder, CandPose, ComputeDanger (§34.4)
│  │  │  ├─ Track.cs, TrackCache.cs           GetTrack (§34.5)
│  │  │  ├─ LevelDef.cs                       the level record (§35.1)
│  │  │  ├─ HandLevels.cs                     levels 1–10 (§35.2)
│  │  │  ├─ LevelGenerator.cs                 TrafficPositions, RawDef, LoopLength, LevelDef (§35.3)
│  │  │  ├─ Bots.cs                           PlanTap, RefSolve, GreedySolve (§35.4)
│  │  │  ├─ Scene.cs, Car.cs                  createScene, cars, queues (§36)
│  │  │  └─ Sim.cs                            WorldSpeed, SafeAt, LightState, Release, StepWorld, CheckCollisions (§36)
│  │  ├─ Runtime/                             asmdef Playbox.CarLoop (refs Core, Common, Engine)
│  │  │  ├─ CarLoopController.cs              screens, game state machine, update loop (§37)
│  │  │  ├─ LevelSource.cs                    baked JSON for 1–300, generator past it, background build (§35.5)
│  │  │  ├─ Boosters.cs                       (§38)
│  │  │  ├─ Economy.cs, Garage.cs, Daily.cs   (§39)
│  │  │  ├─ CarLoopAds.cs                     placements and the interstitial gate on top of IAdService (§40)
│  │  │  ├─ CarLoopView.cs                    camera fit, static layer, per-frame car and effect rendering (§41)
│  │  │  ├─ StaticLayerBuilder.cs             roads, island, decor, markings as meshes (§41.2)
│  │  │  ├─ CarRenderer.cs                    pooled car sprites, shadows, beams, wrecks, tow (§41.3)
│  │  │  ├─ CarLoopFx.cs                      particles, decals, float texts, shake (§41.4)
│  │  │  ├─ DemoDriver.cs                     the attract-mode roundabout on the Car Loop home (§37.9)
│  │  │  ├─ CarLoopSfx.cs, CarLoopHaptics.cs  (§44)
│  │  │  └─ CarLoopStatus.cs                  IGameStatus for the board (§45)
│  │  └─ UI/                                  asmdef Playbox.CarLoop.UI
│  │     ├─ Screens/HomeScreen.cs, LevelsScreen.cs, GarageScreen.cs, ShopScreen.cs
│  │     ├─ Hud/GameHud.cs, BoosterBar.cs, CarsLeft.cs, ClockBar.cs, CoachBubble.cs, LevelIntro.cs, TowBar.cs
│  │     ├─ Panels/ModalHost.cs               card modals with scrim, stack, pause bookkeeping (§43.3)
│  │     ├─ Panels/PausePanel.cs, SettingsPanel.cs, CompletePanel.cs, FailPanel.cs, BoosterIntroPanel.cs,
│  │     │  BoosterBuyPanel.cs, NoCoinsPanel.cs, CarRewardPanel.cs, StarterPanel.cs, RatePanel.cs, DailyPanel.cs
│  │     ├─ Widgets/CoinPill.cs, CoinFlyer.cs, RaisedButton.cs, StarRow.cs, MultiplierBar.cs, ReviveRing.cs, Turntable.cs
│  │     └─ BannerSlot.cs                     reserves the 58 dp banner area (§40.1)
│  ├─ Editor/                                 asmdef Playbox.Editor (Editor only; refs everything above)
│  │  ├─ Audio/Synth.cs                       offline Web-Audio-style synth (§4.3)
│  │  ├─ Audio/Biquad.cs, Audio/Compressor.cs, Audio/WavWriter.cs
│  │  ├─ Audio/PaintSortRecipes.cs            (§18.1)
│  │  ├─ Audio/HexRecipes.cs                  (§30.1)
│  │  ├─ Audio/CarLoopRecipes.cs              sounds and the music loop (§44.1, §44.2)
│  │  ├─ Audio/GenerateAudio.cs               menu: Playbox/Generate/Audio
│  │  ├─ Audio/AudioImportRules.cs            AssetPostprocessor for generated WAVs
│  │  ├─ Textures/Raster.cs                   SDF rasteriser: circles, rounded rects, polygons, capsules (§7.1)
│  │  ├─ Textures/RasterCanvas.cs             CPU subset of Canvas2D: paths, fills, strokes, gradients, transforms, shadow blur (§7.3)
│  │  ├─ Textures/SvgIcon.cs                  minimal SVG reader on top of RasterCanvas (§7.3)
│  │  ├─ Textures/TextureRecipes.cs           every Paint Sort and app texture, as code (Appendix A)
│  │  ├─ Textures/HexTextureRecipes.cs        backdrop, socket, blob, board art (§26, Appendix A)
│  │  ├─ Textures/CarSpriteBaker.cs           port of drawCarShape and the car textures (§42)
│  │  ├─ Textures/CarLoopTextureRecipes.cs    trees, glows, particles, sign, turntable, board art (§41, Appendix A)
│  │  ├─ Textures/IconGenerator.cs            rasterises every icon in §7.3 into IconSet.asset
│  │  ├─ Textures/GenerateTextures.cs         menu: Playbox/Generate/Textures
│  │  ├─ Build/PrefabBuilder.cs               menu: Playbox/Build/Prefabs
│  │  ├─ Build/SceneBuilder.cs                menu: Playbox/Build/Scenes
│  │  ├─ Levels/CarLoopBake.cs                menu: Playbox/Car Loop/Bake Levels; imports and checks the baked JSON (§35.5)
│  │  ├─ Probe/ProbeWindow.cs                 menu: Playbox/Paint Sort/Balance Probe
│  │  ├─ Probe/ProbeCli.cs                    -executeMethod entry point (Paint Sort)
│  │  └─ Probe/CarLoopProbeCli.cs             -executeMethod entry point (Car Loop level table)
│  └─ Plugins/iOS/PlayboxNative.mm            dark-mode query + impact haptics (§4.4)
├─ Shaders/
│  ├─ UnlitColor.shader                       flat colour, alpha blend, _Tint via MPB, Cull Off
│  ├─ Liquid.shader                           §13.4
│  ├─ SoftStroke.shader                       ribbon with soft edges (selection glow, hex outlines, glow rings)
│  ├─ Stream.shader                           §15
│  ├─ BrushReveal.shader                      §17.4 (writes stencil)
│  ├─ StencilColor.shader                     streaks clipped to their shape (§17.5)
│  ├─ Gradient.shader                         vertical two-colour background
│  ├─ TintedSprite.shader                     sprites with alpha multiplier (particles, symbols)
│  ├─ AdditiveSprite.shader                   additive sprites (beams, sparks, fire, glows)
│  ├─ HexTile.shader                          §26.2
│  ├─ HexSocket.shader                        §26.3
│  ├─ RadialFill.shader                       radial gradient fill of a mesh (island glow, scorch, lamp pools)
│  ├─ DashedStroke.shader                     ribbon with animated dashes (danger zone, tow reticle)
│  └─ ScreenBackdrop.shader                   Car Loop's dot grid and vignette; Slow-Mo vignette (§41.1)
├─ Materials/                                 one material per shader; all per-object values go through MaterialPropertyBlock
├─ Textures/Generated/                        written by GenerateTextures (Appendix A)
├─ Audio/Generated/                           written by GenerateAudio (§18.2, §30.2, §44.3)
├─ Fonts/                                     the user's TTFs and their TMP font assets (PLAYBOX_ASSETS.md)
├─ Prefabs/                                   written by PrefabBuilder (§9.2, §26.5, §41.5)
├─ Scenes/Boot.unity, Hub.unity, PaintSort.unity, HexTileSort.unity, CarLoop.unity   written by SceneBuilder (§3.1)
├─ Config/
│  ├─ GameRegistry.asset
│  ├─ Games/PaintSort.asset, Games/HexTileSort.asset, Games/CarLoop.asset   GameDefinitions (§5)
│  ├─ ThemePalette.asset                      values from §6.1
│  ├─ Pigments.asset                          values from §20.1
│  ├─ SfxLibrary.asset                        filled by GenerateAudio
│  ├─ ProductCatalog.asset                    §4.6
│  ├─ AdConfig.asset                          ad unit ids per platform, test mode flag (§4.5)
│  ├─ IconSet.asset, FontSet.asset, UiSkin.asset
│  ├─ HexConfig.asset                         tunables mirrored from §24.1 (read-only at runtime unless Remote Config is added)
│  └─ CarLoop/CarLoopLevels.json, CarLoop/EconomyConfig.asset, CarLoop/AdsConfig.asset, CarLoop/Boosters.asset, CarLoop/Cars.asset
└─ Tests/
   ├─ EditMode/                               asmdef Playbox.Tests.EditMode
   └─ PlayMode/                               asmdef Playbox.Tests.PlayMode
```

### 3.1 Scenes (built by `SceneBuilder`)

| Scene | Contents |
| --- | --- |
| `Boot` | `Bootstrap` object. Creates `Services` (DontDestroyOnLoad: SaveService, SettingsService, ThemeService, SfxPlayer, MusicPlayer, Haptics, AdService, PurchaseService, Analytics, Navigator, MainThread), loads the save, starts the ad SDK and the store (neither blocks: the Hub opens at once), loads `Hub`. Shows the app splash (logo on `bg`) for at most 1.2 s. |
| `Hub` | UI canvas with `HubScreen` (boards for all games in `GameRegistry`), `CardArtRig` (Paint Sort's live board art). |
| `PaintSort` | `BoardRig`, `PaintingRig`, UI canvas with `LobbyScreen` and `PlayScreen` panels, `SheetHost`, `Toast`, and `PaintSortController` wiring it all (§9). |
| `HexTileSort` | `HexRig` (perspective camera, backdrop, board root, tray root), `Fx2D` overlay camera, UI canvas with `HexHud` and `GameOverVeil`, `HexController` (§23). |
| `CarLoop` | `CarLoopRig` (orthographic camera, static layer root, car pool, effects), `Fx2D` overlay camera, UI canvas with the four screens, HUD, `ModalHost`, `BannerSlot`, toasts, and `CarLoopController` (§33). |

### 3.2 Navigation and the game lifecycle

- A board calls `Navigator.OpenGame(id)`: click sound, a 180 ms fade to `bg`,
  `SceneManager.LoadSceneAsync(def.SceneName, Single)`, fade in. `SaveData.last`
  is set to the id when the scene finishes loading, so the Hub can say "Welcome
  back" and feature that game's board.
- Each game scene has one root deriving from `GameScene`. `RequestExit()`
  flushes the save, stops the game's music and banner, and calls
  `Navigator.BackToHub()`.
- **Back buttons.** Paint Sort: the lobby's Back. Hex Tile Sort: a back button
  first in its header (38×38, radius 12, the header's icon-button style). Car
  Loop: a back button first in its home screen's top-left row (44×44, radius 14,
  the `rbtn` style); inside a level, Pause → Home returns to Car Loop's home, not
  the Hub. The Android back key does the same as the visible back button on each
  screen, closes the top sheet or modal first, and on the Hub asks nothing and
  moves the app to the background.
- **Pause.** `OnApplicationPause(true)` calls the active `GameScene.OnPause(true)`
  (Car Loop opens its pause panel in a level; Paint Sort and Hex Tile Sort freeze
  timers) and flushes the save.
- A "Coming soon" board (`Soon = true`) never loads anything. All three games are
  playable in this plan, so `Soon` stays in the code for future games only.

---

## 4. Core services

### 4.1 Save (`SaveService`)

One JSON file, `Application.persistentDataPath/playbox.json`, serialised with
Newtonsoft. Writes are debounced by 150 ms and atomic (write `playbox.json.tmp`,
then replace). Flush immediately on a level win, on a purchase, on
`OnApplicationPause(true)`, on `OnApplicationQuit` and when a game exits. A
corrupt or missing file loads defaults.

```json
{
  "v": 2,
  "settings": { "sound": true, "music": true, "haptics": true, "theme": "system" },
  "purchases": { "noads": false, "carloop_starter": false },
  "last": "paint-sort",
  "games": {
    "paint-sort":    { "...": "§21.1" },
    "hex-tile-sort": { "...": "§31" },
    "car-loop":      { "...": "§45.1" }
  }
}
```

- Each game owns `games[id]` as a `JObject` and reads it through its own typed
  DTO (`PaintSortSave`, `HexSave`, `CarLoopSave`). Unknown fields are kept when
  the game writes it back, so an older build never drops a newer field.
- `settings` and `purchases` belong to Core. A game reads them through
  `SettingsService` and `Services.Purchases.Has("noads")`, never from its own
  section.
- **Migration** from `v: 1` (the Paint Sort–only format): add `settings.music =
  true` and an empty `purchases`, set `v: 2`.
- **"Erase all saved progress"** (app settings) clears `games` and `last`, and
  keeps `settings` and `purchases` (a purchase is not progress).
- A game's own reset (Car Loop's developer "Reset save") clears only that game's
  section.

### 4.2 Settings and theme

`SettingsService` holds `Sound`, `Music`, `Haptics` (bools) and `Theme`
(`system` / `light` / `dark`), persists them in `settings`, and raises
`Changed(key)`. `SfxPlayer` mutes when Sound is off; `MusicPlayer` when Music is
off; `IHaptics` is a no-op when Haptics is off. Every game's own toggles (Car
Loop's pause and settings tiles, Hex Tile Sort's header sound button) read and
write these same three values, so a change anywhere shows everywhere.

**Theme.** `ThemeService` resolves Auto/Light/Dark (Auto: Android reads
`Configuration.uiMode & UI_MODE_NIGHT_MASK` via JNI, iOS calls
`_PlayboxIsDarkMode()`; re-check on application focus) and raises
`ThemeChanged`. The Hub and Paint Sort follow it. Hex Tile Sort (plum and gold)
and Car Loop (night traffic) have one fixed dark look each, as on the web; their
boards on the Hub still follow the theme for the board's chrome (§5).

**App settings sheet** (`SettingsSheet`, opened from the Hub's gear and from
Paint Sort's top bar). Eyebrow "Settings", title "Options"; rows:

| Row | Control | Sub-label |
| --- | --- | --- |
| Sound | switch | "Every sound is made by the app" |
| Music | switch | "Car Loop's soundtrack" |
| Vibration | switch | "On phones that support it" |
| Theme | segmented Auto / Light / Dark | "Auto follows your device" |
| Colour symbols | switch (stored in Paint Sort's save as `symbols`) | "Adds a shape to every colour of paint" |
| Restore purchases | ghost button | "Bring Remove Ads back on a new device" |
| Privacy policy | ghost button (opens `AppLinks.PrivacyUrl`) | "How Playbox uses data and ads" |
| Erase all saved progress | text button in `bad` | confirm sheet "Erase progress" / "Start every game from scratch?" / "Levels, coins, boosters and best scores in every Playbox game go back to zero. Settings and purchases stay." with "Erase everything" / "Keep my progress" |

Action: "Done". A version line under it (12, dim): "Playbox {Application.version}".

### 4.3 Audio: offline synth, clip libraries, playback, music

Every sound and the one music loop are generated by `Playbox/Generate/Audio`
into `Assets/_Project/Audio/Generated/` as 44.1 kHz mono 16-bit WAV, by one
offline synth that reproduces the web prototypes' Web Audio code. Each game's
recipes are in its own part (§18.1, §30.1, §44.1–44.2).

#### Primitives (semantics to reproduce exactly)

**Tone** `{f, f1?, glide?, dur=.12, gain=.25, attack=.004, at=0, type=sine, filter?, ff=1200, q=.8, linAttack=false}`
- Frequency: `f` at `at`; if `f1`, exponential glide to `f1` over `glide`
  (default `dur`), then holds `f1`.
- Gain envelope (default): `0.0001` at `at` → exponential to `gain` at
  `at + attack` → exponential to `0.0001` at `at + dur`; silent after. Voice ends
  at `dur + .05`.
- `linAttack` (Hex Tile Sort's envelope): `0` at `at` → **linear** to `gain` at
  `at + attack` → exponential to `0.0001` at `at + dur`.
- Oscillators: sine; triangle; square and sawtooth with PolyBLEP anti-aliasing.
- Optional biquad (lowpass/bandpass/highpass) at `ff` with `q`. (Web Audio's
  own default Q is 1: Car Loop's tone filters, which never set Q, use `q = 1`.)

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

**Master** (per game, because the three web games wire their audio
differently):

| Group | Web wiring | `Render(...)` |
| --- | --- | --- |
| Paint Sort (`sfx_*`) | mix × 0.7 → compressor | `masterGain .7, compress: true` |
| Hex Tile Sort (`hex_*`) | straight to the output | `masterGain 1, compress: false` |
| Car Loop (`cl_*`, sounds and music) | sfx bus .6 and music bus .11 → master .9 | sounds `masterGain .54`, music `masterGain .099`, `compress: false` |

Compressor: threshold −16 dB, knee 14 dB, ratio 5, attack 2 ms, release 160 ms,
peak detector, soft knee. Every clip is trimmed to the last voice's end + 50 ms
with a 5 ms fade-out (the music loop is not trimmed; §44.2).

**Normalisation.** After rendering, scale **each group** by one factor so the
loudest clip in that group peaks at −1 dBFS. This keeps every game's relative
loudness (including Car Loop's music against its sounds) and lets the three
games sit at similar levels; fine-tune between games with `SfxPlayer` group
volumes, not by editing recipes.

**Determinism**: each clip's noise and jitter use `Mulberry32(fnv1a(clipName))`,
so regenerating produces identical files.

#### `Synth.cs` (core)

```csharp
using System;
using Playbox.Common;

public enum Wave { Sine, Triangle, Square, Saw }
public enum Filt { None, Lowpass, Bandpass, Highpass }

public sealed class Synth
{
    public const int SR = 44100;
    readonly float[] _mix;
    int _end;
    readonly Mulberry32 _rng;
    public Synth(string clipName, double maxSeconds = 4) { _rng = new Mulberry32(Fnv1a(clipName)); _mix = new float[(int)(SR * maxSeconds)]; }
    public double Rand() => _rng.Next();

    static double Env(double t, double peak, double attack, double dur, bool linAttack)
    {
        if (t < attack) return linAttack ? peak * t / attack : 1e-4 * Math.Pow(peak / 1e-4, t / attack);
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
                     double at = 0, Wave type = Wave.Sine, Filt filter = Filt.None, double ff = 1200, double q = .8,
                     bool linAttack = false)
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
            Add(start + n, s * Env(t, gain, attack, dur, linAttack));
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
            Add(start + n, s * Env(t, gain, attack, dur, false));
        }
    }

    public void Bell(double f, double at, double gain = .18)
    {
        Tone(f, dur: 1.1, gain: gain, attack: .003, at: at);
        Tone(f * 2.76, dur: .45, gain: gain * .35, attack: .002, at: at);
        Tone(f * 5.4, dur: .2, gain: gain * .12, attack: .002, at: at);
    }

    /// Master gain, optional compressor, trim, fade. Group normalisation happens afterwards.
    public float[] Render(double masterGain, bool compress)
    {
        int len = Math.Min(_mix.Length, _end + (int)(.05 * SR));
        var o = new float[len];
        for (int i = 0; i < len; i++) o[i] = (float)(_mix[i] * masterGain);
        if (compress) Compressor.Apply(o, SR, thresholdDb: -16, kneeDb: 14, ratio: 5, attack: .002, release: .16);
        int fade = (int)(.005 * SR);
        for (int i = 0; i < fade && i < len; i++) o[len - 1 - i] *= (float)i / fade;
        return o;
    }

    /// For seamless loops: everything past `loopSeconds` is added back onto the start, no trim, no fade.
    public float[] RenderLoop(double loopSeconds, double masterGain)
    {
        int n = (int)(loopSeconds * SR);
        var o = new float[n];
        for (int i = 0; i < _end; i++) o[i % n] += (float)(_mix[i] * masterGain);
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

#### Import settings (`AudioImportRules`)

For `Audio/Generated/*.wav`: Force To Mono, Load In Background off, Load Type
Decompress On Load, Compression PCM, Preload Audio Data on. Exception: the music
loop (`cl_music_loop.wav`) uses Compressed In Memory, Vorbis quality 70, and
Load In Background on.

#### Playback (`SfxPlayer`, `MusicPlayer`)

`SfxPlayer`: 24 pooled 2D `AudioSource`s routed to the mixer's `SFX` group;
`Play(id, variant, volume, pitch, delaySeconds)`. Delayed sounds use
`PlayScheduled(AudioSettings.dspTime + delay)`. Group volumes (Paint Sort,
Hex Tile Sort, Car Loop) start at 1.0 and are tuned by ear at each game's audio
milestone. Muted when Sound is off. When all voices are busy, steal the oldest.

`MusicPlayer`: one looping `AudioSource` on the mixer's `Music` group.
`Play(clip, fadeIn 0.6 s)`, `Stop(fadeOut 0.4 s)`. Muted when Music is off
(volume ramps over 200 ms, like the web's `setTargetAtTime(…, .2)`).

**Ducking.** While a full-screen ad is showing (`IAdService.Busy`), the mixer's
SFX group goes to −80 dB over 50 ms and Music over 200 ms, and both come back
the same way after.

### 4.4 Haptics

`IHaptics.Pulse(ms)` / `Pattern(long[] onOff)`; no-op when Vibration is off.

- **Android** (`AndroidHaptics`): `Vibrator` from the activity;
  API 26+: `VibrationEffect.createOneShot(ms, DEFAULT_AMPLITUDE)` /
  `createWaveform(timings, -1)`; older: `vibrate(ms)` / `vibrate(pattern, -1)`.
- **iOS** (`Plugins/iOS/PlayboxNative.mm`, generated): `_PlayboxImpact(int style)`
  using `UIImpactFeedbackGenerator` (0 light, 1 medium, 2 heavy) and
  `_PlayboxIsDarkMode()` returning `UITraitCollection.currentTraitCollection.userInterfaceStyle == UIUserInterfaceStyleDark`.
  Map a pulse to light (< 10 ms), medium (< 20 ms) or heavy; a pattern fires one
  impact per "on" segment on a timer.

Each game's patterns are in its part (§18.4, §30.3, §44.4).

### 4.5 Ads (`IAdService`)

Only Car Loop shows ads (§40); the service lives in Core so one Remove Ads
purchase covers the whole app and a future game can add placements.

```csharp
public interface IAdService
{
    bool RewardedReady { get; }
    /// done(true) only when the reward is earned; done(false) on no fill, error, or closed early.
    void ShowRewarded(string placement, Action<bool> done);
    /// done() always runs: after the ad closes, or at once if none is available or Remove Ads is owned.
    void ShowInterstitial(string placement, Action done);
    void ShowBanner(string placement);   // bottom, 320×50 (adaptive allowed); no-op if Remove Ads is owned
    void HideBanner();
    /// true while a full-screen ad is up: games pause, audio ducks (§4.3).
    event Action<bool> BusyChanged;
}
```

- **`MediationAdService`** wraps the mediation SDK the user picks (AppLovin MAX,
  Unity LevelPlay or AdMob), compiled only with the
  `PLAYBOX_ADS` scripting define. Ad unit ids per platform and a test-mode flag
  come from `AdConfig.asset`. Initialise after consent (below), preload one
  rewarded and one interstitial, reload after each show, retry loads with
  exponential back-off (2, 4, 8 … 64 s).
- **`MockAdService`** is a port of Car Loop's mock `Ads` object, used in the
  editor, in development builds, and in any build without `PLAYBOX_ADS`:
  - Rewarded: full-screen black layer, top bar with "Rewarded video" label and a
    close button, a creative card (three creatives: "Puzzle Orchard", "Sky
    Courier 3D", "Word Lantern", with the web's gradients, icon letters and CTA
    labels), a 5 px progress bar, "Reward in N s". Length 5 s (2 s with the
    developer toggle *Short ads*). Close before the end → confirm "Close the
    video? You will lose the reward." with "Keep watching" / "Close video".
    At the end: "REWARD EARNED" overlay for 850 ms, then `done(true)`. With the
    developer toggle *No ad fill*: toast "No video is available right now. Try
    again in a moment." and `done(false)`.
  - Interstitial: the same layer labelled "Advertisement"; the close button shows
    a countdown (4 s, 1.5 s with *Short ads*) and then a close icon.
  - Banner: 320×50 card in a 58 dp bar (`#04070E`, top border `edge`), the next
    creative every 20 s, fading 300 ms; a yellow "AD" corner tag.
- **Consent** (only with `PLAYBOX_ADS`): at boot, before initialising the SDK,
  run Google UMP (or the CMP the user chose) and, on iOS 14.5+, the App Tracking
  Transparency prompt with the user's `NSUserTrackingUsageDescription` text. Pass the results to
  the SDK. Settings never blocks on consent.
- **Remove Ads** (`purchases.noads`) disables banners and interstitials in every
  game at once; rewarded ads stay, because the player chooses them.

### 4.6 Purchases (`IPurchaseService`)

```csharp
public interface IPurchaseService
{
    bool Ready { get; }
    string PriceOf(string productId);                           // localised store price, or the catalog fallback
    void Buy(string productId, Action<bool> done);              // grants before done(true)
    void Restore(Action<int> done);                             // number of non-consumables restored
    bool Has(string productId);                                 // owned non-consumables (from SaveData.purchases)
}
```

`ProductCatalog.asset`:

| Product id | Type | Fallback price | Grant |
| --- | --- | --- | --- |
| `noads` | non-consumable | $3.99 | `purchases.noads = true`: no banners or interstitials anywhere in Playbox |
| `carloop_starter` | non-consumable | $1.99 | `purchases.noads = true`, `purchases.carloop_starter = true`; Car Loop: +2,000 coins, +3 of each booster, `starter = true` |
| `carloop_coins1` | consumable | $0.99 | Car Loop +1,000 coins ("Pile of Coins") |
| `carloop_coins2` | consumable | $2.99 | Car Loop +3,000 coins ("Bag of Coins", tag "POPULAR") |
| `carloop_coins3` | consumable | $4.99 | Car Loop +8,000 coins ("Chest of Coins", tag "BEST VALUE") |
| `carloop_coins4` | consumable | $9.99 | Car Loop +20,000 coins ("Vault of Coins") |

Store product ids (the strings in App Store Connect and Play Console) are
fields on each catalog entry, so they can differ per store.

- **Grants are data, applied in Core.** Each entry carries a `ProductGrant`:
  `noAds`, `setPurchaseFlags[]`, and for a game: `gameId`, `coins`,
  `boosters {id: n}`, `setGameFlags[]`. `Entitlements.Apply` adds them to the
  save JSON directly, so a purchase that completes while another scene is open
  (or a pending purchase processed at boot) is never lost. Flush the save, then
  confirm the transaction to the store. If the receiving game is open, it
  refreshes its coin pill and boosters from the `Purchased(productId)` event and
  flies coins from the buy button.
- **Restore** re-applies only `noAds` and the purchase/game flags of owned
  non-consumables (coins and boosters were granted once, at purchase).
- **`MockPurchaseService`** (editor, development builds, or no store
  configured): Car Loop's mock confirm card: ribbon "STORE", title "Confirm
  purchase", a row with the product name and price, the note "Prototype store:
  nothing is charged. A real build opens the App Store or Google Play payment
  sheet here.", button "BUY · {price}" → spinner for 900 ms → grant, buy sound,
  toast "Purchase complete".

### 4.7 Analytics (`IAnalytics`)

`Track(string name, params (string key, object value)[] p)`. Every event gets
`game` (`hub`, `paint-sort`, `hex-tile-sort`, `car-loop`) added by the service.
`LogAnalytics` keeps the last 300 events in memory (shown in a development-build
overlay); `FirebaseAnalytics` (with `PLAYBOX_FIREBASE`) forwards to Firebase.

| Scope | Events |
| --- | --- |
| App | `app_open`, `board_tap` (target game), `settings_change` (key, value), `erase_progress` |
| Ads | `ad_impression` (type), `ad_start` (type, placement), `ad_reward` (placement), `ad_skipped` (placement), `ad_failed` (placement) |
| Store | `iap_view` (product), `iap_purchase` (product, price), `iap_restore` (count) |
| Games | Paint Sort §21.4, Hex Tile Sort §31.2, Car Loop §40.4 |

### 4.8 Shared UI: sheets, toasts, theme binding, fonts, icons

uGUI + TextMeshPro. Sizes are dp (§2). Colours in the Hub and Paint Sort are
theme tokens (§6.1) bound through `ThemedGraphic`, so light/dark switches live.
All Images take their sprite from `UiSkin`; any empty slot uses the generated
primitives (`ui_round_24`, `ui_circle`, `ui_soft_shadow`).

**Shapes.** Every rounded rectangle uses the 9-sliced `ui_round_24` with the
Image's *Pixels Per Unit Multiplier* set to `24 / radius`, so one sprite serves
every corner radius. A border is a second Image, larger by the border width,
behind it in the border colour; a "drop" (the raised 3D edge used by buttons and
boards) is a third Image offset down by the drop height in the darker colour;
vertical gradients use `UiGradient` (vertex colours on the Image's mesh).

**Fonts** (`FontSet.asset`; the TTFs are user-supplied, §1). Each role falls back
to the TMP default font until its asset is assigned.

| Role | Font | Used by |
| --- | --- | --- |
| `AppDisplay` | Lilita One | Hub and Paint Sort display text (titles, buttons, numbers) |
| `AppBody` | Figtree 500–800 | Hub and Paint Sort body text |
| `HexDisplay` | Baloo 2 600–800 | Hex Tile Sort numbers, badges, titles, buttons, floats, banner |
| `HexBody` | Inter 500–700 | Hex Tile Sort labels |
| `CarDisplay` | Bungee | Car Loop titles, big numbers, level numbers, float texts |
| `CarBody` | Fredoka 400–700 | all other Car Loop text |

**Optional art slots** (`UiSkin.asset`). Any art the user adds later goes in a
slot; an empty slot uses the generated stand-in, a
filled one replaces it with no code change. The slot families: app logo and
splash; Paint Sort wall illustrations (`ps_wall_*`: a full-screen sprite with
cover fit replaces the `Gradient` backdrop), UI skin (`ps_*`), frame, cork and
wordmark; Hex Tile Sort backdrop (`hex_backdrop`) and HUD skin (`hex_*`), and the
tile detail texture (`HexTile._Detail`, §26.2); Car Loop car and traffic sprites
(per car in `Cars.asset`, §42), road and ground textures (§41.2), effect
textures (§41.4) and UI kit (`cl_*`). Music and sound replacements go in the
game's music clip and `SfxLibrary.asset`.

**Icons** (`IconSet.asset`): every icon in all three games is generated from the
SVG in the HTML sources (§7.3) as a white 128×128 sprite tinted at runtime, plus
full-colour coin, star and hand sprites. A `UiSkin` icon slot, when assigned,
overrides the generated one.

**Sheets** (`SheetHost`; Hub and Paint Sort): one sheet at a time; the scrim
fades over 260 ms to `--scrim`; the sheet slides up over 360 ms
(cubic-bezier .2, .9, .25, 1). Radius 28 on top, padding 12/20 + bottom safe
area, max height 92%, scrolls. Layout: grab handle (42×5) · eyebrow (11.5,
caps, .14em, accent or tone colour) · title (30 display) · sub (15 muted) · body
· actions (vertical, gap 10; primary 19 display with a 5 dp darker drop; ghost
16). Tapping the scrim closes it unless the sheet is non-dismissable.

**Toast** (Hub and Paint Sort): pill at the top (76 dp + safe area), ink
background, bg-coloured text, 14 bold, visible 1.9 s, fades 200 ms. Hex Tile
Sort has no toasts; Car Loop has its own toast style (§43.3).

---

## 5. Home screen: game boards

Every game appears as a **board**: a chunky card standing on a thick base in
the game's own colour, with artwork, a title, a one-line tagline and a status
chip. The game you last played gets a big board at the top; the rest sit in a
two-column grid below it.

```
HubScreen (safe area, padding 18, vertical scroll, gap 20)
├─ TopRow: logo mark + Wordmark "Playbox" (34, display) · spacer · Settings icon button (42×42, radius 14, surface, `app_settings` icon; opens §4.2)
├─ Greeting: title (clamp 28–36, display) + subtitle (15, muted)
├─ FeatureSection (gap 12; hidden when no game is playable)
│  ├─ Label (12, caps, letter-spacing .14em, dim): "Start here", or "Jump back in" when it's the last game played
│  └─ Board (featured)
├─ MoreSection (gap 12; hidden when empty)
│  ├─ Head: Label "More games" ("Games" when nothing is featured) · spacer · count (12.5, dim): "N coming soon" if any board is soon, else the number of boards
│  └─ BoardGrid: 2 equal columns, column gap 14, row gap 18; if the count is odd the last board spans both columns ("wide")
└─ Note (13.5, dim, centred, max 34ch): "Your progress in each game is saved on this device."
```

**Which board goes where** (`HubScreen.Render`, re-run on enable and on theme change):

```
list     = registry games sorted by Order
ready    = list where !Soon
played   = ready game whose Id == SaveData.last, or null
featured = played ?? first of ready ?? null
grid     = list without featured, in order; if grid.Count is odd, the last one is wide
title    = played ? "Welcome back" : "Pick a game"
subtitle = played ? "{played.Title} is right where you left it." : "Short puzzles that remember where you left off."
```

**Board anatomy** (`Board.prefab`, `BoardView`). Sizes are dp; the featured
values are in brackets.

| Part | Spec |
| --- | --- |
| Base (the slab) | Rounded rect in `b-deep`, same size as the card, offset 6 down, behind it; behind that a soft shadow (`ui_soft_shadow` tinted rgba(10,16,40,.55)) matching CSS `0 20px 32px -22px`: offset 20 down, blur 32, shrunk 22 on every side |
| Card | `surface` fill, radius 24 [28], clips its children to the rounded shape |
| Art | Top of the card, top corners rounded. Small: aspect 1 : 0.86. Wide: 2.1 : 1. Featured: height `clamp(180, 30% of screen height, 230)`. Shows the board art (below) with **envelope** fit, so it always fills |
| Lock badge (soon only) | 32×32 circle, rgba(16,22,40,.72), 10 from the art's top-right corner, white `ui_lock` 16×16 |
| Body | Padding 12/13/14 [16/18/18], vertical gap 5 [6], fills the rest of the card so the foot sits at the bottom and boards in a row line up |
| Title | Display 20 [30], ink, wraps (balanced) |
| Tagline | 12.5 [14.5], muted, line height 1.35, wraps, **never truncated** (keep taglines under ~55 characters) |
| Foot | Row, gap 10, pinned to the bottom of the body (5 above it at least) |
| Chip | Pill, 12 [12.5] heavy, padding 5/10 [6/11], tabular figures; text `b-text` on `b-soft`; soon boards: muted on `surface-2`. **Small boards show only the part before the first " · "** ("Level 4 · 120 coins" → "Level 4") |
| Play button | Not on soon boards. Small: 36×36, radius 12, `b-accent`, `ui_play` 18×18 in `b-ink`, 3 dp `b-deep` drop. Featured: pill at the right, padding 12/18/12/15, radius 15, 4 dp `b-deep` drop, `ui_play` + label (display 18) from `Cta(save)` |

**Motion.**
- Entrance: each board starts 18 dp lower at scale 0.97 and settles over 500 ms
  (cubic-bezier .2,.9,.25,1), staggered 70 ms by position (featured first). No
  fade, so the screen is complete even mid-animation.
- Press: the card moves down 4 dp and the slab offset shrinks to 2 dp (120 ms),
  then springs back.
- Tapping a soon board: shake over 400 ms (x: −6 dp at 20%, +5 at 45%, −3 at
  70%, 0; rotation −1°, +0.8°, 0), haptic 12, toast "{Title} is coming soon".
- Tapping a playable board: click sound, then load its scene.

**The three boards** (`GameDefinition` assets):

| Field | Paint Sort | Hex Tile Sort | Car Loop |
| --- | --- | --- | --- |
| `Id` | `paint-sort` | `hex-tile-sort` | `car-loop` |
| `Order` | 1 | 2 | 3 |
| `Title` | Paint Sort | Hex Tile Sort | Car Loop |
| `Tagline` | Pour paint between vials until each one holds a single colour. | Drop hex stacks so matching colours flip over and clear. | Merge every car into a busy roundabout without a crash. |
| `Soon` | false | false | false |
| `SceneName` | `PaintSort` | `HexTileSort` | `CarLoop` |
| Status | `PaintSortStatus`: `level > 1 ? "Level L · C coins" : "New · 120 coins to start"` | `HexStatus`: `best > 0 ? "Best N" : "New"` (N with en-US thousands separators) | `CarLoopStatus`: `unlocked > 1 ? "Level U · C coins" : "New"` |
| Cta | `level > 1 \|\| cur != null ? "Continue" : "Play"` | `best > 0 ? "Play again" : "Play"` | `unlocked > 1 ? "Continue" : "Play"` |
| Art | `CardArtRig` RenderTexture (below) | `tex_board_hex_tile_sort.png` | `tex_board_car_loop.png` |

Board colours per game are in §6.1. A future game can get its board before it
exists: set `Soon` to true and leave `SceneName` empty, and the board shows its
art with a lock, a "Coming soon" chip, the shake and the toast described above.

**Paint Sort's board art** (`CardArtRig`, rendered into an sRGB RenderTexture
the size of the art area at device scale, again on theme change). Uses Vial
prefabs on the CardArt layer over the wall gradient. `w = min(36, W/11)`;
mouths at `y = 0.55w + Hgeo·w` above the bottom; vials at `x/W` = 0.10
`[Ultramarine, Cadmium Red, Hansa Yellow, Ultramarine]`, 0.24
`[Hansa Yellow, Quinacridone Rose, Cadmium Red]`, 0.62
`[Cadmium Red ×2, Hansa Yellow ×1.35]`, 0.78 `[Ultramarine ×4, corked]`, 0.91
`[Quinacridone Rose ×2, Sap Green]`; a fifth vial tipped 1.18 rad clockwise
with its lip at `(0.62W − 0.1w, mouth + 0.62w)` holding
`[Sap Green, Hansa Yellow ×0.7]`, and a Hansa Yellow stream (width 0.2w) from
that lip into the 0.62 vial's surface with three droplets.

**Hex Tile Sort's and Car Loop's board art** are textures generated by
`HexTextureRecipes` and `CarLoopTextureRecipes` with `RasterCanvas` (§7.3, Appendix A), drawn in the web's y-down art space exactly as
the `draw` functions in `hex-tile-sort.html` and `car-loop.html` do, at
1600 × 1000 px. The background fills the whole image and the subject is
centred, so envelope fit can crop the sides (small boards) or the top and bottom
(wide boards) without losing it. Both use their game's own palette in light and
dark themes.

*Hex Tile Sort* (the scale `u` puts the 270 × 230 design box at 70% of the
image height, centred, shifted by `(−4u, +30u)`):
- Background: vertical gradient #3A1B6E (0) → #1C0E45 (0.55) → #0B0722 (1).
- Hexes are flat-topped, radius `R = 36`, squashed vertically by 0.6; cell centre
  for axial `(q, r)`: `x = 1.5·R·q·1.07`, `y = √3·R·(r + q/2)·1.07·0.6`.
- Cells and stacks (bottom to top), drawn back to front by `y`:
  `(0,−1) [cyan, cyan, lime]`, `(1,−1) [lime ×4]`, `(−1,0) [pink, coral, coral]`,
  `(0,0) [violet ×3, coral]`, `(1,0) [amber, cyan, cyan]`, `(−1,1)` empty,
  `(0,1) [pink, pink, amber ×3]`.
- Tile colours [top, side]: coral #FF5C63/#B8353B, lime #37D07A/#1F8A4E,
  amber #FFB522/#B57A0B, violet #A466FF/#6C3BC0, cyan #26C0F2/#147FA6,
  pink #FF63B4/#B53A7B.
- Slot under each cell: hex radius 0.98R at `y + 3`, fill rgba(9,5,28,.62),
  1.5 px edge rgba(255,255,255,.12). Each tile `i` (thickness 7): side hex at
  `y − 7i`, top hex at `y − 7i − 7`, radius 0.9R, 1 px edge rgba(0,0,0,.18).
  On each stack's top, a ring at radius 0.62R, 2 px, white α .4.
- A coral tile mid-flip above the midpoint between the `(0,0)` and `(−1,0)` tops,
  44 higher than the higher of the two, rotated −0.42 rad, squash 0.26 (side at
  0, top at −5); a dashed trail (3 on, 5 off, 2 px, rgba(255,233,163,.6)) from
  the `(0,0)` top along a quadratic curve to it.

*Car Loop* (the 250 × 236 design box at 70% of the image height, centred,
shifted by `(0, −6u)`; the entry road runs to the bottom edge):
- Background: vertical gradient #16244A → #0B1222.
- Entry road #323E66, x −18…18 from y = 72 down to the image's bottom edge;
  stop line white α .9 at (−16, 84, 32 × 3.5); a white (#F4F4F5) car at (0, 102)
  pointing up.
- Ring: annulus radius 80 / 44 in #323E66; edge lines white α .45, 2 px, at
  radius 76.5 and 47.5; lane line at radius 62, white α .85, 2.5 px, dashes 9/9.
- Island #0D1830 (radius 44); tree circles #1D4A37 at (−6,−4) r15, (9,2) r12,
  (−1,9) r11; highlight circle white α .12 at (−10,−9) r6.
- Street lamps at angles −2.4, −0.75, 0.75, 2.4 rad, radius 94: a radial glow
  (radius 26, rgba(255,226,150,.30) → 0) and a 2.4 dot #FFE7A3. Verge trees
  #1D4A37 at (−108,−62) r9, (112,−30) r11, (−116,40) r10, (104,70) r8.
- Cars on the lane (radius 62), pointing clockwise (rotation = angle + π/2):
  −0.38π #EF4444, −0.92π #3B82F6, 0.12π #F5B82E, 0.78π #8B5CF6. Behind the
  first car, two speed-line arcs at radius 58 and 66 from (its angle − 0.52) to
  (its angle − 0.30), white α .6, 2 px.
- Car shape (local, facing +x): 25 × 13.5 rounded rect r4 in the car colour,
  over a shadow offset (1.5, 2) black α .25; windscreen (3, −4.75, 5 × 9.5) r1.5
  rgba(18,26,44,.78); rear window (−9.5, −4.25, 3 × 8.5) r1, same colour; roof
  shine (−5.5, −4.25, 8 × 8.5) r2, white α .28.

---

## 6. Theme tokens and app strings

### 6.1 Theme tokens (`ThemePalette.asset`)

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

**Home-screen board colours** (per `GameDefinition`, light / dark). `b-accent`
is the play button, `b-deep` the slab under the board and the button's drop,
`b-soft` the chip background, `b-text` the chip text, `b-ink` the play button's
icon and label.

| Game | b-accent | b-deep | b-soft | b-text | b-ink |
| --- | --- | --- | --- | --- | --- |
| Paint Sort | #2B59F0 / #7090FF | #1B3FB8 / #4A63C9 | #E3EAFE / #1F2A52 | #2B59F0 / #7090FF | #FFFFFF / #0B1024 |
| Hex Tile Sort | #FFC94A / #FFC94A | #C57C0A / #A86A0A | #FFF3D1 / #3A2A10 | #8A5200 / #FFD27A | #1A0B3B / #1A0B3B |
| Car Loop | #12935A / #34C771 | #0B6B41 / #1D8A57 | #DDF5E8 / #14301F | #0B6B41 / #6FE3A9 | #FFFFFF / #04210F |

**Lighten and darken.** All three web games use the same rule, implemented once
as `Hex.Shade(color, k)` in Core: per channel, `k ≥ 0` gives
`c + (255 − c)·k` and `k < 0` gives `c·(1 + k)`, rounded with `JsRound` and
clamped to 0–255. (Paint Sort's `mix` toward white or black by `a` is
`Shade(c, a)` and `Shade(c, −a)`.)

### 6.2 App strings

- Home screen (§5): greeting "Welcome back" / "{Title} is right where you left
  it." after a game has been played, otherwise "Pick a game" / "Short puzzles
  that remember where you left off."; section labels "Start here", "Jump back
  in", "More games", "Games"; count "{N} coming soon" or the number of boards;
  note "Your progress in each game is saved on this device."; soon chip "Coming
  soon"; toast "{Title} is coming soon"; button labels "Play", "Continue",
  "Play again".
- Board titles, taglines and statuses: the table in §5.
- Settings (§4.2): the rows and confirm sheet as written there; toasts "Progress
  erased", "Remove Ads restored." / "No purchases to restore on this account.",
  "Purchase complete".
- Every string lives in a `StringTable` asset per scope (`App`, `PaintSort`,
  `HexTileSort`, `CarLoop`) keyed by id, English only for now, so translation
  later is a data change.

---

## 7. Editor tooling

### 7.1 Generators (`Playbox/Generate/...`)

- **All**: runs Textures, Icons, then Audio, then refreshes `SfxLibrary.asset`
  and `IconSet.asset`.
- **Textures**: writes every PNG in Appendix A with import settings (sprite or
  default, wrap, filter bilinear, no mipmaps for UI, 9-slice borders set in the
  sprite meta).
- **Icons**: rasterises every icon in §7.3 and fills `IconSet.asset`.
- **Audio**: renders every recipe (§18.1, §30.1, §44.1–44.2), normalises each
  group (§4.3), writes WAVs.

`Raster.cs`: an anti-aliased signed-distance rasteriser for the simple Paint
Sort and app textures. For each pixel centre, compute the signed distance `d` to
the shape in pixels and set coverage `clamp(0.5 − d, 0, 1)`. Shapes: circle,
ellipse, rounded rect, capsule (segment + radius), convex/concave polygon
(winding test + edge distance), annulus. Composite layers with straight alpha
"over". Gaussian blur (separable) for shadows and glows.

### 7.2 Builders (`Playbox/Build/...`, `Playbox/Car Loop/...`)

- **Prefabs**: creates every prefab in §9.2, §26.5 and §41.5 with materials,
  sorting orders, layers and pool sizes.
- **Scenes**: creates Boot, Hub, PaintSort, HexTileSort and CarLoop (§3.1), with
  canvases, the hierarchies in §5, §19, §29 and §43, references wired, and adds
  them to Build Settings in that order.
- **Car Loop / Bake Levels**: imports `CarLoopLevels.json` (made by the Node
  script in §0.5), checks it (§35.5), and reports any level whose C# generator
  output differs from the baked one.

### 7.3 `RasterCanvas`, SVG icons and the icon set

Several generated textures are ports of web canvas drawing code (car sprites,
board art, Car Loop's trees and sign, Hex Tile Sort's backdrop and socket).
Rather than re-deriving each one as SDF shapes, `RasterCanvas` implements the
subset of the Canvas 2D API those functions use, so each port is a line-by-line
translation of the JavaScript.

```csharp
public sealed class RasterCanvas
{
    public RasterCanvas(int width, int height);
    // state (Save/Restore push and pop all of it)
    public void Save(); public void Restore();
    public void Translate(double x, double y); public void Rotate(double a); public void Scale(double sx, double sy);
    public void Transform(double a, double b, double c, double d, double e, double f); public void SetTransform(...);
    public Paint FillStyle, StrokeStyle;                  // Paint = solid colour, LinearGradient or RadialGradient
    public double LineWidth = 1, GlobalAlpha = 1, LineDashOffset, ShadowBlur, ShadowOffsetX, ShadowOffsetY;
    public LineCap LineCap; public LineJoin LineJoin; public Color32 ShadowColor;
    public Composite GlobalCompositeOperation;            // SourceOver, Lighter, SourceAtop
    public void SetLineDash(params double[] segments);
    // paths
    public void BeginPath(); public void ClosePath(); public void MoveTo(double x, double y); public void LineTo(double x, double y);
    public void Arc(double x, double y, double r, double a0, double a1, bool ccw = false);
    public void ArcTo(double x1, double y1, double x2, double y2, double r);
    public void Ellipse(double x, double y, double rx, double ry, double rot, double a0, double a1, bool ccw = false);
    public void QuadraticCurveTo(...); public void BezierCurveTo(...); public void Rect(...); public void RoundRect(double x, double y, double w, double h, double r);
    public void Fill(FillRule rule = FillRule.NonZero); public void Stroke(); public void Clip();
    public void FillRect(double x, double y, double w, double h); public void ClearRect(...);
    public void DrawImage(RasterCanvas src, double x, double y, double w, double h);
    public static LinearGradient CreateLinearGradient(double x0, double y0, double x1, double y1);  // .AddColorStop(t, colour)
    public static RadialGradient CreateRadialGradient(double x0, double y0, double r0, double x1, double y1, double r1);
    public Texture2D ToTexture(); public void SavePng(string path);
}
```

Implementation rules:
- Flatten curves and arcs to polylines with 0.1 px tolerance in device space.
- Fill: scanline polygon coverage with 4×4 supersampling per pixel, non-zero or
  even-odd winding.
- Stroke: build the stroke outline from the flattened path (joins and caps as
  set; miter limit 10), split by the dash pattern first, then fill it non-zero.
- Colour maths in sRGB, premultiplied internally, like a browser canvas;
  gradients interpolate premultiplied sRGB; output straight-alpha sRGB PNG.
- Shadow: render the shape's alpha into a scratch buffer, Gaussian blur with
  σ = `ShadowBlur / 2`, tint with `ShadowColor`, offset, composite under the
  shape.
- `Lighter` adds premultiplied colours (clamped); `SourceAtop` paints only where
  the destination is opaque (used for burnt car sprites).

**`SvgIcon`** reads the SVG subset the three games' icons use: `<svg viewBox>`,
`<path d>` (M m L l H h V v C c S s Q q A a Z z, arcs converted with the
SVG endpoint-to-centre formulas), `<rect x y width height rx>`, `<circle cx cy r>`,
attributes `fill`, `stroke`, `stroke-width`, `stroke-linecap`, `stroke-linejoin`,
`stroke-dasharray`, `opacity`, and `fill="url(#gCoin)"` (the one gradient in Car
Loop's `<defs>`). `currentColor` is white. The only `<text>` (the "AD" in
`i-noads`) is replaced by these strokes, width 1.3, round caps:
`M9 14.9 L10.5 9.4 L12 14.9 M9.5 13.2 H11.5` and
`M13.1 9.4 V14.9 H14.1 Q16.2 14.9 16.2 12.15 Q16.2 9.4 14.1 9.4 Z`.

**Icons** (`IconGenerator`): 128×128 px, the 24×24 viewBox scaled by 128/24 and
centred, white on transparent unless marked full colour. Copy each SVG string
from the source named.

| Icon ids | Source |
| --- | --- |
| `app_settings` | the sliders icon in `shell.html`'s top row |
| `app_back` | `shell.html` exit button path `M15 5l-7 7 7 7`, stroke 3 |
| `ps_back`, `ps_menu`, `ps_restart`, `ps_undo`, `ps_hint`, `ps_vial`, `ps_play` | the `ICONS` object in `paint-sort.html` |
| `hex_sound_on` | Car Loop `i-sound` |
| `hex_sound_off` | Car Loop `i-sound` with the two wave arcs removed and a stroke `M15 9l6 6M21 9l-6 6`, width 2.2, round caps |
| `hex_restart`, `hex_rotate_right` | Car Loop `i-retry` (clockwise arrow) |
| `hex_rotate_left` | Paint Sort `restart` (anticlockwise arrow) |
| `cl_<symbol>` for each of the 33 `<symbol>`s in `app.html` | `coin`, `star`, `i-pause`, `i-gear`, `i-play`, `i-ad`, `i-lock`, `i-gift`, `i-cart`, `i-garage`, `i-grid`, `i-sound`, `i-music`, `i-vibe`, `i-home`, `i-retry`, `i-close`, `i-check`, `i-back`, `i-plus`, `i-slow`, `i-light`, `i-tow`, `i-auto`, `i-clock`, `i-flame`, `i-noads`, `i-car`, `i-crash`, `i-doc`, `i-hand`, `i-chev`, `i-crown`. **Full colour:** `cl_coin` (keeps its gradient and colours), `cl_i-hand` (white with the dark outline), `cl_i-gift` (the ribbon line is `#0B1222`), `cl_i-car` (window rects `#0B1222` at α .55). |
| `cl_sign` | `signSVG()` output in a 100×100 viewBox, rendered at 256×256, full colour (Car Loop's logo mark) |

Generated icons are the stand-ins; any `UiSkin` icon slot the user fills
replaces its generated icon.

---

# Part II: Paint Sort

## 8. Rules

The player sorts paint: tap a vial to pick it up, tap another to pour.

- **Vials** hold 4 units of paint, stacked bottom to top. A level has K colours
  (4 units of each) in K vials plus 2 empty vials.
- **Pouring** moves the source's top run (all same-colour units on top) onto the
  target, but only if the target is empty or its top colour matches, and only as
  much as fits. A vial that is full of one colour gets **corked** and can no
  longer be picked up.
- **Win** when every vial is either empty or a corked single colour.
- **Hidden paint** (from level 13): grey layers with a "?" whose colour shows
  once the paint above them has been poured off. Consecutive hidden units always
  draw as one band, so a seam never gives the colour away.
- **The painting.** Every level has a small generated painting above the
  vials, drawn in pencil. Each colour corked brushes its part of the picture in;
  an undo that un-corks a colour wipes its paint again.
- **Levels** are generated on the device from the level number (the same level
  everywhere), solver-checked, and chosen by simulated players to follow a
  **sawtooth**: within each block of ten, difficulty climbs, the 5th level is
  **hard** and the 10th **super hard**, and the level after each spike eases
  off. Every block starts harder than the last.
- **Boosters:** Undo (5 per try, then buy 5 more), Hint (points at a pour that
  still wins; never spent on a dead board), Add vial (one extra empty vial, once
  per level). Restart is free.
- **Coins:** start with 120. A level pays 10 (hard 30, super hard 60), plus 5 if
  no undo, hint or extra vial was used. Prices: 5 undos 30, a hint 40, a vial 90.
- **Dead ends:** when no sequence of pours can finish the board, a bar says so
  and offers Undo, Add vial and Restart.
- **Progress** (level, coins, boosters, the board in progress) saves after every
  pour; a killed app resumes on the same board.

Everything below makes those rules exact: the engine (§10), the state model on
paint ids (§11), and the look, motion and sound of the pour (§12–§18).

---

## 9. Units, prefabs and scene

### 9.1 Units and coordinates

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

### 9.2 Prefabs (built by `PrefabBuilder`)

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
CardArtRig.prefab           at world (20000, 0); layer CardArt; camera -> Paint Sort's board-art RenderTexture (§5)
UI prefabs                  Sheet, Toast, Board, TopBar, BoosterButton, PigmentDot, StuckBar, HardIntro, FloatLabel
```

### 9.3 Code

Paint Sort's part of the tree in §3 (the editor scripts it needs are listed
there: `PaintSortRecipes`, `TextureRecipes`, the probe window and CLI).

```
Assets/_Project/Scripts/
├─ PaintSort/
│  ├─ Engine/                              asmdef Playbox.PaintSort.Engine (noEngineReferences: true)
│  │  ├─ Move.cs
│  │  ├─ Seeds.cs                          SeedFor, Shuffle, JsRound (the RNG itself is Common/Mulberry32.cs)
│  │  ├─ Difficulty.cs                     RAMP, PICK, caps, Spec(n)
│  │  ├─ LevelSpec.cs
│  │  ├─ Rules.cs                          IsFull, IsSolved, RunLen, ListMoves, Apply, Heur, KeyOf
│  │  ├─ Solver.cs                         weighted A*
│  │  ├─ Playouts.cs                       casual + skilled simulated players, RateMove
│  │  ├─ Generator.cs                      Deal, Generate
│  │  ├─ GeneratedLevel.cs
│  │  ├─ Probe.cs                          difficulty table rows
│  │  └─ Art/ArtBuilder.cs                 painting composition (pure, doubles only)
│  ├─ Runtime/                             asmdef Playbox.PaintSort (refs Core + Engine)
│  │  ├─ PaintSortController.cs            state machine, owns LevelState, wires views
│  │  ├─ LevelState.cs                     ids model, history, reveal set (§11)
│  │  ├─ LevelCache.cs                     background generation of n and n+1
│  │  ├─ Economy.cs                        constants (§11.8)
│  │  ├─ BoardLayout.cs                    rows, w, slot positions (§12)
│  │  ├─ VialGeometry.cs                   polygon, cap table, AreaBelow, LevelFor, AngleFor (§13.1)
│  │  ├─ VialMeshes.cs                     interior, outline, rim, highlights, shadow meshes (§13.2)
│  │  ├─ VialView.cs                       per-vial motion state + renderer updates (§13.5–13.9)
│  │  ├─ LiquidBands.cs                    bands -> shader arrays (§13.4)
│  │  ├─ SymbolLayer.cs                    '?' and colour-blind glyph sprites (§13.6)
│  │  ├─ PourAnimation.cs                  one pour's timeline and poses (§14)
│  │  ├─ StreamRenderer.cs                 paint stream ribbon (§15)
│  │  ├─ FxPool.cs                         droplets, sparks, splats (§16)
│  │  ├─ HintPointer.cs                    arrow + dashed target outline
│  │  ├─ PaintingRenderer.cs               renders an ArtBuilder result into a RenderTexture (§17)
│  │  ├─ DeadEndWatcher.cs                 debounced solver check (§11.6)
│  │  ├─ HintService.cs                    solver-backed hint (§11.5)
│  │  ├─ Tutorial.cs                       level-1 coach text + pointer (§11.7)
│  │  ├─ BoardInput.cs                     taps, keyboard (§11.4)
│  │  ├─ PaintSortSfx.cs                   game events -> SfxPlayer calls (§18.3)
│  │  ├─ PaintSortHaptics.cs               game events -> haptic patterns (§18.4)
│  │  └─ PaintSortStatus.cs                IGameStatus for Paint Sort's board
│  └─ UI/                                  asmdef Playbox.PaintSort.UI
│     ├─ LobbyScreen.cs                    wordmark, next painting card, level road, play button
│     ├─ LevelRoadGraphic.cs               custom Graphic drawing the sawtooth road (§19.3)
│     ├─ PlayHud.cs                        top bar, level + tier badge, coins
│     ├─ BoosterBar.cs, BoosterButton.cs
│     ├─ PigmentDots.cs
│     ├─ CoachLine.cs
│     ├─ StuckBar.cs
│     ├─ HardIntro.cs
│     ├─ FloatLabel.cs                     pigment name that floats up from a corked vial
│     └─ Sheets/WinSheet.cs, PauseSheet.cs, BuySheet.cs, HowToSheet.cs, RestartSheet.cs, MysteryTipSheet.cs, SettingsSheet.cs
```

Scene contents: §3.1.

---

## 10. Engine (pure C#, full source)

Namespace `Playbox.PaintSort.Engine`. Use `double` everywhere a number is not
an index. Port this code as written; it reproduces the web engine exactly.

### 10.1 `Move.cs`

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

### 10.2 `Common/Mulberry32.cs` and `Engine/Seeds.cs` (RNG and seeding)

The RNG lives in `Playbox.Common` so every engine and the editor synth share
it; every Paint Sort engine file starts with `using Playbox.Common;`.

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.Common
{
    /// Port of the web rng32() / mulberry32(). Bit-exact with the JavaScript version.
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
}

namespace Playbox.PaintSort.Engine
{
    using Playbox.Common;

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

### 10.3 `LevelSpec.cs` and `Difficulty.cs`

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

### 10.4 `Rules.cs`

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

### 10.5 `Solver.cs` (weighted A*)

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

### 10.6 `Playouts.cs` (the simulated players)

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

### 10.7 `Generator.cs`

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
        public int[] Palette;        // Palette[colour] = pigment index 0..11 (§20.1)
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

### 10.8 `Probe.cs`

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

### 10.9 `Art/ArtBuilder.cs` (painting composition)

Pure: returns path commands in art space (400 × 300, y-down). Rendering is §17.

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

### 10.10 JavaScript-to-C# parity rules

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

### 10.11 Engine usage rules

- `Generator.Generate(n)` takes up to ~350 ms at level 120 on a desktop core and
  more on phones. **Always call it on a worker thread** (§21.2).
- The expected difficulty curve is Appendix B.2. The probe CLI (§21.3) must print
  identical numbers.

---

## 11. Level state and game rules

### 11.1 The ids model

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

### 11.2 Rules on ids

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

### 11.3 A pour

1. Snapshot the source and target bands (for the animation).
2. Push `{V: copy of Vials, M: Moves}` to `Hist` (drop the oldest past 40).
3. `n = min(TopRun(i), 4 - target count)`; move the top `n` ids from `i` to `j`.
4. `Moves++`; `fresh = RevealTops()`; `completes = VialFull(j)`.
5. Clear the selection and any hint pointer; hide the stuck bar.
6. If `Rules.IsSolved(Colors(), 4)` → `OnSolved()` immediately (the level counts
   as won even if the app closes mid-animation).
7. Save. Start a `PourAnimation` (§14).

When the pour animation ends: reset the source's lift; set wobble (source
`0.07w`, target `max(current, 0.06w)`); play the plop; if `fresh` has ids in the
source, play the reveal sound and a white sparkle at the source's new surface;
if `completes`, run **Celebrate** (§11.9); recompute `DoneSet` and the painting;
if the level is won and no other pours are animating, start the win sequence
after 250 ms, otherwise schedule the dead-end check.

`OnSolved`: `Won = true`; coins += `Spec.Reward`; stats (`won`, `hard` for tier
1, `super` for tier 2); `Clean = !Help`, and if clean coins += 5; if `N == 1` set
`tips.tut = true`; `level = max(level, N + 1)`; `cur = null`; save now; start
generating level `N + 1` in the background.

### 11.4 Input

Tapping vial `i` (hit test in §12.3):

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

### 11.5 Boosters

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

### 11.6 Dead-end watcher

380 ms after the last pour finishes (debounced), on a worker thread: if
`ListMoves(Colors(), 4, false)` is empty, or `Solver.Solve(Colors(), 4, 5000)`
returns `!Ok && Exhausted`, the board is dead: show the stuck bar ("No way out
from here" with Undo, Add vial (hidden if already used), Restart) and play the
bonk. Tag each check with a state version and drop stale results.

### 11.7 Tutorial and coach line

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

### 11.8 Economy (`Economy.cs`)

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

### 11.9 Celebrate (a vial is corked)

`k` = number of full vials − 1. Start the cork drop and the glow. Show the float
label with the pigment name. After 150 ms: complete sound `k` (clamped to 12),
haptic [12,30,16], sparkles (pigment colour ×16 at power 1.2, white ×8 at power
0.9) at 0.2w above the mouth. The painting starts revealing that pigment 120 ms
after the pour ends.

### 11.10 Win sequence

All vials hop (stagger 55 ms); 46 splats in palette colours (§16); win sound;
haptic [20,60,20,60,40]; after 1250 ms open the Win sheet (§19.6).

---

## 12. Board layout

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
vialH   = Hgeo * w + 0.1w              // Hgeo = 3.807301 (§13.1)
gap     = 1.2w
used    = rows * vialH + (rows - 1) * gap + 1.6w
top     = max(0, (H - used) / 2) + 1.25w      // distance from the field top to the first row's mouth
counts  = rows == 1 ? [count] : [ceil(count/2), floor(count/2)]
mouth x = fieldCentreX + (k - (cnt - 1) / 2) * slotW
mouth y = fieldTopY - top - row * (vialH + gap)          // y-up
```

Re-layout on field resize and when a vial is added. Vials glide to new slots:
`dx += (x - dx) * min(1, dt * 0.014)` (same for y).

### 12.3 Hit testing

A tap belongs to the vial whose slot column contains it (`|x - dx| < slotW/2`,
nearest wins) and whose vertical band contains it: from `mouthY + lift + 0.9w`
down to `mouthY - Hgeo*w - 0.35w`.

---

## 13. Vials: geometry, meshes, liquid shader

### 13.1 Geometry (`VialGeometry.cs`, w = 1)

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

World polygon for a pose (§14.1): `world = P + Rot(phi) * ((local - L) * w)`,
where `phi` is the z-rotation in radians. World areas scale by `w²`: a vial
holding `u` units encloses `u * UnitA * w²`.

### 13.2 Meshes (`VialMeshes.cs`, built at runtime, w = 1)

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

### 13.3 Draw order inside a vial

Sorting order within the vial's `SortingGroup`: SelectGlow/CompleteGlow −1,
GlassBack 0, Liquid 1, Symbols 2, Highlights 3, Outline 4, Rim 5, Cork 6.
Between vials: resting vials sort 0; a vial being poured from sorts 100 so it
draws over its neighbours; streams sort 50; FX sort on the `Fx` layer.

### 13.4 Liquid shader (`Shaders/Liquid.shader`)

The CPU computes band tops in world space (§13.5) and the shader colours the
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
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Color.hlsl"
            #define MAX_BANDS 8
            // All colours arrive as sRGB (SetVectorArray does not convert). The
            // blending below happens in sRGB, as in the browser; the result is
            // converted to linear on output (§2, colour rules).

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

                col.rgb = SRGBToLinear(col.rgb);
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
array's size on first use). Pass `_BandColor` and `_Primer` as **sRGB** values
(the hex colours as written, not `.linear`); the shader converts.

`Gradient.shader` follows the same rule: its two colours arrive as sRGB vectors,
it interpolates in sRGB (as a CSS gradient does) and outputs
`SRGBToLinear(rgb)`.

### 13.5 Per-frame band upload (`LiquidBands.cs`)

For each visible vial:

1. Get the pose (resting §13.9 or pouring §14) and the bands: `BandsOf(i)` at
   rest; during a pour the source uses `TrimTop(srcBands, poured)` and the target
   uses `AddTop(dstBands, pigment, received)`. `TrimTop` removes an amount from
   the top bands (dropping emptied bands); `AddTop` merges into a visible
   top band of the same pigment or pushes a new band.
2. `poly = world polygon`, `minY`, `maxY`.
3. `acc = 0`; for each band `acc += units`;
   `top[b] = LevelFor(poly, acc * UnitA * w², minY - 1, maxY + 1)`.
4. Colours: pigment hex (§20.1), or `_Primer` for hidden bands.
5. Wobble: `_Wob = min(0.09w, wob)`, `_WaveK = 2π / (1.15w)`,
   `_WavePhase = timeMs * 0.011`.
6. `_GlossAxis`: world positions of local `(-0.5, -Hgeo/2)` and `(0.5, -Hgeo/2)`.

### 13.6 Symbols and question marks (`SymbolLayer.cs`)

One pooled SpriteRenderer per paint unit that needs a mark, using
`tex_symbols.png` (Appendix A).
- Hidden unit: cell 12 (question mark), world size `0.46w`, colour white α .82.
- Colour-blind mode on: visible units get the pigment's glyph (cell = pigment
  index), world size `1.3 × 0.34w`, colour = pigment ink (§20.1).
- Only whole units get a mark; skip everything when `|cos(phi)| < 0.4`.
- Position of the unit `u` (0-based from the bottom, counting all units below
  it): `Y = LevelFor(poly, (before + u + 0.5) * UnitA * w², ...)` and `X` = where
  the vial's centre line crosses `Y`:

```
s = Ly + (Y - P.y + Lx*w*sin(phi)) / (w*cos(phi))        // local y on the axis
X = P.x - Lx*w*cos(phi) - (s - Ly)*w*sin(phi)
```

### 13.7 Cork

`tex_cork` sprite, world size `0.8w × 0.6w`, pivot top-centre, local
position `y = +0.36w + drop` (so it sits from 0.36w above the mouth to 0.24w
inside). Shown only on full vials that are not animating. Drop animation over
520 ms from the moment the vial corks: `drop = (1 - easeOutBounce(t/520)) * 1.8w`.

### 13.8 Glows

- **Selected**: SelectGlow on, colour accent.
- **Corked**: `CompleteGlow` (fx_glow) sized `2.2w × (Hgeo + 0.6)w`, centred on
  the body, pigment colour, alpha `0.9 * sin(π t/1200)` for 1200 ms.

### 13.9 Motion (per vial, `dt` in ms)

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

## 14. The pour animation

### 14.1 Timeline (`PourAnimation.cs`)

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

### 14.2 Easing (`Easing.cs`)

```
easeInOutSine(t)  = -(cos(π t) - 1) / 2
easeInOutCubic(t) = t < .5 ? 4t³ : 1 - (-2t + 2)³ / 2
easeOutBack(t)    = 1 + 2.9 (t - 1)³ + 1.9 (t - 1)²
easeOutBounce(t)  = standard (n = 7.5625, d = 2.75)
```

### 14.3 Sound and haptics at pour time

At the tap: haptic 8, and schedule the glug train to start at `tA + lag` and
last `tB` (§18.3). At the end of the pour: plop for fill `d0 + n`.

---

## 15. The paint stream (`StreamRenderer.cs`, `Stream.shader`)

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
splashes spawn (§16).

---

## 16. Particles (`FxPool.cs`)

Pooled SpriteRenderers with `TintedSprite.shader`, updated by one script
(`ParticleSystem` isn't needed). All speeds are world units (= dp) per second,
converted from the web's px/ms. "Up" is +y.

| Kind | Texture | Spawn | Velocity | Gravity | Life | Size (radius) | Rotation / fade |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Splash burst | fx_droplet | 7 when the stream first lands, at `(end.x, sy)` | vx ±80, vy +120..+320 | −1200 | 380 | `w·(0.04..0.08)` | alpha `1 - q²`; dies when it falls below `sy` |
| Splash spray | fx_droplet | 1 per 38 ms on average while flowing, at `end.x ± 0.1w` | vx ±60, vy +70..+190 | −1200 | 300 | `w·(0.03..0.06)` | as above |
| Spark | fx_spark | `Sparkle(x, y, colour, count, power)` | random direction, speed `(80..300) · power`, plus vy +80 | −400; velocity × `0.985^(dt/16.67)` | 500..900 | `w·(0.07..0.15)`, shrinking to 40% | rotation `spin + 6 rad/s`; alpha `1 - q²` |
| Splat (win) | fx_splat | 46 at `(W/2 ± 0.15W, 0.45H below the field top)` | vx ±450, vy +450..+1000 | −1100 | 1300..2000 | `w·(0.08..0.20)` | rotation `spin + 4 rad/s`; alpha `min(1, (1 - q)·2.2)`; palette colours in turn |

`q` = life fraction. Sparkle calls: corking (§11.9); reveal (white ×8, power
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

## 17. Paintings

Every level has a small abstract painting with one shape per colour. It
starts as a pencil underdrawing, and each pigment brushes into its shape when
its vial is corked. Finished paintings are the win screen's centrepiece.

### 17.1 Pipeline

`ArtBuilder.Build(n, K)` (§10.9) → flatten paths into contours → build meshes in
`PaintingRig` → render with `PaintingCamera` into a RenderTexture (800 × 600,
ARGB32, MSAA 4, depth+stencil 24) → shown by a `RawImage` inside the frame.

`PaintingRenderer.Render(RenderTexture rt, List<ArtShape> art, int[] palette, float[] progress)`
applies the state and calls `PaintingCamera.Render()` manually. It is used for
the easel (every frame during a reveal, otherwise on change), the lobby preview
(all progress 0), the win sheet (all progress 1) and nowhere else.

### 17.2 Flattening (`PathFlattener`)

- Split into contours at each `MoveTo`; `Close` closes the current contour.
- `Arc`, with HTML canvas semantics: if not `Ccw` and `end - start >= 2π`, a full
  circle; otherwise the sweep is `(end - start) mod 2π` going clockwise in art
  space (increasing angle). With `Ccw`, sweep negative. Points:
  `(cx + r cos a, cy + r sin a)`. Segments: `max(12, ceil(|sweep| · r / 3))`.
  An arc following a current point on the same contour connects with a line
  (for `arch` that point already coincides).
- `Quad`: 16 segments.
- Convert every point to rig space: `(x, 300 - y)`.

### 17.3 Meshes per shape

- **Fill**: `ring` (even-odd) → build the annulus directly as a strip between its
  two circles. `dots` → one fan per circle. Everything else → ear-clip the single
  contour (`Triangulator`). `uv0` = art-space `(x, y)` (y-down) for the shader.
- **Streaks**: 10 quads (rounded caps) from `(sx, sy)` to
  `(sx + len·W·0.5, sy + (v − 0.5)·3)`, with `sx = X + u·W·0.7`, `sy = Y + v·H`
  (X, Y, W, H = the shape's bbox), width `lw`, colour pigment light or dark
  (§20.1).
- **Pencil**: closed ribbon along each contour, width 1.5, colour `#5F6474`.
  None for the ground.

### 17.4 `BrushReveal.shader` (fill)

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

### 17.5 Streaks, pencil, ground

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

### 17.6 Frame

UI `Image` with `tex_frame_{light,dark}` (9-slice), 5 dp border, the RawImage
inset 5 dp; behind it `tex_frame_shadow` (9-slice), offset 12 dp down. Easel
frame height `clamp(76, 15.5% of screen height, 142)` dp, aspect 4:3.

### 17.7 How the painting follows the game (required in the build)

The painting on the easel is a core feature, not decoration: **while the player
sorts, the canvas above the vials paints itself one colour at a time.**

- **Where it is:** on the play screen, the framed canvas ("easel") sits at the
  top, under the top bar and above the coach line and the vials (§19.2), with
  the row of pigment dots under it. It is always visible while playing.
- **What it shows at level start:** the level's composition
  (`ArtBuilder.Build(N, K)`) as a pencil underdrawing on the canvas ground: every
  shape outlined, nothing coloured. When resuming a saved level, pigments that
  are already corked show fully painted straight away (no animation).
- **Shape ↔ colour:** shape `s` is painted with pigment
  `LevelState.Palette[s.Slot]`. The easel keeps `progress[slot]` (0..1) for
  each of the level's K colour slots.
- **Trigger:** whenever `DoneSet` is recomputed (end of every pour, undo,
  restart, add vial): for each slot, if its pigment is now in a corked vial and
  wasn't before, start its reveal (0 → 1 over 900 ms, starting 120 ms after the
  pour ends; §17.5); if its pigment is no longer corked, set its progress to 0
  immediately. The matching pigment dot fills at the same moment.
- **Rendering while playing:** re-render the easel RenderTexture every frame
  while any reveal is running, once after any instant change, and not at all
  otherwise.
- **End of level:** after the last vial corks, the easel finishes its last
  reveal and the Win sheet shows the same painting at full progress, larger, in
  the frame, captioned "Study No. N · K pigments · M pours".
- **Lobby:** the "Up next" card shows the next level's underdrawing (all
  progress 0) so the player sees the canvas they are about to paint.
- **Theme:** the canvas ground and pigments are the same in light and dark mode;
  only the frame sprite switches (`tex_frame_light` / `tex_frame_dark`).

Checks (add to the M5 acceptance and PlayMode tests): cork one vial on level 5
and assert its slot's progress is 0 before the pour ends, and reaches 1 within
1100 ms after; undo that pour and assert the progress returns to 0 in the same
frame; resume a saved level with two corked vials and assert those two slots
render at progress 1 with no animation.

---

## 18. Sound and haptics

Paint Sort's clips are the `sfx_*` group, rendered with master gain 0.7
through the compressor (§4.3). `PaintSortSfx` maps game events to `SfxPlayer`
calls; `PaintSortHaptics` maps them to `IHaptics` patterns.

### 18.1 Recipes (`PaintSortRecipes.cs`)

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

### 18.2 Generated audio files

46 files: `sfx_click`, `sfx_pick`, `sfx_drop`, `sfx_bonk`, `sfx_tink`,
`sfx_bubble_00`–`11`, `sfx_pour_hiss_1`–`4`, `sfx_plop_1`–`4`,
`sfx_complete_00`–`12`, `sfx_reveal`, `sfx_undo`, `sfx_hint`, `sfx_vial`,
`sfx_win`, `sfx_coin`, `sfx_hard_intro`, `sfx_superhard_intro`. `GenerateAudio`
also fills `SfxLibrary.asset` (SfxId → clips).

### 18.3 Playback (`PaintSortSfx.cs`)

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

### 18.4 Haptic patterns (`PaintSortHaptics.cs`)

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

## 19. UI layouts

Shared rules (fonts, sheets, toasts, theme binding, icons) are in §4.8;
Paint Sort uses the `AppDisplay` and `AppBody` fonts and the `ps_*` icons.

### 19.1 Paint Sort lobby

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

### 19.2 Play screen

```
PlayScreen (wall gradient by tier)
├─ TopBar: Back · Level column ("Level N" 24 display; tier badge under it: 10 bold caps, white on hard/super, radius 999) · spacer · Coin pill · Menu
├─ Easel: Frame (§17.6) + PigmentDots (11 dp rings, 2 dp pigment ring + 1 dp edge outline; filled and scaled 1.15 when corked, 300 ms)
├─ CoachLine (min height 40, 14.5 bold muted, centred, balanced wrap)
├─ FieldArea (flex; the board renders here; FloatLabels live here)
├─ StuckBar (hidden; radius 16, surface, shadow; rises in 300 ms): "No way out from here" (bad colour, 14 bold) · Undo · Add vial · Restart (small ghost buttons)
├─ BoosterBar (padding 6/12 + bottom safe area; 4 columns)
│  └─ BoosterButton ×4 (72 wide): icon tile 56×56 radius 19 surface with a 4 dp line-coloured drop; label (12 bold muted);
│     count badge top-right (23 high, accent; shows "+" on a coin-coloured badge when empty and buyable); "used" state at 45% opacity
│     order: Restart · Undo (undos left) · Hint (inventory) · Add vial (inventory; "used" after one this level)
└─ HardIntro overlay (§19.4)
```

### 19.3 `LevelRoadGraphic`

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

### 19.4 Hard intro

Full-screen overlay: background `--hard` darkened 12% (super: `--super` darkened
15%) with `ui_stripes` tiled at 5% black (7% for super). Card centred: kicker
"Hard level" / "Super hard level" (clamp 40–56 display, white, 4 dp dark drop),
"LEVEL N" (13 bold caps .14em, 85% white), "K colours[, some hidden]. Worth R
coins." (16). Animation: the card scales 2.2 → 1 and rotates −6° → 0 over 550 ms
with overshoot; the overlay's alpha is 0 → 1 over the first 8% of 2.1 s, holds to
85%, fades to 0. Tap or 2.1 s dismisses. Plays the intro sound and haptic.

### 19.5 Float label

At `(vial x, mouth y + 1.1w)` projected to the canvas: pigment name, 17 display,
pigment colour, 5 dp outline in `--surface`. Over 1.5 s: 0% alpha 0, scale 0.6,
y +10%; 15% alpha 1, scale 1.08, y −60%; 75% alpha 1, scale 1, y −120%; 100%
alpha 0, y −160% (percent of its own height, upward).

### 19.6 Sheets content

| Sheet | Eyebrow / title / body | Actions |
| --- | --- | --- |
| Win | eyebrow "Level N complete" (or "Hard level beaten" / "Super hard level beaten" in tier colour); title by tier (§20.2); body: framed painting (height min(25% screen, 210)), caption "Study No. N · K pigments · M pours", coin row counting up to the reward in steps of `max(1, round(total/12))` every 55 ms starting after 350 ms, plus " incl. 5 for no boosters" when clean. Not dismissable. | "Next level" (or "Next: hard level N+1" / "Next: super hard level N+1", styled by tier) · "Back to levels" |
| Pause (menu) | "Level N" / "Paused"; toggles: Colour symbols, Sound, Vibration | Resume · How to play · Restart level · Back to levels |
| Restart | "Level N" / "Start this level again?" / "The board goes back to how it started. Your 5 undos come back too." | Restart level · Keep playing |
| Buy | "Boosters" / "Out of undos" · "Out of hints" · "Out of spare vials" / description (§20.2); if short of coins append "It costs P coins and you have C. Levels pay 10, hard ones 30 and super hard ones 60." | "Buy 5 undos · 30 coins" / "Buy a hint · 40 coins" / "Buy a vial · 90 coins" (disabled if short) · Not now |
| How to play | "How to play" / "Sort the paint" / five rows (§20.2) | Got it |
| Hidden paint tip (first level with hidden paint, after the intro) | "New" / "Hidden paint" / "Grey layers with a question mark are paint you can’t see yet. Pour off whatever sits on top and the colour shows." | Got it |
| Settings | the app settings sheet (§4.2) | Done |

---

## 20. Pigments and strings

### 20.1 Pigments (`Pigments.asset`)

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

### 20.2 Strings

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

---

## 21. Save section, threading and the balance probe

### 21.1 Save section (`games["paint-sort"]`)

```json
{
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
```

The current board (`cur`) is saved after every pour, undo, restart and booster,
so a killed app resumes on the same board. The Play button says "Continue level
N" when `cur.n == level`. Defaults for a new save: `level 1`, `coins 120`,
`inv {hint 3, vial 2}`.

**Board status** (`PaintSortStatus`): `level > 1 ? "Level {level} · {coins}
coins" : "New · 120 coins to start"`; Cta `level > 1 || cur != null ?
"Continue" : "Play"`.

### 21.2 Threading and performance

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

### 21.3 Balance probe

- **Window** `Playbox/Paint Sort/Balance Probe`: from/to fields, Run, a table
  (level, tier, colours, hidden, moves, casual, skilled, difficulty bar, ms),
  "all solvable" check (re-solve each board with budget 400000), CSV export.
- **CLI**: `Unity -batchmode -quit -projectPath . -executeMethod
  Playbox.Editor.ProbeCli.Run -from 1 -to 60`, printing the same columns as
  Appendix B.2, then `all solvable: yes|NO (count)` and the mean difficulty per
  tier. Exit code 1 if any level is unsolvable.

### 21.4 Analytics events

`level_start` (level, tier, colours, hidden), `level_complete` (level, tier,
moves, clean, reward), `level_restart` (level, moves), `dead_end` (level,
moves), `booster_used` (id, level), `booster_bought` (id, price). Each carries
`game` (§4.7).

---

# Part III: Hex Tile Sort

## 22. Rules

Hex Tile Sort is an endless run on a 19-cell hex board. Implement exactly:

- **Board.** 19 pointy-top hex cells in axial coordinates `(q, r)` with
  `|q|, |r|, |q + r| ≤ 2` (a "flower"). Cell order is `q` from −2 to 2, and for
  each `q`, `r` from −2 to 2, skipping cells outside the flower; neighbour
  directions are, in this order, `(1,0) (1,−1) (0,−1) (−1,0) (−1,1) (0,1)`. Both
  orders decide ties, so keep them.
- **Stacks.** A cell holds a stack of coloured tiles, bottom to top. Its **top
  run** is the number of same-colour tiles at the top.
- **Tray.** Three slots, each holding a generated stack. The tray refills (three
  new stacks) only when all three slots are empty.
- **Placing.** Drag a tray stack onto an **empty** cell (or tap a tray stack to
  select it, then tap an empty cell). Occupied cells never accept a stack.
  Placing never waits for merges to finish: the player can keep placing while a
  chain runs, and new stacks join the same chain.
- **Merging.** Whenever neighbouring stacks have the same top colour, a merge
  happens. The **receiver** takes the top runs of **all** its neighbours whose
  top colour matches (the **givers**) in one move. Every legal merge on the board
  is scored (§24.3) and the best one runs; ties go to the earliest receiver in
  cell order, with +10 for the stack placed last. This repeats until no merge is
  left.
- **Clearing.** A stack whose top run reaches **10** becomes **primed** (gold
  rim) for **500 ms**. While primed it can still receive (each feed restarts the
  500 ms) but never gives. When its time runs out and no merge is waiting, its
  whole top run pops, if it is still 10 or more.
- **Score** per pop: `run × 10 × combo + (run > 10 ? (run − 10) × 30 : 0)`, where
  `combo = min(chain, 10)` and `chain` counts pops since the board last went
  quiet (nothing primed). A chain of 2 or more shows "COMBO ×N" when it ends.
- **Colours and tiers.** A run starts with 4 colours; every 7 clears unlocks
  one more, up to 7 ("NEW COLOUR"). Tier = `min(3, floor(clears / 7))`.
- **New stacks** (§24.4) are 1–4 tiles in runs of 1–3, leaning toward colours
  already on top of the board, and get taller after 18 clears.
- **Start of a run.** Six seed stacks of 1–3 tiles, one colour each, on random
  cells, never giving two neighbours the same top colour.
- **End.** When every cell holds a stack, nothing is primed, nothing is still
  dropping, merging or refilling: "Board full". Score is kept as the best if it
  beats it.
- **Rotation.** Two buttons turn the board 60° left or right (360 ms). It
  changes only the view (adjacency is fixed) and is blocked while merges run.
- Restart starts a new run at once (no confirmation), as on the web.

## 23. World, camera and layout

Hex Tile Sort is the one 3D game. Tiles are real hex prisms; the perspective
camera and the z-buffer replace the web's painter's sort (`DEPTH_K`), and a flip
is a real 180° hinge rotation.

**World units.** Hex circumradius `R = 1`. Ground plane `y = 0`; the camera
looks toward +z and down, so "lower on screen" in the web (larger canvas y) is
smaller world z.

| Web (canvas, y-down, size `s`) | Unity world |
| --- | --- |
| cell offset `bx = s√3(q + r/2)`, `by = 1.5·s·r` | `x = √3(q + r/2)`, `z = −1.5·r` |
| hex corner `i` at angle `60i − 90°`: `(cos a, sin a)` | `(cos a, 0, −sin a)` (corner 0 points away from the camera) |
| tile thickness `th = 0.225 s` (screen rise per tile) | prism height `H = 0.45` (rises 0.225 on screen at the 60° pitch) |
| tile `i` drawn `i·th` above the cell | prism `i` spans `y ∈ [i·H, (i+1)·H]` |
| `G.rot` (clockwise on screen) | board root rotated by `+G.rot` about world +y |
| a screen offset of `k·s` upward at the board | world height `2k` (a vertical segment shows at half length) |

**Camera.** Perspective, vertical FOV 30°, pitch 60° (x-rotation 60°), aimed at
the board centre. A second camera, `HeldCamera`, renders layer `HexHeld` (tray
stacks, the held stack and their shadows) after the board with depth cleared, so
they always draw on top. The `Fx2D` overlay camera draws particles, score
floats and the banner (§27).

**Layout** (`HexLayout`, run on start and on every resolution change; dp, with
the play column capped at 520 × 960 dp and centred, like the web's `#app`):

```
area      = the rect between the bottom of the tier ribbon and the bottom of the screen (W × H)
trayH     = clamp(H × 0.21, 108, 168)
boardH    = H − trayH
s         = max(16, min((W − 28) / 9.4, boardH / 9.1))     // web uses 8.95; 9.4 leaves room for the near row's perspective growth
cy        = (boardH − 8s) × 0.62 + 4s + 0.35s                // board centre, from the top of the area
trayY     = H − trayH × 0.42 − 16
slotX[i]  = W × (i + 1) / 4,  i = 0..2
trayScale = clamp((trayH × 0.42) / (s × 2.2), 0.55, 0.82)
```

**Camera fit.** Place the camera so 1 world unit at the board centre is `s` dp
and the board centre lands at `(area.x + W/2, area.y + cy)` on screen:

```
d     = (screenHeightDp / 2) / (s × tan(15°))          // distance from camera to the board centre
Δ     = ((area.y + cy) − screenHeightDp / 2) / s        // world units; positive = target below screen centre
cam.position = boardCentre − cam.forward × d + cam.up × Δ
```

(Moving the camera along its own up axis moves the target on screen without
changing its scale.) Horizontal centring uses the same idea along `cam.right`
when the play column is not centred on the screen.

**Tray and held stacks.** A tray stack sits where the ray through
`(slotX[i], trayY)` meets `y = 0`, scaled by `trayScale × dist/d` (dist = camera
to that point), so it shows at `trayScale × s` per unit like the web. The held
stack sits where the ray through `(finger.x, finger.y − 1.1s)` meets `y = 0`,
raised by 0.3, scaled by `dist/d`.

**Backdrop.** A quad parented to the board camera at distance 200, sized to fill
the view, textured with `tex_hex_backdrop.png` (Appendix A: the page's three
CSS background layers). Camera clear colour `#0B0722`.

## 24. Engine (pure C#)

Namespace `Playbox.HexTileSort.Engine`, no `UnityEngine`. Randomness comes in
through `IRandom` (a `Mulberry32` seeded per run from the clock; tests pass fixed
seeds). The web uses `Math.random`; draw in **exactly the web's order** so a
seeded C# run and a seeded port of the JavaScript produce the same stacks.

### 24.1 `HexConfig.cs`

```csharp
namespace Playbox.HexTileSort.Engine
{
    public static class HexConfig
    {
        public const int ClearAt = 10;          // tiles of one colour needed to clear
        public const double ClearGraceMs = 500; // a full stack holds this long; restarts each time it is fed
        public const int ComboCap = 10;         // the score multiplier stops growing here
        public const int BoardRadius = 2;       // 19-cell flower
        public const int TraySlots = 3;
        public const int StartColours = 4;
        public const int ClearsPerTier = 7;     // clears needed to unlock the next colour
        public const int SeedStacks = 6;
        public static readonly string[] Faces = { "#FF5C63", "#FFB522", "#37D07A", "#26C0F2", "#A466FF", "#FF63B4", "#4A6BFF" };
        public static readonly string[] Names = { "coral", "amber", "lime", "cyan", "violet", "pink", "blue" };
        public static int MaxColours => Faces.Length;
        public static readonly (int dq, int dr)[] Dirs = { (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1) };
    }

    public interface IRandom { double Next(); }      // [0, 1)
    public static class Rnd { public static int Int(IRandom r, int n) => (int)(r.Next() * n); }   // web rnd(n)
}
```

### 24.2 `HexBoard.cs`

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.HexTileSort.Engine
{
    public sealed class Cell
    {
        public readonly int Q, R, Index;
        public readonly List<int> Stack = new List<int>();   // colour indices, bottom to top
        public bool Primed, Dropping, Locked;                // Locked: giving tiles away right now (empty in data, not on screen)
        public double PrimeMs;
        public Cell(int q, int r, int index) { Q = q; R = r; Index = index; }
        public int Top => Stack.Count > 0 ? Stack[Stack.Count - 1] : -1;
    }

    public sealed class HexBoard
    {
        public readonly List<Cell> Cells = new List<Cell>();
        readonly Dictionary<(int, int), Cell> _map = new Dictionary<(int, int), Cell>();

        public HexBoard()
        {
            int R = HexConfig.BoardRadius;
            for (int q = -R; q <= R; q++)
                for (int r = -R; r <= R; r++)
                {
                    if (Math.Abs(-q - r) > R) continue;
                    var c = new Cell(q, r, Cells.Count);
                    Cells.Add(c); _map[(q, r)] = c;
                }
        }

        public Cell At(int q, int r) => _map.TryGetValue((q, r), out var c) ? c : null;

        public List<Cell> Neighbours(Cell c)
        {
            var list = new List<Cell>(6);
            foreach (var (dq, dr) in HexConfig.Dirs) { var n = At(c.Q + dq, c.R + dr); if (n != null) list.Add(n); }
            return list;
        }

        public static int TopRunLen(Cell c)
        {
            int n = c.Stack.Count; if (n == 0) return 0;
            int col = c.Stack[n - 1], i = n - 1;
            while (i > 0 && c.Stack[i - 1] == col) i--;
            return n - i;
        }

        public static List<int> TakeTopRun(Cell c)
        {
            int len = TopRunLen(c), from = c.Stack.Count - len;
            var run = c.Stack.GetRange(from, len);
            c.Stack.RemoveRange(from, len);
            return run;
        }

        public bool Full { get { foreach (var c in Cells) if (c.Stack.Count == 0) return false; return true; } }
        public bool AnyPrimed { get { foreach (var c in Cells) if (c.Primed) return true; return false; } }
        public bool AnyDropping { get { foreach (var c in Cells) if (c.Dropping) return true; return false; } }
    }
}
```

### 24.3 `MergeChooser.cs`

A receiver `R` takes the top runs of all its matching neighbours at once. The
score rewards reaching ten, a bigger resulting run, freeing a cell, and a giver
whose newly exposed colour lines up with one of **its** neighbours (the
follow-up merge the naive "everything flows into the stack you just placed"
rule throws away).

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.HexTileSort.Engine
{
    public sealed class Merge { public Cell Receiver; public List<Cell> Givers; public int Score; }

    public static class MergeChooser
    {
        public static int ScoreMerge(HexBoard b, Cell R, List<Cell> givers)
        {
            int gained = 0;
            foreach (var g in givers) gained += HexBoard.TopRunLen(g);
            int total = HexBoard.TopRunLen(R) + gained;

            int score = total >= HexConfig.ClearAt ? 1400 + total * 6 : total * 22;
            if (R.Primed) score += 300;                         // topping up a full stack is great

            foreach (var g in givers)
            {
                int run = HexBoard.TopRunLen(g), rest = g.Stack.Count - run;
                if (rest == 0) { score += 70; continue; }       // giver empties, freeing a cell
                int exposed = g.Stack[rest - 1], bestRun = 0;
                foreach (var n in b.Neighbours(g))
                {
                    if (n == R || n.Stack.Count == 0) continue;
                    if (n.Top == exposed) bestRun = Math.Max(bestRun, HexBoard.TopRunLen(n));
                }
                if (bestRun > 0) score += 90 + bestRun * 12;    // uncovers a follow-up merge
            }
            return score;
        }

        /// A primed stack may receive, never give; a dropping stack is still in the air.
        public static Merge BestMerge(HexBoard b, Cell lastPlaced)
        {
            Merge best = null;
            foreach (var R in b.Cells)
            {
                if (R.Stack.Count == 0 || R.Dropping) continue;
                int col = R.Top;
                var givers = b.Neighbours(R).FindAll(n => n.Stack.Count > 0 && !n.Primed && !n.Dropping && n.Top == col);
                if (givers.Count == 0) continue;
                int score = ScoreMerge(b, R, givers);
                if (R == lastPlaced) score += 10;               // gentle tiebreak, nothing more
                if (best == null || score > best.Score) best = new Merge { Receiver = R, Givers = givers, Score = score };
            }
            return best;
        }
    }
}
```

### 24.4 `StackFactory.cs`

```csharp
using System;
using System.Collections.Generic;

namespace Playbox.HexTileSort.Engine
{
    public static class StackFactory
    {
        /// Board top colours, each repeated 1 + min(topRun, 8) times, in cell order. Colours not yet unlocked are skipped.
        public static List<int> BoardTopColours(HexBoard b, int colours)
        {
            var pool = new List<int>();
            foreach (var c in b.Cells)
            {
                if (c.Stack.Count == 0) continue;
                int col = c.Top;
                if (col >= colours) continue;
                int w = 1 + Math.Min(HexBoard.TopRunLen(c), 8);
                for (int i = 0; i < w; i++) pool.Add(col);
            }
            return pool;
        }

        public static int PickColour(HexBoard b, int colours, int exclude, IRandom rng)
        {
            var pool = BoardTopColours(b, colours).FindAll(c => c != exclude);
            if (pool.Count > 0 && rng.Next() < 0.62) return pool[Rnd.Int(rng, pool.Count)];   // no draw when the pool is empty
            int col, guard = 0;
            do { col = Rnd.Int(rng, colours); } while (col == exclude && ++guard < 12);
            return col;
        }

        public static int StackHeight(IRandom rng, int clears)
        {
            double r = rng.Next();
            if (clears > 18) return r < 0.22 ? 1 : r < 0.58 ? 2 : r < 0.88 ? 3 : 4;
            return r < 0.30 ? 1 : r < 0.70 ? 2 : r < 0.95 ? 3 : 4;
        }

        public static List<int> GenStack(HexBoard b, int colours, int clears, IRandom rng)
        {
            int left = StackHeight(rng, clears), last = -1;
            var tiles = new List<int>();
            while (left > 0)
            {
                int run = 1 + Rnd.Int(rng, Math.Min(left, 3));
                int col = PickColour(b, colours, last, rng);
                for (int i = 0; i < run; i++) tiles.Add(col);
                last = col; left -= run;
            }
            return tiles;
        }

        /// Six seed stacks; never two neighbours with the same top colour, so the board starts settled.
        public static void SeedBoard(HexBoard b, int colours, IRandom rng)
        {
            var pool = new List<Cell>(b.Cells);
            for (int i = 0; i < HexConfig.SeedStacks; i++)
            {
                var c = pool[Rnd.Int(rng, pool.Count)]; pool.Remove(c);
                var taken = new HashSet<int>();
                foreach (var n in b.Neighbours(c)) if (n.Stack.Count > 0) taken.Add(n.Top);
                var open = new List<int>();
                for (int k = 0; k < colours; k++) if (!taken.Contains(k)) open.Add(k);
                int col = open.Count > 0 ? open[Rnd.Int(rng, open.Count)] : Rnd.Int(rng, colours);
                int h = 1 + Rnd.Int(rng, 3);
                for (int t = 0; t < h; t++) c.Stack.Add(col);
            }
        }
    }
}
```

### 24.5 `Tiers.cs`

```csharp
namespace Playbox.HexTileSort.Engine
{
    public static class Tiers
    {
        public static int Tier(int clears) => System.Math.Min(HexConfig.MaxColours - HexConfig.StartColours, clears / HexConfig.ClearsPerTier);
        public static int Colours(int clears) => HexConfig.StartColours + Tier(clears);
        /// Progress bar fill: full once every colour is unlocked.
        public static double Into(int clears, int colours) =>
            colours >= HexConfig.MaxColours ? 1 : (double)(clears % HexConfig.ClearsPerTier) / HexConfig.ClearsPerTier;
    }
}
```

## 25. The resolver and its timings

`HexController` owns the run: `HexBoard`, tray (`List<int>[3]`), `score`,
`best`, `clears`, `colours`, `chain`, `over`, `rotating`, `dirty`,
`lastPlaced`, `selected`, `held`, and the flags `resolving` and `refilling`.

**Every frame** (dt in ms, clamped to 50, as on the web), in this order:
1. Step tweens (all animations below are tweens awaited by coroutines).
2. Step effects (§27.5–27.7), decay `glow` (4.5/s) and `ring` (2.4/s) on every
   cell, and count down `PrimeMs` on every primed cell (even while resolving).
3. **Pump:** if `!over && !resolving && (dirty || some cell is primed with
   PrimeMs ≤ 0)`: `dirty = false`, start the resolver.
4. **Game-over check:** if `!over && !resolving && !refilling`, nothing is
   dropping, nothing is primed, and the board is full: game over.
5. Tick the shown score toward the real one: step
   `sign(diff) × max(1, ceil(|diff| × 0.24))`, snap when within 2.
6. Render.

**The resolver** (one coroutine, re-entrancy guarded, up to 2000 iterations):

```
resolving = true
loop:
    m = BestMerge(board, lastPlaced)
    if m:
        groups = for each giver: (giver, TakeTopRun(giver))
        givers: hideBadge = true, Locked = true
        await FlipIn(groups, m.Receiver, chain)                  // §27.3
        givers: hideBadge = false, Locked = false
        m.Receiver.Stack += every group's run, in giver order
        if m.Receiver.Primed: m.Receiver.PrimeMs = 500           // fed again: the window restarts
        await Squash(m.Receiver, 0.62, 120 ms)
        givers: ring = 0.8
        continue
    due = cells with Primed and PrimeMs ≤ 0
    if due:
        for each c in due:
            c.Primed = false; c.PrimeMs = 0
            if TopRunLen(c) < 10: continue                       // no longer eligible
            chain++
            await PopRun(c, min(chain, 10))                      // §27.4, scores, clears++, tier check
        continue
    lit = false
    for each c not Dropping and not Primed with TopRunLen(c) ≥ 10: c.Primed = true; c.PrimeMs = 500; lit = true
    if lit: play prime
    if not AnyPrimed:                                            // only end the chain once nothing is counting down
        if chain ≥ 2: banner "COMBO ×{chain}"
        chain = 0
    break
resolving = false
```

**Place** (never locks input):

```
hide the hint line; selected = −1
cell.Stack = copy of tiles; cell.Dropping = true; lastPlaced = cell; tray[slot] = null; play place
drop the stack from +3.6 world units to 0 over 170 ms (easeOutQuad)
cell.Dropping = false; cell.ring = 1; Squash(cell, 0.9, 150 ms) (not awaited)
dirty = true
if all three tray slots are empty and !refilling: refilling = true; await RefillTray(); refilling = false
```

**PopRun(cell, combo):** `run = TopRunLen`, remove it, start the pop animation
(§27.4), 18 particles, `pts = run×10×combo + (run > 10 ? (run−10)×30 : 0)`,
`score += pts`, `clears++`, float "+pts", shake `min(9, 4 + combo×1.6)`, clear
sound for `combo`, tier check (if `Tiers.Colours(clears)` grew: `colours` = it,
banner "NEW COLOUR"), update the HUD and the best score; then wait 330 ms.

**Best score** is saved the moment `score > best` (as the web does on every HUD
update), so quitting mid-run keeps it.

**New run:** clear tweens and effects, `score = clears = chain = 0`,
`colours = 4`, `over = false`, rotation 0, `lastPlaced = null`; new board;
`SeedBoard`; show the hint line; `refilling = true`, refill the tray,
`refilling = false`.

**Game over:** `over = true`, play over, wait 220 ms, show the veil (§29).

## 26. Meshes and shaders

### 26.1 Meshes (`HexMeshes`, built once at runtime)

- **Tile prism:** pointy-top hexagon, circumradius 1, height `H = 0.45`, base at
  `y = 0`: a top hex (6 triangles, normal up), a bottom hex (normal down) and six
  side quads (flat normals). UV0.x = 0 for top/bottom, 1 for sides; UV0.y = the
  vertex's `y / H` (0 at the base, 1 at the top). Tiles are identical on both
  faces, so a tile that lands upside down after a flip looks the same.
- **Socket:** hex slab, circumradius 0.985, from `y = −0.06` to `y = 0`.
- **Outline loops:** closed hex ribbons for the glow, ring and primed rims,
  built with `RibbonBuilder` (width set per use, soft edges via `SoftStroke`).
- **Blob:** a ground quad for contact shadows and tray pedestals.

### 26.2 `HexTile.shader` (unlit, opaque; a `HexTileFade` variant is transparent with ZWrite Off for popping tiles)

Properties (per tile via `MaterialPropertyBlock`): `_Face` (sRGB colour),
`_Flash` (0–1 white overlay), `_Alpha` (fade variant only); on the material,
`_Detail` (optional greyscale texture multiplied into the top face with planar
xz UVs, default white, for user art). All shading is in
sRGB; output `SRGBToLinear`. The shading reproduces `makeTileSprite`:

- **Top and bottom faces** (`|n.y| > 0.5` in object space). Let `p` be the
  fragment's offset from the tile's centre in **world** xz (so light stays at the
  top-left of the screen while the board turns), in units of R, with z flipped to
  the web's screen sense: `p = (wx − ox, −(wz − oz))`.
  - Gradient along the web's diagonal from `(−0.7, −1)` to `(0.6, 1)`:
    `t = saturate(dot(p − a, b − a) / |b − a|²)`; stops: 0 `Shade(face, +0.26)`,
    0.48 `face`, 1 `Shade(face, −0.14)`.
  - Rim: distance from the fragment to the hex edge (object space) under
    0.0275 → `Shade(face, −0.34)` (the web's stroke of width `0.055s`, half of it
    inside).
  - Gloss: inside the polygon `(−0.866, −0.5) (0, −1) (0.866, −0.5)
    (0.706, −0.2) (−0.706, −0.2)` (web corners 5, 0, 1 and their inset, in `p`
    space) → blend white at α 0.20.
  - Flip shading: `k = |normalWS.y|`; blend toward `Shade(face, −0.58)` by
    `(1 − k) × 0.62` (the web's dimmed sprite drawn at `sin(angle) × 0.62`).
- **Side faces:** vertical gradient `lerp(Shade(face, −0.30), Shade(face, −0.55), 1 − uv.y)`.
- `_Flash`: `lerp(colour, white, _Flash)`.

### 26.3 `HexSocket.shader` (unlit, transparent)

From `makeSocketSprite`, with `p` in world-aligned units as above:
- Fill: vertical gradient by `p.y` from `rgba(9,5,28,.72)` at `p.y = −1` to
  `rgba(28,16,66,.52)` at `p.y = 1`.
- Edge: within 0.025 of the hex edge → `rgba(255,255,255,.10)` over the fill.
- Inner top shadow: the hex outline shifted by `(0, −0.12)` in `p` space, as a
  band of width 0.16, black at α 0.35, only inside the socket.

### 26.4 Other materials

- **Contact shadow:** blob with the generated `fx_hex_blob.png` (soft ellipse),
  tint `#05021A` at α 0.34, size 1.64 × 0.78 world units, centred 0.15 in front
  (−z) of the cell on the ground; scaled with the stack's squash.
- **Glow, ring, primed rims:** `SoftStroke` ribbons, core plus a wider soft halo
  (the web's `shadowBlur`), values in §27.2.
- **Tray pedestal:** blob with a white radial gradient (α 0.10 → 0) at α 0.9,
  radius 1.25 × 0.48 world units at the slot, on `HexHeld`.

### 26.5 Prefabs (built by `PrefabBuilder`)

```
HexRig.prefab
├─ BoardCamera            perspective 30°, pitch 60°, culling HexBoard, clear #0B0722
│  └─ Backdrop            quad at distance 200, tex_hex_backdrop
├─ HeldCamera             same projection as BoardCamera (copied every frame), culling HexHeld, clear depth only
├─ BoardRoot              rotates for the 60° turns
│  └─ Cell × 19           Socket, Ring (outline), Glow (outline), Primed (outline), StackRoot (drop/squash), ShadowBlob
├─ TrayRoot               3 × (Pedestal, StackRoot) on HexHeld
├─ Held                   StackRoot + ShadowBlob on HexHeld
├─ TilePool               Tile × 160 (MeshRenderer, HexTile material), re-parented as needed
├─ FlipPivots             Pivot × 24 (empty transforms for hinge flips)
└─ BadgePool              TextMeshPro (3D) × 19, billboarded, depth-tested
Fx2DCamera.prefab         orthographic overlay, 1 unit = 1 dp, culling Fx2D (shared with Car Loop)
```

## 27. Animations and effects

All durations in ms; easing names from `Easing.cs`. Hex Tile Sort's
**easeOutBack uses c = 1.9**: `1 + (c+1)(t−1)³ + c(t−1)²`; `smooth(t) =
t²(3 − 2t)`.

### 27.1 Drop, squash, ring

- **Drop:** stack root from `y = +3.6` to 0 over 170 (easeOutQuad).
- **Squash** `(amount, dur)`: `sqz = sin(π·p) × amount` over `dur` (linear `p`);
  stack root scale `(1 + 0.16·sqz, 1 − 0.22·sqz, 1 + 0.16·sqz)` about its base.
- **Ring:** set to 1 on placement (0.8 on givers after a merge, 0.55–0.5 on the
  hovered cell while dragging); decays 2.4/s; an outline on the ground at radius
  `0.98 + 0.10(1 − ring)`, width 0.09, `#B8FFEA` at α `ring × 0.9`.

### 27.2 Glows and rims

- **Merge preview** (while dragging over a cell): each neighbour whose top colour
  equals the held stack's top gets `glow = 1` (decays 4.5/s). Outline at the top
  face of its top tile (`y = n·H + 0.01`), radius 1.02, width 0.10, `#FFF7D6`,
  halo `#FFD86B` of width 0.5, alpha `glow × (0.55 + 0.45 sin 7t)`.
- **Primed:** outline at the top face, radius 1.05, width 0.11, `#FFE9A3`, halo
  `#FFC94A` of width `0.85 × (0.6 + 0.4 sin 11t)`. No countdown is shown: the gold
  rim says "ready"; how long is left is not something to watch.

### 27.3 Flips (`FlipAnimator`, port of `flipIn`)

Tiles hinge over the shared hex edge and land on the receiver.

```
FLIP = 250, GAP = 76, SIDE_OFF = 44
list = []
for giver index gi, run of m tiles (bottom→top j = 0..m−1):
    for j = m−1 down to 0:                                   // the top tile of the run topples first
        list += { colour, giver, zs = (giver.Stack.Count + j) × H + H/2,  start = gi × SIDE_OFF + (m−1−j) × GAP }
sort list by start                                           // landing order = departure order
idx = receiver.Stack.Count
for each o in list:
    ze = idx++ × H + H/2                                     // tile-centre height where it lands
    u  = normalise(receiver.xz − giver.xz)   (world, after board rotation);  D = distance
    hinge = giver.xz + u·D/2 at height zp = (zs + ze) / 2
    tile local offset from the hinge = −u·D/2 + up·(zs − zp)
total = FLIP + last start + 100
```

Each tile is parented to a pivot at its hinge; over its `[start, start + 250]`
window the pivot rotates by `180° × smooth(q)` about `cross(up, u)` (so the tile
rises over the edge toward the receiver and lands exactly on the stack top). The
tile scales by `1 + 0.07 × sin(angle)` mid-flight. After landing, a 120 ms bump:
scale `(1 + 0.16b, 1 − 0.22b)` with `b = 1 − after/120`. Each landing plays the
merge sound with index `combo × 2 + landed` (clamped to 10) and sets
`shake = max(shake, 2.2)`. Givers hide their badge during the flip.

### 27.4 Pops (`PopAnimator`, port of `popRun` / `drawPopTile`)

For each tile `i` of the cleared run (bottom first), `delay = 16i`; over 330
total, `p = clamp((ms − delay)/260, 0, 1)`, `out = clamp((p − 0.34)/0.66, 0, 1)`:
scale `1 + 0.34 × easeOutBack(min(1, 3p)) + 0.5 × out` about the tile centre,
lift `out × 1.4` world units, `_Alpha = 1 − out`, and while `out < 0.6` a white
flash `_Flash = (1 − out/0.6) × 0.75`.

### 27.5 Particles (`HexFx`, on the Fx2D overlay, dp)

18 per pop at the projected stack top `(x + rand(−0.5, 0.5)·s, y − run·th·0.5)`:
angle `rand(0, 2π)`, speed `90 + rand × 300` dp/s, `vy −= 180`; size
`r = s × (0.10 + 0.10 × rand)`, drawn as a `2r × 1.2r` rectangle rotated by
`rot` (start `rand × 6`, spin `(rand − 0.5) × 14` rad/s); colour white for every
third, else `Shade(face, (rand − 0.4) × 0.4)`. Gravity 1500 dp/s² (downward);
`life` from 1, minus 1.5/s; alpha = life.

### 27.6 Score floats and banner (Fx2D, `HexDisplay` font 800)

- **Float** "+pts" at the stack top minus `0.4s`: `vy = −70` dp/s, `vy *= 0.94`
  each frame, life 1.25 minus 1.05/s, alpha = life; size `0.82s` (`1.05s` when
  combo > 1), fill `#FFE38A`, stroke `rgba(10,5,30,.85)` width `max(3, 0.16s)`.
- **Banner** ("COMBO ×N", life 1.3; "NEW COLOUR", life 1.25) at
  `(W/2, cy − 3.6s)`: life minus 0.85/s, alpha = life, scale
  `1 + 0.22 × max(0, 1 − (1 − life) × 4)`; size `0.95s`, stroke
  `rgba(10,5,30,.9)` width `0.22s`, fill a vertical gradient `#FFF0B0 → #FFB020`
  (TMP colour gradient).

### 27.7 Badges and shake

- **Badge:** on the top tile of every stack whose top run is ≥ 2 (hidden on
  givers mid-flip): the number, `HexDisplay` 800 at `0.80s` on screen, outline
  `Shade(face, −0.52)` of width `max(2, 0.13s)`, fill `#FFF3C4` when the run is
  ≥ 8, else white. A 3D TextMeshPro billboard at the top face (so nearer stacks
  hide it), scaled each frame by `dist/d` to keep its screen size.
- **Shake:** decays 90 dp/s; each frame the board camera is offset by
  `(rand − 0.5) × shake` dp along its right and up axes (dp ÷ s = world units).

### 27.8 Tray (`HexTray`)

- **Refill:** three new stacks slide up from 90 dp below their slots; over 260
  (easeOutBack, c = 1.9) `slide[i] = clamp(p × 1.35 − i × 0.14, 0, 1)`.
- **Selected** stack (tap-tap play): bobs by `sin(6t) × 0.10s` and gets a gold
  outline (`#FFD86B`, α 0.55, radius `1.25 × trayScale`, width 0.08).
- **Held** stack: a shadow blob at α 0.30 under it; drawn at board scale.

## 28. Input (`HexInput`)

Uses screen dp, as the web does, so the feel is identical:

- **cellUnder(x, y):** among cells that are empty, not `Locked` and not
  `Dropping`, the one whose projected centre (`y = 0`) is nearest; accept it if
  within `1.35s`.
- **slotUnder(x, y):** `-1` if `y < trayY − 1.9s`; otherwise the occupied slot
  with `|x − slotX| < 1.25s`.
- **Pointer down** (ignored when `over` or `rotating`): on a tray slot → hold it
  (`held` at `(x, y − 1.1s)`), select it, play pick, preview glows for the cell
  under the held stack. Else, with a selected slot: if a cell is under the
  finger, place there; otherwise deselect.
- **Pointer move:** moved = true past 6 dp; the held stack follows; when the cell
  under it changes, refresh the preview glows and set that cell's ring to 0.55
  (and keep it ≥ 0.5 while hovering).
- **Pointer up:** with a held stack: over a cell → place; not moved → keep it
  selected (tap-tap play); moved but not over a cell → deselect and play bad.
  Pointer cancel drops the hold and the selection.
- **Rotate** buttons (and ←/→ in the editor): ignored while resolving, rotating
  or over; clear selection, hold and glows; play pick; rotate the board root by
  ±60° over 360 ms (easeOutCubic).

## 29. UI (`HexHud`, `GameOverVeil`)

One fixed dark look. Tokens: `ink #0B0722`, `deep #150C36`, `plum #241354`,
`panel rgba(255,255,255,.07)`, `panel-line rgba(255,255,255,.14)`,
`text #F3EEFF`, `dim #A79CD0`, `gold #FFC94A`. Fonts: `HexDisplay` (Baloo 2),
`HexBody` (Inter).

```
HexHud (play column max 520 dp, centred; safe area)
├─ Header (padding safe-top+12 / 14 / 6; row, gap 10)
│  ├─ Back            38×38, radius 12, panel fill, 1 dp panel-line border, app_back icon 20, press scale .92 (→ Playbox home)
│  ├─ Stat "Score"    panel, 1 dp panel-line border, radius 14, padding 6/12/7, min width 88;
│  │                  label 9.5 bold caps .14em dim; value 22 HexDisplay 800 (shown score, en-US separators)
│  ├─ Stat "Best"     same; value gold, 18, 2 dp top padding
│  ├─ spacer
│  ├─ Sound           38×38 icon button: hex_sound_on / hex_sound_off (toggles the app Sound setting)
│  └─ Restart         38×38 icon button: hex_restart (new run at once)
├─ Ribbon (margin 6/16/0; row, gap 10)
│  ├─ Label           "Tier N · K colours", 12 HexDisplay 700 caps .12em dim
│  └─ Bar             height 6, radius 99, fill white α .09; inner fill gradient #8B5CF6 → #22D3EE, width = Tiers.Into, animated 450 ms cubic-bezier(.2,.9,.2,1)
├─ (the board area: everything below the ribbon)
└─ BottomBar (absolute, bottom = safe-bottom + 6, padding 0/14; row, space-between)
   ├─ RotateLeft      42×42, radius 14, panel + border, hex_rotate_left 19, press scale .9
   ├─ Hint            "Drag a stack onto an empty cell", 12 dim, centred; fades to 0 over 500 ms at the first placement
   └─ RotateRight     42×42, hex_rotate_right
```

**Game-over veil:** full-screen radial gradient (60% × 50% at 50% 45%)
`rgba(36,19,84,.72) → rgba(11,7,34,.92)`, fades in over 280 ms. Card: width
`min(84%, 340)`, padding 26/22/20, radius 24, vertical gradient
`rgba(255,255,255,.10) → .045`, 1 dp panel-line border; enters from 14 dp lower
at scale .96 over 320 ms cubic-bezier(.2,1.2,.3,1).
- Title "Board full" (30 display 800).
- Body (13, dim, line height 1.55): "{clears} stack(s) cleared. Keep a free cell
  in the middle — that's where merges reach furthest."
- Score (52 display 800), sub-label (11 bold caps .16em dim): "new best" when
  `score ≥ best && score > 0`, else "final score".
- Legend: one 16×18 swatch (radius 4, vertical gradient `Shade(face, +0.2) →
  Shade(face, −0.25)`) per unlocked colour, gap 6.
- Button "Play again": full width, padding 13/18, radius 16, 17 display 800, text
  `#1A0B3B`, gradient `#FFD971 → #FFB020`, 6 dp drop `#C57C0A`; pressed: down
  4 dp, drop 2 dp. Starts a new run.

## 30. Sound and haptics

### 30.1 Recipes (`HexRecipes.cs`, group `hex_*`: master 1, no compressor)

The web's `tone(freq, dur, type, vol, slide)`: frequency `freq`, exponential
slide to `max(40, freq + slide)` over `dur` when `slide` is set; gain 0 → linear
to `vol` at 12 ms → exponential to 0.0001 at `dur`; voice ends at `dur + .02`.
So each web tone is `Tone(f, f1: slide ? max(40, f + slide) : 0, dur, gain: vol,
attack: .012, type, linAttack: true)`.

| File | Recipe |
| --- | --- |
| `hex_place.wav` | tone(190, .10, square, .035, slide −40) |
| `hex_merge_00..10.wav` | tone(330 × 1.06^i, .10, triangle, .045) for i = 0..10 |
| `hex_clear_1..8.wav` | base = 440 × 1.12^(c−1) for combo c = 1..8; for k, s in [0, 4, 7, 12]: tone(base × 2^(s/12), .16, triangle, .05) at k × .055 s |
| `hex_pick.wav` | tone(520, .05, sine, .03) |
| `hex_prime.wav` | tone(660, .10, sine, .045) + tone(880, .16, sine, .045) at .09 s |
| `hex_bad.wav` | tone(150, .16, sawtooth, .03, slide −70) |
| `hex_over.wav` | for k, s in [0, −3, −7, −12]: tone(392 × 2^(s/12), .28, triangle, .05) at k × .13 s |

### 30.2 Generated audio files

25 files: `hex_place`, `hex_merge_00`–`10`, `hex_clear_1`–`8`, `hex_pick`,
`hex_prime`, `hex_bad`, `hex_over`.

| Game event | Sound |
| --- | --- |
| pick up a tray stack, rotate the board | pick |
| stack placed | place |
| each tile landing in a flip | merge `min(combo × 2 + landed, 10)` |
| stacks become primed | prime |
| a run pops | clear `min(combo, 8)` |
| a dragged stack dropped off the board | bad |
| game over | over |

### 30.3 Haptics (a Playbox addition; the web has none)

| Event | Pattern |
| --- | --- |
| pick up | 6 |
| place | 8 |
| bad drop | [18, 30, 18] |
| pop | [12, 30, 16] |
| combo banner | 20 |
| game over | [30, 60, 30] |

## 31. Save section and board status

### 31.1 Save (`games["hex-tile-sort"]`)

```json
{ "best": 12840, "runs": 7 }
```

`best` is written the moment the score beats it; `runs` counts finished runs.
A run in progress is not saved (as on the web): leaving the game ends the run.

**Board status** (`HexStatus`): `best > 0 ? "Best {best:N0 en-US}" : "New"`;
Cta `best > 0 ? "Play again" : "Play"`.

### 31.2 Analytics events

`run_start`; `run_end` (score, clears, tier, best, new_best, duration_s);
`tier_up` (tier, clears). Like every event, each carries `game` (§4.7).

---

# Part IV: Car Loop

## 32. Rules

Car Loop is a one-tap timing game on a ring road. Implement exactly:

- **Track.** A closed loop (circle, rounded square, stadium, triangle, hexagon …)
  sampled into points 1 track unit apart. Road width 30; cars 24 × 13.
- **Feeders.** One or two vertical roads under the ring meet it with a smooth
  turn (radius 36). Your cars queue on them 34 units apart; the front car waits
  at the stop line.
- **One speed.** Every moving car (ring traffic, merging cars, the queue moving
  up) moves at one shared world speed `V(t)`. Rush-hour levels swing `V` with a
  sine wave.
- **Tap.** A tap releases the front car if it is at the stop line; otherwise the
  tap is held for 0.3 s and fires when the car arrives. On two-entrance levels the
  left half of the screen taps the left feeder and the right half the right one.
  **The clock starts on the first tap.**
- **Collision.** Each car is two circles (front and back, 5.6 from its centre). A
  crash is any pair of circles closer than 11.1, checked only for a car that is
  merging or within 16 units of joining the ring. Cars already on the ring never
  collide with each other, because they share one speed.
- **Win:** every one of your cars is on the ring and has finished merging.
  **Lose:** a crash, or the clock reaching zero. Two revives per attempt (ad or
  coins) continue the same attempt.
- **Stars** from the time left: ≥ 40% three, ≥ 15% two, otherwise one.
- **A close call** (a merge that passed within 17.5 of another car) pays +3 coins.
- **Levels** 1–10 are hand-made; from 11 they are generated from the level
  number, then proven playable by three bots, which also set the clock (§35).
  Variations arrive on a schedule: counter-clockwise rings, two entrances, rush
  hour, hard levels (×2 coins).
- **Boosters:** Slow-Mo, Green Light, Tow Truck, Autopilot (§38).
- **Economy:** coins from clears, close calls, a ×2–×5 rewarded multiplier, the
  daily reward and the shop; spent on boosters, revives and garage cars (§39).

### The fact that makes everything else work

Because every moving car shares one speed, the gap between a car you release and
any other car is **fixed at the moment you tap**. Each feeder therefore has a
**danger interval**: the ring offsets at which a released car will hit a ring
car. It is `[−22, +22]` on every shape (Appendix C). That one precomputed
interval drives the Green Light booster, Autopilot, the teaching zone on levels
2–3, the validation bots and the clock. **Never use the physics engine for cars:**
move them by distance along the sampled path and run the two-circle check
yourself, or the predictor and the real collisions drift apart.

## 33. Units, coordinates and scene

- **Track units** are the web's world units (road width 30, car length 24).
- **The engine keeps the web's coordinates** (y down, angles clockwise from +x on
  screen), so ported code and Appendix C match number for number. The view
  converts: Unity position `(x, −y, 0)`, z-rotation `−a` (radians → degrees).
  Every mesh built from engine coordinates flips y; since that reverses triangle
  winding, every Car Loop shader is `Cull Off`.
- **Camera** (orthographic, port of `layout()`), in dp with `bannerH = 58` (0
  with Remove Ads):

```
playing:  top = 110,  bottom = screenH − bannerH − 94
home:     top = logo.bottom + 4,  bottom = homeBottom.top − 6          (the attract-mode roundabout)
if bottom − top < 160:  top = max(60, top − 40);  bottom = top + 200
peek  = home ? 36 : 62
needW = bbox.x1 − bbox.x0;   needH = (stopY + peek) − bbox.y0
sc    = clamp(min((screenW − 18) / needW, (bottom − top) / needH), 0.38, 1.7)      // dp per track unit
ox    = screenW/2 − (bbox.x0 + bbox.x1)/2 × sc
oy    = top + ((bottom − top) − needH × sc)/2 − bbox.y0 × sc
```

  A track point `(x, y)` lands at dp `(ox + x·sc, oy + y·sc)` from the top-left.
  So `orthographicSize = (screenH / 2) / sc` and the camera sits at Unity
  `((screenW/2 − ox)/sc, −(screenH/2 − oy)/sc)`. Re-run on resize, on every
  screen change (home ↔ level) and when Remove Ads changes `bannerH`.
- **Scene** (`CarLoop.unity`): `CarLoopRig` (camera, background quad, static
  layer root, car pool, effect pools), the `Fx2D` overlay camera (screen-space
  vignettes), the UI canvas (screens, HUD, modal host, banner slot, toasts,
  coach) and `CarLoopController`.

## 34. Track geometry

Namespace `Playbox.CarLoop.Engine`, no `UnityEngine`. `Vec2` is a small
`(double X, double Y)` struct; `Pose` is `(double X, Y, A)`.

### 34.1 `Geom.cs`

```csharp
namespace Playbox.CarLoop.Engine
{
    public static class Geom
    {
        public const double CarLen = 24, CarW = 13, HitOff = 5.6, HitD = 11.1, CloseD = 17.5, RoadW = 30,
                            QGap = 34, TurnR = 36, StopPad = 8, Tail = 16, SafeM = 1.5;
        public const double Tau = System.Math.PI * 2;
    }
}
```

### 34.2 `PathTable.cs`

```csharp
using System;
using System.Collections.Generic;
using Playbox.Common;

namespace Playbox.CarLoop.Engine
{
    /// A path resampled to equal steps. X, Y, A are Float32Array in the web: store float, compute in double.
    public sealed class PathTable
    {
        public float[] X, Y, A;
        public double L, Step;
        public int Cnt;
        public bool Closed;

        public static PathTable Resample(IReadOnlyList<Vec2> pts, bool closed, double ds)
        {
            var P = new List<Vec2>(pts); if (closed) P.Add(pts[0]);
            int m = P.Count; var cum = new double[m];
            for (int i = 1; i < m; i++) cum[i] = cum[i - 1] + JsMath.Hypot(P[i].X - P[i - 1].X, P[i].Y - P[i - 1].Y);
            double L = cum[m - 1];
            int n = Math.Max(2, JsMath.JsRound(L / ds)), cnt = closed ? n : n + 1;
            double step = L / n;
            var t = new PathTable { X = new float[cnt], Y = new float[cnt], A = new float[cnt], L = L, Step = step, Cnt = cnt, Closed = closed };
            int j = 0;
            for (int k = 0; k < cnt; k++)
            {
                double s = k * step;
                while (j < m - 2 && cum[j + 1] < s) j++;
                double sg = cum[j + 1] - cum[j]; if (sg == 0) sg = 1;
                double u = JsMath.Clamp((s - cum[j]) / sg, 0, 1);
                t.X[k] = (float)(P[j].X + (P[j + 1].X - P[j].X) * u);
                t.Y[k] = (float)(P[j].Y + (P[j + 1].Y - P[j].Y) * u);
            }
            for (int k = 0; k < cnt; k++)
            {
                int i0 = k - 1, i1 = k + 1;
                if (closed) { i0 = (i0 + cnt) % cnt; i1 %= cnt; } else { i0 = Math.Max(0, i0); i1 = Math.Min(cnt - 1, i1); }
                t.A[k] = (float)Math.Atan2((double)t.Y[i1] - t.Y[i0], (double)t.X[i1] - t.X[i0]);
            }
            return t;
        }

        public Pose PoseAt(double s)
        {
            double f;
            if (Closed) { s %= L; if (s < 0) s += L; f = s / Step; } else f = JsMath.Clamp(s, 0, L) / Step;
            int i = (int)Math.Floor(f), j = i + 1; double t = f - i;
            if (Closed) { i %= Cnt; j %= Cnt; } else if (i >= Cnt - 1) { i = j = Cnt - 1; t = 0; }
            double xi = X[i], yi = Y[i], ai = A[i];
            double da = (double)A[j] - ai; if (da > Math.PI) da -= Geom.Tau; else if (da < -Math.PI) da += Geom.Tau;
            return new Pose(xi + (X[j] - xi) * t, yi + (Y[j] - yi) * t, ai + da * t);
        }

        /// Two circles per car, front and back. A crash is any pair closer than HitD.
        public static double CircDist(in Pose P, in Pose Q)
        {
            double o = Geom.HitOff, pc = Math.Cos(P.A) * o, ps = Math.Sin(P.A) * o, qc = Math.Cos(Q.A) * o, qs = Math.Sin(Q.A) * o, m = 1e9;
            for (int i = -1; i <= 1; i += 2)
                for (int j = -1; j <= 1; j += 2)
                {
                    double dx = P.X + pc * i - Q.X - qc * j, dy = P.Y + ps * i - Q.Y - qs * j, d = dx * dx + dy * dy;
                    if (d < m) m = d;
                }
            return Math.Sqrt(m);
        }
    }
}
```

### 34.3 `Shapes.cs`

| Shape | Type | Parameters |
| --- | --- | --- |
| `circle` | circle | r 112 |
| `bigCircle` | circle | r 130 |
| `squircle` | rect | w 108, h 108, corner 46 |
| `roundRect` | rect | w 140, h 100, corner 40 |
| `stadiumV` | rect | w 80, h 138, corner 80 |
| `stadiumH` | rect | w 150, h 80, corner 80 |
| `tall` | rect | w 92, h 150, corner 44 |
| `tri` | tri | s 150, corner 42 |
| `hex` | hex | s 128, corner 30 |
| `pent` | pent | s 130, corner 34 |

(`w` and `h` are half-sizes: the rect's corners are `(±w, ±h)`.)

```csharp
public static List<Vec2> LoopPoints(ShapeDef sh)
{
    var p = new List<Vec2>();
    switch (sh.Type)
    {
        case "circle":
            for (int i = 0; i < 260; i++) { double a = (double)i / 260 * Geom.Tau; p.Add(new Vec2(Math.Cos(a) * sh.R, Math.Sin(a) * sh.R)); }
            return p;
        case "rect":
            return RoundedPoly(new[] { new Vec2(-sh.W, -sh.H), new Vec2(sh.W, -sh.H), new Vec2(sh.W, sh.H), new Vec2(-sh.W, sh.H) }, sh.Corner);
        case "tri":
            { double r = sh.S; return RoundedPoly(new[] { new Vec2(0, -r), new Vec2(r * .866, r * .5), new Vec2(-r * .866, r * .5) }, sh.Corner); }
        default:   // hex, pent
            {
                int k = sh.Type == "hex" ? 6 : 5; double a0 = sh.Type == "hex" ? 0 : -Math.PI / 2;
                var v = new Vec2[k];
                for (int i = 0; i < k; i++) { double a = a0 + i * Geom.Tau / k; v[i] = new Vec2(Math.Cos(a) * sh.S, Math.Sin(a) * sh.S); }
                return RoundedPoly(v, sh.Corner);
            }
    }
}

public static List<Vec2> RoundedPoly(Vec2[] v, double r)
{
    int n = v.Length; var pts = new List<Vec2>();
    for (int i = 0; i < n; i++)
    {
        Vec2 p = v[(i - 1 + n) % n], c = v[i], q = v[(i + 1) % n];
        double ax = p.X - c.X, ay = p.Y - c.Y, bx = q.X - c.X, by = q.Y - c.Y;
        double la = JsMath.Hypot(ax, ay), lb = JsMath.Hypot(bx, by); ax /= la; ay /= la; bx /= lb; by /= lb;
        double th = Math.Acos(JsMath.Clamp(ax * bx + ay * by, -1, 1));
        double d = r / Math.Tan(th / 2), rr = r, maxD = Math.Min(la, lb) / 2 * .999;
        if (d > maxD) { d = maxD; rr = d * Math.Tan(th / 2); }
        double mx = ax + bx, my = ay + by, ml = JsMath.Hypot(mx, my); mx /= ml; my /= ml;
        double cd = rr / Math.Sin(th / 2), cx = c.X + mx * cd, cy = c.Y + my * cd;
        double a1 = Math.Atan2(c.Y + ay * d - cy, c.X + ax * d - cx), a2 = Math.Atan2(c.Y + by * d - cy, c.X + bx * d - cx);
        double da = a2 - a1; while (da > Math.PI) da -= Geom.Tau; while (da < -Math.PI) da += Geom.Tau;
        int st = Math.Max(2, (int)Math.Ceiling(Math.Abs(da) * rr / 2));
        for (int k = 0; k <= st; k++) { double a = a1 + da * k / st; pts.Add(new Vec2(cx + Math.Cos(a) * rr, cy + Math.Sin(a) * rr)); }
    }
    return pts;
}

/// Length of the unsampled loop polyline (used to size traffic).
public static double LoopLength(ShapeDef sh) { var p = LoopPoints(sh); double L = 0; for (int i = 0; i < p.Count; i++) { var q = p[(i + 1) % p.Count]; L += JsMath.Hypot(q.X - p[i].X, q.Y - p[i].Y); } return L; }
```

### 34.4 `Feeder.cs`

```csharp
public sealed class Feeder
{
    public double Sm, Fx, Fy, Sy, Le;          // merge distance on the loop, feeder x, turn start y, stop y, feeder path length
    public Vec2 M, T;                           // merge point and loop tangent there
    public PathTable Path;                      // stop line → turn → merge point
    public List<(double a, double b)> Danger = new List<(double, double)>();

    public static Feeder Make(PathTable loop, double tx)
    {
        double maxY = -1e9; for (int k = 0; k < loop.Cnt; k++) if (loop.Y[k] > maxY) maxY = loop.Y[k];
        int best = 0; double bd = 1e9;
        for (int k = 0; k < loop.Cnt; k++) { if (loop.Y[k] < maxY - 20) continue; double d = Math.Abs(loop.X[k] - tx); if (d < bd) { bd = d; best = k; } }
        double sm = best * loop.Step, Mx = loop.X[best], My = loop.Y[best], Tx = Math.Cos(loop.A[best]), Ty = Math.Sin(loop.A[best]);
        double R = Geom.TurnR, fx = Mx - Tx * R, Fy = My + R, Sy = Fy + Geom.StopPad, k4 = .5523 * R;
        Vec2 P0 = new Vec2(fx, Fy), P1 = new Vec2(fx, Fy - k4), P2 = new Vec2(Mx - Tx * k4, My - Ty * k4), P3 = new Vec2(Mx, My);
        var pts = new List<Vec2> { new Vec2(fx, Sy) };
        for (int i = 0; i <= 48; i++)
        {
            double t = i / 48.0, u = 1 - t;
            pts.Add(new Vec2(u * u * u * P0.X + 3 * u * u * t * P1.X + 3 * u * t * t * P2.X + t * t * t * P3.X,
                             u * u * u * P0.Y + 3 * u * u * t * P1.Y + 3 * u * t * t * P2.Y + t * t * t * P3.Y));
        }
        var path = PathTable.Resample(pts, false, 1);
        return new Feeder { Sm = sm, M = P3, T = new Vec2(Tx, Ty), Fx = fx, Fy = Fy, Sy = Sy, Path = path, Le = path.L };
    }

    /// Where a released car is after travelling u: on the feeder path, then on the loop.
    public Pose CandPose(PathTable loop, double u) => u < Le ? Path.PoseAt(u) : loop.PoseAt(Sm + (u - Le));

    /// Sweep the ring offset d; record every interval of d where a released car would hit a car at that offset.
    public void ComputeDanger(PathTable loop)
    {
        double lo = -90, hi = Le + 60, res = .5; double? st = null;
        for (double d = lo; d <= hi; d += res)
        {
            bool hit = false;
            for (double u = 0; u <= Le + Geom.Tail; u += 1)
            {
                var P = CandPose(loop, u); var Q = loop.PoseAt(Sm - Le + u + d);
                if (PathTable.CircDist(P, Q) < Geom.HitD) { hit = true; break; }
            }
            if (hit && st == null) st = d;
            if (!hit && st != null) { Danger.Add((st.Value, d - res)); st = null; }
        }
        if (st != null) Danger.Add((st.Value, hi));
    }
}
```

### 34.5 `Track.cs`

`TrackCache.Get(def)` keys on `shape | dir | feeders` and builds once:

```
pts  = LoopPoints(shape);  if dir < 0: reverse pts
loop = Resample(pts, closed: true, ds: 1)
cx, cy = mean of the loop samples
feeders = for each tx in def.Feeders: f = Feeder.Make(loop, tx); f.ComputeDanger(loop)
x0, x1, y0, y1 = loop sample bounds;  m = RoadW/2 + 6
for each feeder: x0 = min(x0, f.Fx − m); x1 = max(x1, f.Fx + m)
bbox  = (x0 − m, x1 + m, y0 − m, y1 + m)
stopY = max(f.Sy)
```

## 35. Levels: hand-made, generated, validated, baked

### 35.1 `LevelDef`

```csharp
public sealed class LevelDef
{
    public int N; public string Shape; public int Dir = 1; public string Pattern;
    public bool Hard, Dual, Teach; public string Tutorial;      // "tap", "gap", "ccw" or null
    public Pulse Pulse;                                         // null, or { Amp, Period } (rush hour)
    public int Speed, Traffic, Player, Time;
    public double Tx; public double[] Feeders; public uint Seed;
    public double GreedyT, RefT; public int Spare, Att;          // diagnostics from validation
}
public sealed class Pulse { public double Amp, Period; }
```

### 35.2 Hand-made levels 1–10 (`HandLevels.cs`)

| n | Shape | Traffic | Cars | Speed | Pattern | Extras | Teaches |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | circle | 0 | 5 | 120 | even | tutorial `tap` | tap (pointer hand, 30 s clock) |
| 2 | squircle | 2 | 4 | 125 | even | teach, tutorial `gap` | wait for the gap (danger zone shown) |
| 3 | stadiumV | 4 | 4 | 130 | pairs | teach | gaps come in sizes (zone shown) |
| 4 | squircle | 4 | 5 | 134 | random | tx −30 | off-centre entrance; Slow-Mo unlocks |
| 5 | circle | 5 | 5 | 137 | trains | | big gaps between trains |
| 6 | stadiumH | 5 | 6 | 140 | even | | Green Light unlocks |
| 7 | tri | 5 | 6 | 142 | random | | short ring |
| 8 | circle | 6 | 6 | 145 | pairs | dir −1, tutorial `ccw` | counter-clockwise |
| 9 | hex | 6 | 6 | 148 | random | | Tow Truck unlocks |
| 10 | squircle | 7 | 7 | 152 | pairs | hard | first hard level (×2 coins) |

Hand levels start from `{dir: 1, tx: 0}` and copy the row (the bots may still
lower traffic, §35.3).

### 35.3 Generator (`LevelGenerator.cs`, levels 11+)

**Traffic positions** (`TrafficPositions(def, L)`), RNG `Mulberry32(def.Seed)`:

```
n = def.Traffic; if n == 0: none
off = R() × L
even:          for i < n:  off + i×L/n
pairs/trains:  gs = 2 (pairs) or 3 (trains); groups = ceil(n/gs); k = 0
               for g < groups: b = off + g×L/groups; for j < gs while k < n: b + j×(CarLen + 6); k++
random:        tries = 0; while count < n and tries < 3000: tries++; s = R() × L;
               keep s if every kept o has min(|o − s| mod L, L − that) ≥ 32
```

Positions are not wrapped (they can exceed `L`); `PoseAt` wraps them.

**RawDef(n)** (levels ≥ 11; RNG `Mulberry32(n × 7919 + 17)`; `pick(a) =
a[(int)(R() × a.Length)]`). Draw in exactly this order; a draw marked
*(if …)* happens only when the condition holds:

```
hard  = n % 10 == 0 || (n > 20 && n % 10 == 5)
dual  = n ≥ 16 && n % 5 == 1
pulse = n ≥ 12 && n % 4 == 3
shape   = pick([circle, squircle, stadiumV, stadiumH, roundRect, tall, tri, hex, pent, bigCircle])
if dual: shape = pick([stadiumH, roundRect])
dir     = (n ≥ 11 && R() < .38) ? −1 : 1                         // the draw always happens for n ≥ 11
pattern = pick([even, pairs, trains, random, random])
tx      = dual ? 0 : pick([0, 0, 0, −30, 30])                     // draw (if !dual)
speed   = JsRound(min(185, 148 + (n − 10) × .75) × (n > 60 ? .95 + R() × .1 : 1) + (hard ? 6 : 0))   // draw (if n > 60)
if pulse: amp = .15 + min(.12, (n − 12) × .004); period = 3.2 + R() × 1.6; speed = JsRound(speed × .92)
L     = LoopLength(shape);  cap = 2L / (47 + .3 × speed)
fill  = lerp(.55, .88, sqrt(clamp((n − 10)/70, 0, 1))) × (hard ? 1.08 : 1) × (.92 + R() × .16) × (pulse ? .9 : 1)
total = max(7, JsRound(cap × fill))
player  = clamp(JsRound(total × .5 + R() × 1.2 − .6), 5, 10);  traffic = max(2, total − player)
```

Then for every level: `N = n`, `Seed = ToUint32(n × 104729 + 7)` (compute in
`long`), and `Feeders = dual ? (rect shape ? [−(w − corner) × .75, +(w − corner) × .75]
: [−50, 50]) : [tx]`.

Why the capacity sizing: a cautious player needs a gap of about
`47 + 0.3 × speed` units to merge, and gaps split as cars go in, so a ring holds
about `2 × length / gap` cars. Levels fill from 55% of that to 88% by level 80,
rising fastest early on.

**LevelDef(n)** validates and sets the clock:

```
for att = 0 .. 11:
    d = RawDef(n)                                   // hand level for n ≤ 10
    d.Traffic = max(0, d.Traffic − att)
    if att ≥ 4: d.Player = max(3, d.Player − floor((att − 2)/2))
    res = GreedySolve(d, extra: 3)
    ref = res.Ok && res.Spare ≥ (n < 25 ? 2 : 1) ? RefSolve(d, REF, maxT: 20) : fail
    if ref.Ok && RefSolve(d, CAUTIOUS, maxT: 60).Ok: break
slack  = (n ≤ 3 ? 2.2 : lerp(2, 1.4, clamp((n − 4)/60, 0, 1))) × (hard ? .95 : 1) × (dual ? 1.15 : 1)
d.Time = ceil(max(ref.T × slack + 2, d.Player × 1.2 + 3))
if n == 1: d.Time = 30
```

If all 12 attempts fail (never happens in levels 1–300; Appendix C), use
`Time = ceil(Player × 1.2 + 3)` and log a warning.

### 35.4 Bots (`Bots.cs`)

`REF = {lead .35, margin .12, gap .25}`, `CAUTIOUS = {lead .45, margin .15, gap .35}`.
Both bots step at `dt = 1/60` exactly, accumulating `t += dt` in `double`.

```
PlanTap(g, f, lead, e):            // aims at the middle of the first gap wider than ±e at least `lead` ahead
    fd = feeder f; L = loop length; s0 = fd.Sm − fd.Le; m = SafeM
    ds = [phase(c) − s0 for every car in Loop or Enter mode]
    safe(x) = for each d0 in ds: d = d0 + x; d −= floor(d/L)×L; if d > L/2: d −= L
              if any danger (a, b) has a − m ≤ d ≤ b + m: false
              true
    need = ceil(2e) + 1; run = 0
    for x = floor(lead − e); x < lead + L; x++:                 // x is an integer distance
        if !safe(x): run = 0; continue
        if ++run ≥ need: a = x − run + 1; b = x; while b < a + L && safe(b + 1): b++
                         return clamp((a + b)/2, lead, b − e)
    return −1

GreedySolve(def, extra):            // taps on the first safe frame; must leave room for `extra` more cars
    g = CreateScene(def); crashed = false; settled = 0; tDone = −1; t = 0
    hooks: crash → crashed = true; settled(c) → if c is a player car: settled++
    while t < 240:
        for each feeder f: c = queue front; if c && c.Q ≤ .001 && SafeAt(g, f, 0): Release(g, f)
        g.Wt += dt; d = WorldSpeed(g) × dt; k = max(1, ceil(d/1.5)); repeat k: StepWorld(g, d/k)
        t += dt
        if crashed: return { Ok: false, T: t, Spare: 0 }
        if tDone < 0 && settled ≥ def.Player:
            tDone = t; if extra == 0: break
            for i < extra: AddQueueCar(g, i % feeders)
        if tDone ≥ 0 && t > tDone + 2.2 × L / def.Speed: break
    return tDone < 0 ? { Ok: false } : { Ok: true, T: tDone, Spare: settled − def.Player }

RefSolve(def, P, maxT):             // plans each tap P.lead s ahead, ±P.margin s, never twice within P.gap s
    g = CreateScene(def); crashed = false; settled = 0; first = −1; t = 0; target = −1; tf = 0; next = 0; stuck = −1
    patience = def.Pulse ? def.Pulse.Period : .05
    while t < (first < 0 ? 0 : first) + maxT:
        if target < 0 && t ≥ next:
            any = false
            for each feeder f with a front car c:
                any = true; V = WorldSpeed(g)
                x = PlanTap(g, f, max(V × P.lead, c.Q), V × P.margin)
                if x ≥ 0: target = g.Dist + x; tf = f; break
            if any && target < 0 && no car is in Enter mode or has Tail > 0:
                if stuck < 0: stuck = t else if t − stuck > patience: return { Ok: false }   // no gap anywhere: stuck for good
            else stuck = −1
        if target ≥ 0 && g.Dist ≥ target:
            c = front car of tf; if c && c.Q ≤ .001: Release(g, tf) else feeder tf.Buffer = 1
            if first < 0: first = t
            target = −1; next = t + P.gap
        g.Wt += dt; d = WorldSpeed(g) × dt; k = max(1, ceil(d/1.5)); repeat k: StepWorld(g, d/k)
        for each feeder: if Buffer > 0: Buffer −= dt
        t += dt
        if crashed: return { Ok: false }
        if settled ≥ def.Player: return { Ok: true, T: t − max(0, first) }
    return { Ok: false }
```

### 35.5 The baked set (`LevelSource`, `CarLoopBake`)

- Levels **1–300 ship as data**: `Config/CarLoop/CarLoopLevels.json`, produced
  by running the **web engine itself** with the Node script in §0.5 (about 30 s,
  87 KB). Baked levels stay identical across app updates and can be hand-edited
  or remotely tuned per level.
- `CarLoopBake` (editor) checks the file: levels 1–300 present and in order;
  known shapes and patterns; `1 ≤ Time ≤ 60`; `Player 3–10`; `Feeders` 1 or 2
  values. It then runs the C# `LevelDef(n)` for every level and reports any field
  that differs (the JSON wins at runtime; differences point at a porting bug).
- **Past level 300** `LevelSource` runs the C# `LevelDef(n)` on a worker
  thread, caches the result, and requests `n + 1` while the level-complete panel
  is up (as the web does with its 450 ms timeout). If the player reaches a level
  that is not ready, show the level-intro text "LEVEL N" and start when it
  arrives.

### 35.6 JavaScript-to-C# parity rules for Car Loop

Everything in §10.10 applies, plus:

| JavaScript | C# | Why it matters |
| --- | --- | --- |
| `Float32Array` (path X, Y, A) | `float[]`, **read into `double` before any arithmetic** | `y[i1] - y[i0]` on two floats is float arithmetic in C#; in JS it is double. |
| `Math.hypot(a, b)` | `JsMath.Hypot(a, b)` (V8's algorithm: scale by the max, Kahan-compensated sum of squares, `sqrt × max`) | `Math.Sqrt(a*a + b*b)` can differ in the last bit and shift path samples. |
| `n*104729+7` passed to `mulberry32` | `JsMath.ToUint32(n * 104729L + 7)` | `a\|0` wraps at 32 bits. |
| `(cum[j+1]-cum[j])\|\|1` | `if (sg == 0) sg = 1` | |
| `for (d = lo; d <= hi; d += .5)` | the same accumulating `double` loop | Halves are exact in binary; don't rewrite it as `lo + i * .5` with a different end test. |
| `t += 1/60` | the same accumulating `double` | Bot times in Appendix C depend on it. |
| `Math.sin/cos/atan2` | `Math.Sin/Cos/Atan2` | May differ by an ulp on some CPUs. Geometry tests use a 1e-3 tolerance; level fields are compared exactly and any difference is reported, not fatal (the baked JSON is the shipped truth). |

## 36. Simulation (`Scene.cs`, `Car.cs`, `Sim.cs`)

```csharp
public enum CarKind { Player, Traffic }
public enum CarMode { Queue, Enter, Loop, Wreck, Tow, Gone }

public sealed class Car
{
    public int Id; public CarKind Kind; public CarMode Mode; public int F;      // feeder index
    public double S, U, Q; public int Slot;                                     // loop distance, feeder distance, queue offset
    public double Tail, MinD = 1e9; public bool Armed;                          // Tail: distance left in the post-merge check
    public Pose P; public double Born, RelT; public string Color;
    // presentation state (wreck flight, smoke timer, tow timer)
    public double Vx, Vy, Vr, WreckT, SmokeT, TowT;
}

public sealed class FeederState { public Feeder Def; public readonly List<Car> Queue = new List<Car>(); public double Buffer; }

public interface ISimHooks { void Released(Car c); void Merged(Car c); void Settled(Car c); void Crash(Car a, Car b); }

public sealed class Scene
{
    public LevelDef Def; public Track Track; public PathTable Loop;
    public List<FeederState> Feeders; public readonly List<Car> Cars = new List<Car>();
    public int NextId = 1; public double T, Wt, Dist, SlowK = 1; public bool Collide = true; public ISimHooks Hooks;
}
```

```
CreateScene(def, colours = ["#3B82F6"]):
    track = TrackCache.Get(def); g.Loop = track.Loop; g.Feeders = one FeederState per track feeder
    for i, s in TrafficPositions(def, Loop.L): add Car{Kind Traffic, Mode Loop, S s, Color colours[i % colours.Count]}
    for i < def.Player: AddQueueCar(g, i % feeders)
    UpdatePose every car

AddQueueCar(g, f): c = Car{Kind Player, Mode Queue, F f, Slot = queue count, Q = Slot × QGap, Born = g.T}; add to queue and to Cars

Phase(c)       = c.Mode == Loop ? c.S : feeder(c.F).Sm − feeder(c.F).Le + c.U
WorldSpeed(g)  = def.Speed × (def.Pulse ? 1 + Amp × sin(Tau × g.Wt / Period) : 1)

SafeAt(g, f, look):                 // safe to release from f now (look 0) or for the next `look` units of travel
    s0 = fd.Sm − fd.Le; m = SafeM
    for each car in Loop or Enter:
        d = Phase(c) − s0; d −= floor(d/L)×L; if d > L/2: d −= L
        if any danger (a, b) has a − m − look ≤ d ≤ b + m: return false
    return true

LightState(g, f):  no front car → off;  !SafeAt(g, f, 0) → red;  SafeAt(g, f, WorldSpeed(g) × g.SlowK × .4) → green;  else amber

UpdatePose(c):  Loop → Loop.PoseAt(c.S);  Enter → feeder path PoseAt(c.U);  Queue → (fd.Fx, fd.Sy + c.Q, −π/2)

Release(g, f):  c = queue.RemoveFirst(); if none: return
                c.Mode = Enter; c.U = 0; c.MinD = 1e9; c.Armed = false; c.RelT = g.T
                re-number the queue's Slots; Hooks.Released(c)

StepWorld(g, d):
    g.Dist += d
    for each car:
        Loop:  c.S += d; if c.Tail > 0: c.Tail −= d; if c.Tail ≤ 0: c.Tail = 0; Hooks.Settled(c)
        Enter: c.U += d; if c.U ≥ fd.Le: c.Mode = Loop; c.S = fd.Sm + (c.U − fd.Le); c.Tail = max(.01, Tail − (c.U − fd.Le)); Hooks.Merged(c)
        Queue: tq = c.Slot × QGap; if c.Q > tq: c.Q = max(tq, c.Q − d)
    for each feeder f with a front car c and c.Q ≤ .001:
        if c.Armed: if SafeAt(g, f, 0): Release(g, f)
        else if fd.Buffer > 0: fd.Buffer = 0; Release(g, f)
    UpdatePose every car in Loop, Enter or Queue
    if g.Collide: CheckCollisions(g)

CheckCollisions(g):
    for each a in Enter, or in Loop with Tail > 0:
        for each b ≠ a in Loop or Enter:
            dd = CircDist(a.P, b.P)
            if dd < HitD: Hooks.Crash(a, b); return
            if dd < a.MinD && !(b.Mode == Enter && b.F == a.F): a.MinD = dd
```

The simulation is advanced in sub-steps of at most 1.5 units of travel
(`n = max(1, ceil(d / 1.5))`) everywhere: in the game loop, the bots and the
attract-mode demo.

## 37. Game flow (`CarLoopController`)

### 37.1 States

`G.mode` is `demo` (the attract-mode ring on the Car Loop home) or `play`.
`G.state` in play mode:

| State | World moves | Clock runs | Next |
| --- | --- | --- | --- |
| `ready` | yes | no (waits for the first tap) | first tap → `playing` |
| `playing` | yes | yes (unless in tow mode) | win → `won`; crash → `crashed`; clock 0 → `timeup` |
| `paused` | no | no | resume → the previous state |
| `crashed` | yes (wrecks fly, traffic keeps going) | no | after 1.15 s → `over` + fail panel |
| `timeup` | no | no | after 0.75 s → `over` + fail panel |
| `won` | yes | no | after 1.5 s → complete panel |
| `over` | no | no | revive → `ready`; retry → new level |

### 37.2 The update loop (port of `update`, `dt` in seconds, clamped to 0.05)

```
g.T += dt
if state in {ready, playing, crashed, won, demo}:
    target = towMode ? .1 : (slowT > 0 ? .42 : 1);  g.SlowK += (target − g.SlowK) × min(1, dt × 7)
    wdt = dt × g.SlowK;  g.Wt += wdt;  d = WorldSpeed(g) × wdt;  repeat n = max(1, ceil(d/1.5)): StepWorld(g, d/n)
    each feeder: if Buffer > 0: Buffer −= dt                       // real time, not world time
    if state == playing && started && !towMode: time −= wdt; if time ≤ 0: time = 0; OnTimeUp()
    if slowT > 0 && !towMode: slowT = max(0, slowT − dt)
    if lightT > 0: lightT = max(0, lightT − dt)
    if state == demo: DemoTick(dt)
crashed: endT += dt; if endT > 1.15: state = over; open the fail panel (crash)
timeup:  endT += dt; if endT > .75:  state = over; open the fail panel (time)
won:     endT += dt; if endT > 1.5 and the panel isn't shown: open the complete panel
if state != paused: update effects (§41.4)
```

Then render (§41) and refresh the HUD (§43.4). Because the clock runs on world
time, Slow-Mo slows it too, and Tow mode freezes it.

### 37.3 Starting a level (`StartLevel(n)`)

1. Close every modal, clear pause reasons, leave tow mode, hide the coach.
2. `def = LevelSource.Get(n)`; scene with traffic colours from §37.8;
   `time = def.Time`, `state = ready`, `started = false`, zero `slowT`, `lightT`,
   `autoN`, `closeN`, `boostersUsed`, `revives`; hooks `Released`, `Merged`,
   `Settled`, `Crash` (§37.5).
3. Build the static layer (§41.2), switch to the game HUD, fit the camera.
4. HUD: "LEVEL N" plus a HARD chip on hard levels; booster bar; car pips; level
   intro (§43.4).
5. `stats.played++`, save, `level_start` (level, time, traffic, player).
6. If a booster unlocks at or below this level and its intro hasn't been seen,
   open the booster intro 700 ms later (only if still in `ready`), then the
   tutorial; otherwise the tutorial now (§37.7).

### 37.4 Tap (`Tap(f)`)

```
ignore unless mode == play, not tow mode, and state is ready or playing
c = front car of feeder f
if none: on two-entrance levels toast "That road is empty. Tap the other side."; return
if state == ready: state = playing; started = true                  // the clock starts here
if c.Armed: return
if autoN > 0: c.Armed = true; autoN−−; play auto; return            // Autopilot (§38)
if c.Q ≤ .001: Release(g, f) else feeder.Buffer = .3                 // held for 0.3 s
```

Input: pointer down anywhere on the game view (not on HUD buttons). In tow mode
the tap goes to `TowAt` instead (§38). Two feeders: the left half of the screen
taps the feeder with the smaller x. Editor keys: Space, ↑, Enter (left/only
feeder), ← and →, Esc or P (pause), 1–4 (boosters).

### 37.5 Hooks, win and lose

- **Released(c):** tap sound, haptic 8, a 4-puff tyre smoke behind the car
  (§41.4); hide the coach on tutorial levels or when it has no timer.
- **Merged(c)** (player cars): merge sound, update car pips, a green ring
  (`#7CF0A8`, radius 20, 0.45 s, width 2.2). Level 1, first merge: coach "Nice!
  Get them all in before the clock runs out." for 2.6 s.
- **Settled(c)** (player car finished its 16-unit tail, mode play): if
  `c.MinD < 17.5` and the state is ready/playing → `closeN++`, float "CLOSE!"
  (`#FFC23D`, 15) and "+3" (`#FFE27A`, 11) at the car, close sound, haptic 12.
  Then check the win: every player car is in Loop with `Tail ≤ 0` → win.
- **Win:** `state = won`, island glows green (fading), leave tow mode, hide the
  coach; 110 confetti at the island centre, a ring the size of the island
  (`#7CF0A8`, 0.8 s, width 4); win sound, honk at 380 ms, haptic [20,40,20];
  player cars flash their headlights (§41.3); `level_complete` (level,
  timeLeft, close, boosters, revives).
- **Crash(a, b)** (play mode): both cars become wrecks thrown off the road
  (§41.4), crash effects at their midpoint, shake 18, crash sound. If the state
  was ready/playing: `state = crashed`, island pulses red (held), haptic
  [60,40,90], hide coach, leave tow mode, `stats.crashes++`, `level_fail`
  (reason crash, cars in).
- **Time up:** `state = timeup`, island pulses red, leave tow mode, hide coach,
  fail sound, haptic [40,60,40], float "TIME!" (`#FF7884`, 30) at the island,
  `stats.timeups++`, `level_fail` (reason time, cars in).

### 37.6 Revive (`DoRevive(kind)`)

```
for each car in Wreck or Enter mode:
    player car → back to the FRONT of its feeder queue: Mode Queue, Armed false, MinD 1e9, angle −π/2
    traffic car → removed
re-number every queue (Slot = index, Q = Slot × QGap), clear feeder buffers, clear particles
if kind == time: time += 15
state = ready; started = false; glow off; shake 0
revives++; stats.revives++; save
coach "Back on the road. Tap when you are ready." for 3 s; `revive` (kind, level)
```

### 37.7 Tutorial, tips and level intro

- Level 1 (`tap`): coach "Tap anywhere to send a car into the roundabout." with
  a pointing hand at the feeder (stays until the first release).
- Level 2 (`gap`): coach "Traffic! Tap when the **red zone** is empty and your
  car slips in behind." with the hand.
- One-time tips (stored in `tips`, shown once ever): two entrances "Two
  entrances. Tap the **left** or **right** half of the screen." (hands on both
  feeders, 5 s); rush hour "Rush hour: the traffic **speeds up and slows down**.
  Time it." (4.2 s); counter-clockwise "This ring flows **the other way**. Watch
  the new gaps." (4.2 s); hard "Hard level: tighter gaps, **double coins**." (3.5 s).
  Checked in that order; the first that applies is shown.
- Levels 2–3 (`teach`) show the danger zone for free until won (§41.3).
- Level intro: "LEVEL N" with one tag: hard "HARD · ×2 COINS", else two entrances
  "Two entrances", else rush hour "Rush hour: traffic surges", else reversed
  "Counter-clockwise".

### 37.8 Traffic colours (`TrafficColoursFor(def)`)

Player colour (`PlayerColour()`): cyber → its glow colour; police and ambulance
→ `#E8EEFF`; otherwise the body colour. From `TRAFFIC_COLORS` keep colours that
contrast with it: if the player colour's saturation < 0.2, keep colours with
saturation ≥ 0.2; otherwise keep every colour with saturation < 0.2 and every
colour whose hue is more than 38° away (hue/saturation as in the web's
`hueSat`). Number of colours `k = n < 3 ? 1 : n < 8 ? 2 : 3`; pick them with
`Mulberry32(seed + 5)` by removing `pool[(int)(R() × pool.Count)]` k times.
Traffic car `i` gets colour `i % k`.

`TRAFFIC_COLORS = #3B82F6 #EF4444 #F472B6 #22C55E #A855F7 #22D3EE #FB923C #E5E7EB #FACC15 #14B8A6`.

### 37.9 Attract mode (`DemoDriver`)

On the Car Loop home the ring plays itself: def `{n 0, circle, dir 1, traffic 4,
player 16, speed 118, pairs, seed 4242, feeders [0], time 999}`, colours
`#3B82F6 #EF4444 #22C55E #A855F7`, collisions off. Each frame: `demoT −= dt`;
when `demoT ≤ 0`, the front car is at the line and `SafeAt(0, V × .3)`: release,
3 puffs, `demoT = rand(.5, 1.3)`. With 10 or more player cars on the ring, the
oldest is towed away. Keep the queue at 6 or more cars. The camera uses the home
layout (§33); no level number is drawn.

### 37.10 Pause bookkeeping

Pause reasons are a set: `modal`, `ad`, `screen`. Any reason present and the
state ready/playing → remember it and switch to `paused`; no reasons left and
paused → back to the remembered state. Opening a modal adds `modal` unless the
panel is marked "doesn't pause" (complete, fail, car reward, starter, rate);
closing the last pausing modal removes it. A full-screen ad adds `ad`. Leaving
the game screen for Garage/Shop/Levels mid-level adds `screen` (Back returns and
resumes). App backgrounded mid-level opens the pause panel.

## 38. Boosters

| Booster | Id | Unlock | Effect | Pack | Price | Colour | Icon |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Slow-Mo | `slow` | 4 | `slowT = 6` s: world speed eases to ×0.42 (the clock slows too) | 3 | 250 | `#36A3FF` | `i-slow` |
| Green Light | `light` | 6 | `lightT = 15` s: a traffic signal at each feeder and the coloured danger zone (red = crash now, amber = closing within 0.4 s of travel, green = go) | 3 | 250 | `#34C771` | `i-light` |
| Tow Truck | `tow` | 9 | Tow mode: bullet time (×0.1, clock frozen); tap a traffic car on the ring and a crane lifts it away for good. Cancel costs nothing. | 3 | 375 | `#FFC23D` | `i-tow` |
| Autopilot | `auto` | 13 | `autoN += 3`: the next 3 taps arm the front car; an armed car waits at the line and goes on the first safe frame | 3 | 450 | `#C08BFF` | `i-auto` |

Descriptions (panels): Slow-Mo "Slows every car to under half speed for 6
seconds. The clock slows with them."; Green Light "For 15 seconds a signal shows
the danger zone. Go on green, wait on red."; Tow Truck "Tap any traffic car and
a crane lifts it off the road for good."; Autopilot "Your next 3 cars wait at the
line and merge by themselves at the first safe gap."

`UseBooster(id)` (only in play mode, state ready/playing):
- Locked (`unlocked < unlock`): deny sound, toast "{Name} unlocks at level {n}".
- None left: booster buy panel (§43.3).
- Slow while running: toast "Slow-Mo is already running". Light while on: toast
  "Green Light is already on". Tow: if already in tow mode, leave it; if no
  traffic car is on the ring, toast "No traffic to tow on this ring"; else enter
  tow mode (the tow bar, §43.4) **without** consuming. Auto: toast "Autopilot
  ready: tap and your car waits for a safe gap".
- `Consume(id)`: `boosters[id]−−`, clear the coach flag for it, save,
  `boostersUsed++`, the booster's sound, haptic 15, refresh the bar,
  `booster_used` (id, level).
- `TowAt(x, y)` (track units): nearest traffic car in Loop mode within 32 units;
  none → deny, toast "Tap right on a traffic car". Else that car's mode becomes
  `Tow` (1.3 s animation, then removed), consume `tow`, leave tow mode, float
  "TOWED!" (`#FFC23D`, 14).
- **Button progress ring:** Slow `slowT/6`, Light `lightT/15`, Auto `autoN/3`,
  Tow 1 while in tow mode; a glow while active.
- **Intro:** the first time a level at or past a booster's unlock starts, the
  "New booster" panel gives 2 free, and the button pulses with a "TAP!" callout
  until that booster is used.

## 39. Economy, garage, daily reward

### 39.1 Constants (`EconomyConfig.asset`)

| Constant | Value |
| --- | --- |
| Starting coins | 150 |
| Level payout | `min(150, 25 + floor(1.5 × n))` |
| Star multiplier (1 / 2 / 3 stars) | ×1 / ×1.25 / ×1.5 |
| Hard levels | ×2 |
| Close call | +3 each (always paid, outside the multiplier) |
| Revive price (1st / 2nd per attempt) | 150 / 300 coins; max 2 |
| Time revive | +15 s |
| Multiplier bar | ×2 ×3 ×4 ×5 ×4 ×3 ×2 |
| Free-car progress per clear | `0.12 + 0.03 × stars` |
| Shop free coins | +100, 180 s cooldown |
| "Not enough coins" ad | +100 |

### 39.2 Level complete (`CompletePanel` logic, port of `openComplete`)

```
frac = time / def.Time;  stars = frac ≥ .4 ? 3 : frac ≥ .15 ? 2 : 1
stars[n] = max(stars[n], stars);  first clear (unlocked ≤ n) → unlocked = n + 1;  stats.won++
bonus  = rarity bonus % of the equipped car (0, 5, 10, 20)
base   = JsRound(levelPayout(n) × starMult[stars] × (hard ? 2 : 1) × (1 + bonus/100))
closeC = closeN × 3
target = cheapest coin car not owned (null if none); if target: carProg = min(1, carProg + .12 + .03 × stars)
save; if level n + 1 isn't ready, build it now (§35.5)
```

The needle sweeps the 7-segment bar back and forth at 0.69 of its width per
second (the web's `.0115` per frame at 60 fps); `idx = min(6, floor(pos × 7))`
and the Claim button shows `×multBar[idx]`. **Claim** stops the needle and plays
a rewarded ad (`level_multiplier`): earned → pay `base × mult`; not earned → the
needle resumes. **"No thanks, take {base + closeC}"** appears after 1300 ms and
pays `base`. Paying (once): count the reward up to the amount over 500 ms, add
`amount + closeC` coins (flying from the button), `level_reward` (level, coins,
mult), and after 1250 ms close the panel and run the after-level chain.

### 39.3 After-level chain (`AfterLevel(n)`)

Run in order, each step waiting for its panel to close:
1. Every car with a level cost now reached and not owned → "Unlocked" car panel
   (owned at once; "EQUIP NOW" or "Later").
2. `carProg ≥ 1` and a gift car exists → "New car" panel: claim with a rewarded
   ad (`gift_car`) → owned and equipped, `carProg = 0`; "No thanks" → `carProg = 0`.
3. `n == 5` and no starter pack bought or seen → the starter-pack offer.
4. `n == 8` and not rated → the rate prompt.
5. Interstitial check (§40.2), then `StartLevel(n + 1)`.

### 39.4 Garage (`Cars.asset`)

| Id | Name | Body type | Colour | Rarity (coin bonus) | Unlock |
| --- | --- | --- | --- | --- | --- |
| `zippy` | Zippy | compact | `#FFB020` | Common (0) | starter |
| `cab` | City Cab | taxi | `#FFD43B` | Common | 300 coins |
| `mint` | Mint Hatch | hatch | `#46E3B0` | Common | 500 coins |
| `patrol` | Patrol | police | `#F2F5FF` | Rare (+5%) | 3 rewarded ads |
| `ranger` | Ranger | pickup | `#FF7A45` | Rare | 900 coins |
| `vento` | Vento GT | sports | `#FF3B5C` | Rare | 1,400 coins |
| `medic` | Medic | ambulance | `#FFFFFF` | Rare | reach level 15 |
| `brute` | Brute | muscle (stripe `#FFC23D`) | `#2A2F45` | Epic (+10%) | 2,200 coins |
| `hauler` | Hauler | van | `#5B8CFF` | Epic | 3,000 coins |
| `bolt` | Bolt R | racer | `#22E0D0` | Epic | 6 rewarded ads |
| `aurum` | Aurum | super | `#FFC940` | Legendary (+20%) | 7,500 coins |
| `neon` | Neon X | cyber (glow `#FF3DF2`) | `#151A2E` | Legendary | reach level 40 |

Rarity colours: Common `#9AA6C4`, Rare `#36A3FF`, Epic `#C08BFF`, Legendary
`#FFC23D`. Every car has the same hitbox; skins never change difficulty.

Car state: equipped → "In use"; owned → "Owned"/EQUIP; coin price → BUY (not
enough → deny + "Not enough coins" panel; bought → owned and equipped, unlock
sound, haptic [20,30,20], toast "{Name} is yours!", `car_bought`); ad count →
"WATCH TO UNLOCK · a/b" (each earned view `adUnlock[id]++`; at the target → owned
and equipped, toast "{Name} unlocked!", else toast "{a} of {b} videos watched";
placement `car_<id>`); level → "REACH LEVEL N" (disabled). Equip: sound, toast
"{Name} equipped", `car_equipped`.

### 39.5 Daily reward (`Daily.cs`)

| Day | Reward |
| --- | --- |
| 1 | 100 coins |
| 2 | 150 coins |
| 3 | 2 Slow-Mo |
| 4 | 250 coins |
| 5 | 2 Green Light |
| 6 | 400 coins |
| 7 | 500 coins + 1 Tow Truck + 1 Autopilot |

`todayKey` is the local date. Available if `daily.last != today`; the day is
`daily.last == yesterday ? (daily.day % 7) + 1 : 1`. Claim ×1 or ×2 (rewarded
`daily_double`) multiplies everything; then `daily = {last: today, day}`, buy
sound, `daily_claim` (day, mult). The panel opens by itself 500 ms after the Car
Loop scene opens (not on every return to its home) when a reward is available
and at least one level has been played; the home gift button shows a pulsing red
dot while available.

### 39.6 Coins

`AddCoins(n, from)`: coins += n, save, and if `from` is a UI element, fly coins
from it to the visible coin pill (§43.1); `Spend(n)`: false if short, else
subtract, save, pop the pills. Pills on every screen show the same animated
number.

## 40. Ads, store and analytics

Car Loop uses the Core services (§4.5–4.7) through `CarLoopAds`.

### 40.1 Banner

Shown on every Car Loop screen (home, levels, garage, shop, gameplay) unless
Remove Ads is owned; hidden when leaving the Car Loop scene. `BannerSlot`
reserves 58 dp (plus the bottom safe area) at the bottom; the booster bar sits
on top of it, and the camera fit uses `bannerH` (§33).

### 40.2 Interstitials (`MaybeInterstitial(kind, then)`, port of `Ads.maybe`)

```
kind == level: sinceInt++   else (retry): retries++        // both saved
now  = seconds since app start
gate = !noAds && unlocked ≥ 4 && now − lastInterstitial ≥ 45 && now − lastRewarded ≥ 30
want = kind == level ? sinceInt ≥ 2 : retries % 3 == 0
if gate && want: sinceInt = 0; save; ShowInterstitial(kind, then) else then()
```

`lastInterstitial` and `lastRewarded` are session times (start at −∞).

### 40.3 Rewarded placements

Placement strings double as ad-network placement names, so analytics line up.

| Placement | Where | Reward |
| --- | --- | --- |
| `revive_crash`, `revive_time` | fail panel | continue (crash wreckage removed) / +15 s |
| `level_multiplier` | level complete | the payout × needle multiplier |
| `booster_slow`, `booster_light`, `booster_tow`, `booster_auto` | booster buy panel | +1 booster |
| `gift_car` | free-car offer | the car |
| `car_patrol`, `car_bolt` | garage | 1 view toward 3 / 6 |
| `daily_double` | daily reward | ×2 |
| `shop_free_coins` | shop | +100 coins, then 180 s cooldown |
| `no_coins` | not-enough-coins panel | +100 coins |

An earned rewarded view sets `lastRewarded` and `stats.adsWatched++`.

### 40.4 Analytics events

`level_start` (level, time, traffic, player), `level_complete` (level, timeLeft,
close, boosters, revives), `level_fail` (level, reason, in), `level_reward`
(level, coins, mult), `revive` (kind, level), `booster_used` (id, level),
`booster_bought` (id, with), `car_unlocked` (id), `car_bought` (id, coins),
`car_equipped` (id), `daily_claim` (day, mult), `rate_prompt` (stars), plus the
Core ad and store events. Watch first: fail rate and attempts per level, revive
take-up, multiplier take-up, day-1 retention against the interstitial cadence.

### 40.5 Store

The products are in §4.6 (`noads`, `carloop_starter`, `carloop_coins1`–`4`).
Shop and offer buttons call `Purchases.Buy` and show the localised price.
Remove Ads appears on the Car Loop home (hidden once owned) and in the shop; the
starter pack in the shop (until bought), on the home (after its first offer, until
bought) and once after level 5. "Restore purchases" in the shop and in Car Loop's
settings calls `Purchases.Restore` and toasts "Remove Ads restored." or "No
purchases to restore on this account."

## 41. Rendering (`CarLoopView`)

### 41.1 Camera and background

Camera clear `#0B1222`. A background quad on the camera (behind everything)
uses `ScreenBackdrop.shader`, computed in screen dp: a dot grid (1.5 × 1.5 dp
squares every 22 dp starting at 10 dp, `rgba(130,150,215,.07)`) and a radial
vignette centred at `(W/2, 0.42H)` from radius 30 to `max(W, H) × 0.8`:
`rgba(44,78,150,.2) → rgba(0,0,0,.4)`. The same shader on the `Fx2D` overlay
draws the Slow-Mo vignette (§41.4).

### 41.2 Static layer (`StaticLayerBuilder`, once per level and on resize)

All geometry is built in track units (y-down) and flipped (§33). `nIn` is the
inward normal sign: `+1` if the normal `(−sin a₀, cos a₀)` at sample 0 points at
the loop centre, else `−1`. Draw order, back to front:

1. **Trees** (seeded `Mulberry32(seed + 99)`, decor only): 70 candidates in the
   visible track rect: `x = lerp(x0, x1, R())`, `y = lerp(y0, y1, R())`,
   `r = 5 + R() × 7`; skip if closer than `RoadW/2 + r + 6` to any road or inside
   the island; a kept tree draws one more `R()` for its palette `q`. Shadow
   ellipse at `(x + 2, y + 3)`, `1.05r × 0.9r`, black α .35. Canopy: generated
   tree sprite A (`q < .5`: `#123A33`, inner `#1B5246`) or B (`#173F2E`, inner
   `#22573C`) at radius r (the inner circle at `(−.25r, −.3r)` radius `.62r`, a
   highlight `rgba(160,255,200,.08)` at `(−.35r, −.45r)` radius `.3r` are baked in).
2. **Island:** the loop offset inward by `RoadW/2 + 3`, triangulated, `#0F1E2B`;
   220 speckles (1.4 × 1.4, `rgba(60,180,140,.05)`) at `lerp(c − 200, c + 200, R())`
   for x and y, kept only inside the island (continue the same RNG); an inner
   shadow band 8 wide inside the island edge, black α .45.
3. **Lamps:** `nl = max(4, round(L/170))` at samples `floor((i + .5)/nl × cnt)`,
   offset outward by `RoadW/2 + 9`; skip any within 60 of a feeder's merge
   point. Glow radius 44 `rgba(255,210,130,.16) → 0` (`RadialFill`), post dot r
   2.4 `#39456A`, bulb r 1.2 `#FFE2A6`.
4. **Roads:** the loop and each feeder road (from `(fx, Sy + 2000)` along the
   feeder path), as ribbons with round joins and butt caps, in three passes over
   all roads: outline width `RoadW + 11` `#070C18`, rim `RoadW + 4` `#46557E`,
   asphalt `RoadW` `#29334F`.
5. **Edge lines** `rgba(205,218,255,.2)`, width 1.1, offset `±(RoadW/2 − 3)`; the
   outer edge is skipped over `[sm − (TurnR + RoadW/2 + 8), sm + 4]` at each
   feeder; each feeder gets both edges from `Sy + 2000` up to `Fy + 4`.
6. **Centre dashes** 7 on / 9 off, width 1.4, `rgba(150,165,205,.38)`, along the
   loop and each feeder's straight part.
7. **Chevrons:** `nc = max(3, round(L/150))` at samples
   `floor((i + .25)/nc × cnt)`, rotated to the loop angle: two triangles
   `(4, ±7.2) (−1, ±7.2 − 3.2) (−1, ±7.2 + 3.2)`, `rgba(180,195,235,.14)`.
8. **Stop lines:** at `y = Sy − CarLen/2 − 4`: rect `(fx − RoadW/2 + 3, y − 1.6,
   RoadW − 6, 3.2)` `rgba(240,244,255,.85)`; four give-way triangles at
   `x = fx − RoadW/2 + 6 + i(RoadW − 12)/3`: `(x − 3, y − 8) (x + 3, y − 8)
   (x, y − 3.6)` at α .55.
9. **Danger-zone ribbons** (built here, shown only when needed, §41.3): per
   feeder and danger interval `(a, b)`, the loop from `s0 + a` to `s0 + b`
   (`s0 = sm − Le`) sampled every 2 units: a wide ribbon (`RoadW − 5`, round
   caps) and a thin dashed one (`DashedStroke`, 4/4, width 1.6).
10. **Signals** (built here, shown with Green Light): at
    `(fx + side × (RoadW/2 + 11), Sy − 10)`, `side` = +1 if the feeder is right of
    centre: pole 2 × 16 `#0A0F1C`; housing 11 × 24, radius 3.5, `#0A0F1C`,
    1 px `#3B4C7C`; lamps r 2.6 at `dy` −6.5 (red `#FF4D5E`), 0 (amber `#FFC23D`),
    6.5 (green `#34C771`), off colour `#1C2236`; the lit lamp gets an additive
    glow r 12.

### 41.3 Per frame (`CarRenderer`, `CarLoopView`)

- **Island glow:** a second island mesh with `RadialFill` centred at the island
  centre (`+18` y on triangles), radius `max(w, h) × .62`; colour green
  `52,199,113` or red `255,77,94`; alpha held `0.32 + 0.2 sin(6t)` (crash, time
  up) or fading `max(0, 1 − t/1.6) × 0.6` (win); the rim at 15% of that.
- **Level number** (play mode): `CarDisplay` at size `min(w, h) × 0.42` at the
  island centre, `rgba(190,205,255,.11)`, or the glow colour at α
  `.55 + glowAlpha × .6` while glowing.
- **Decals:** scorch marks (radial `rgba(5,5,8,.7) → 0`, r 14–20).
- **Danger zone** (Green Light on, or a teach level not yet won): ribbon colour
  red/amber/green by `LightState`, wide ribbon α .30, dashed ribbon α .85 with
  dash offset `−20t`.
- **Cars**, in three passes: shadows (`tex_car_shadow`, offset `(1.6, 2.6)` plus
  `lift × (10, 14)` for towed cars, scale `1 + lift × .35`, α .6 for wrecks);
  headlight beams (additive, `tex_car_beam` at 10 ahead of the car, α .22 for
  your cars, .14 for traffic, only in Loop, Enter or Queue); bodies (the car's
  sprite, burnt for wrecks). A merging player car shows a tail outline (rounded
  rect 27 × 15 r 5, white, width 1.4, α `tail/16 × .6`). On a win, player cars on
  the ring flash an extra beam (α .5) while `sin(14t) > 0`. An armed car shows
  four pulsing amber dots at `(±6, ±11)` and a violet badge (r 8.5, `#C08BFF`) at
  `(RoadW/2 + 12, −2)` with a white steering-wheel glyph.
- **Tow:** a cable (`#C9D3EE`, 1.3) from the top of the view to a hook (amber r
  2.6) that drops to the car over 0.35 s (easeOutCubic), lifts it (scale
  `1 + lift × .35`, `lift` 0 → 1 over 0.35–0.6 s) and pulls it up and out
  (easeInCubic over 0.6–1.3 s) with a sway `sin(9t) × .15`. In tow mode every
  traffic car on the ring has a rotating dashed amber reticle (r `17 + 1.5 sin 8t`,
  dashes 5/4, width 2, rotation `2t`).
- **Signals** with Green Light: lamp colours from `LightState`.

### 41.4 Effects (`CarLoopFx`)

Particles are pooled world-space sprites with `v *= exp(−drag × dt)`,
`vy += grav × dt`, life `t / life`:

| Effect | Spawn |
| --- | --- |
| Tyre puff (release) | n puffs behind the car (11 back, ±3): velocity back 10–40 ± 12; smoke size 3–5 growing +10, `#8D98B8`, α .35, life .5–.9 |
| Crash | white ring r 60 (.45 s, width 5), amber ring r 38 (.6 s, width 3), a white flash r 70 (.22 s); 38 sparks (additive streaks, speed 90–330, `#FFD36B`/`#FFF3C2`, life .25–.6, drag 3.2); 10 fire blobs (additive radial, size 7–13 +16, speed 20–70); 16 smoke (size 5–9 +16, `#3A4258`, α .55, life 1.1–2.2, drag 1.2, upward −8); 16 debris (rectangles in the two cars' colours, speed 60–200, spin ±14, drag 2.4); a scorch decal |
| Wreck | each crashed car flies off: direction 0.55 × away from the impact + 0.7 × away from the island centre + 0.5 × its heading, speed 140–220, spin ±7–12; velocity decays `exp(−2.1 dt)`, spin `exp(−2.6 dt)`; smoke puffs every 0.06 s for 1.2 s then every 0.22 s until 5 s |
| Confetti (win) | 110 from the island centre, angle up ±0.4, speed 120–330, gravity 240, drag 1.6, life 1.6–2.6, colours `#FFC23D #34C771 #36A3FF #FF4D5E #C08BFF #FFFFFF`; width `size × abs(cos(rot × 1.3)) + .5` (flutter) |
| Rings | circle outline radius `size × easeOutCubic(k)`, width `w(1 − k) + .4`, α `1 − k` |
| Float text | `CarDisplay`, rises 30 × easeOutCubic(k), pops in with easeOutBack over the first 15%, fades over the last 30%, outline `rgba(8,12,24,.9)` width 4, life 1.1 s |
| Shake | 18 on a crash, decays 28/s, random offset ±shake/2 dp |
| Slow-Mo vignette | `Fx2D`, radial from 30% of `min(W, H)` to 75% of `max(W, H)`: transparent → `rgba(30,110,255, .32 × a)`, `a = clamp((1 − SlowK)/.58, 0, 1)`, × .6 in tow mode |

### 41.5 Prefabs (built by `PrefabBuilder`)

```
CarLoopRig.prefab
├─ Camera                 orthographic, culling CarLoop, clear #0B1222
│  └─ Backdrop            quad, ScreenBackdrop.shader (dots + vignette)
├─ StaticLayer            meshes rebuilt per level (§41.2)
├─ Cars                   CarView × 48 (Shadow, Beam, Body, Tail, Armed) — pooled
├─ Fx                     sprites × 256 (smoke, spark, fire, debris, confetti, ring, flash), decals × 16
├─ Texts                  TextMeshPro (3D) × 12 for float texts, 1 for the level number
└─ Tow                    cable, hook, reticles × 12
```

## 42. Generated car art (`CarSpriteBaker`)

`drawCarShape` is ported line for line onto `RasterCanvas` (§7.3). Each sprite
is a 34 × 24-unit canvas at **8 px per unit** (272 × 192 px), origin at the
centre, nose toward +x; import as Sprite, pivot centre, PPU 8, so it renders 34
× 24 track units. Port the helpers exactly: `rr` (rounded rect via `arcTo`),
`quad`, `bodyGrad` (vertical gradient across the width: `Shade(col, −.32)` at 0,
`+.08` at .3, `+.22` at .5, `+.08` at .7, `−.32` at 1), wheels, lights, mirrors,
windshield, and the per-type branches (`racer`, `cyber` with `shadowBlur 3 × PX`
glow, `super`, `police`, `muscle`, `ambulance`, `van`, `pickup`, `sports`,
hatch/compact/taxi/sedan defaults; lengths compact 21, hatch 22, taxi/police/
sedan 24, pickup/sports/ambulance/muscle/van/super 25; width 12.6 for super and
sports, else 13; corner radius 5 compact, 2.6 van/ambulance, else 4).

| Texture | Contents |
| --- | --- |
| `car_<id>.png`, `car_<id>_burnt.png` (12 cars) | the player cars; burnt = the same canvas with `rgba(18,14,12,.72)` painted `SourceAtop` |
| `car_traffic_<hex>.png`, `…_burnt.png` (11 colours: the 10 `TRAFFIC_COLORS` and the demo's `#22C55E`) | sedan in that body colour |
| `car_shadow.png` | 272 × 192: rounded rect 24 × 13 r 4, centred, blurred σ 1.3 units, black α .55 |
| `car_beam.png` | 240 × 144 (60 × 36 units at 4 px): two cones from `(2, h/2 ± 4)` to `(w, h/2 ± 4 ∓ 14 … ± 14)`, each filled with a radial gradient `rgba(255,236,170,.55) → 0` of radius 40; pivot at the left edge, centred |

Thumbnails in the garage, the progress bar and the car pips use the same car
sprites rotated −90° (nose up). The turntable (§43.2) uses them too.

**User car art**, if added later, is cropped tight to the 24 × 13
footprint at 192 × 104 px (8 px per unit). Import it with PPU 8 and pivot centre
so it lines up with the generated sprites, and assign it per car in `Cars.asset`
(body, lights layer drawn additively on top, wreck in place of the burnt
variant). Greyscale traffic bodies are tinted with the traffic colour through
their mask.

## 43. UI screens and panels

One fixed dark look. Fonts: `CarDisplay` (Bungee), `CarBody` (Fredoka).

### 43.1 Tokens and widgets

| Token | Value | Token | Value |
| --- | --- | --- | --- |
| night | `#0B1222` | go / goDeep | `#34C771` / `#1C8C4C` |
| night2 | `#0F1830` | amber / amberDeep | `#FFC23D` / `#D98A00` |
| panel / panel2 | `#17213C` / `#1F2C4E` | stop / stopDeep | `#FF4D5E` / `#B8283A` |
| edge / edge2 | `#2C3A62` / `#3B4C7C` | ad / adDeep | `#8E5CFF` / `#5A2FD0` |
| ink / ink2 / ink3 | `#F4F7FF` / `#B9C3E0` / `#7C88AC` | sky / skyDeep | `#36A3FF` / `#1A68C9` |
| shade | `#070C18` | coin | `#FFC940` |

- **RaisedButton** (`.btn`): min height 56, radius 18, padding 10/18, fill `c`,
  5 dp drop in `d` plus a soft shadow, white `CarBody` 600 20 with a 2 dp text
  shadow; a gloss on the top 42% (inset 8, white α .34 → 0); pressed: down 4 dp,
  drop 1 dp. Variants: go (default), amber (dark text `#3B2500`), ad (violet),
  stop, sky, ghost (panel2, ink2); sizes sm (46, 17, radius 15), xs (38, 15,
  radius 12, 3 dp drop); disabled: greyscale and darker. An "AD" tag inside ad
  buttons: pill, black α .24, `i-play` 14 + "AD" (700 12).
- **Round button** (`rbtn`): 46 × 46 (44 on the home row), radius 15, 2 dp edge2
  border, gradient panel2 → panel, 4 dp shade drop, icon 22–24.
- **Coin pill:** height 40, padding 0/6, fully rounded, `rgba(6,10,22,.74)`, 2 dp
  edge border, coin icon 26, number 700 17 tabular (min width 34), a green "+"
  button (26 circle, 2 dp goDeep drop) that opens the shop; pops (scale 1.14 at
  40%, 350 ms) when the number changes.
- **Coin flyer:** `min(12, 4 + floor(amount/30))` coins (28 dp) fly from the
  source to the visible pill: scale .3 → 1.1 at 35% with a random scatter
  (x ±70, y −70…20) → .75 at the pill, 720 + 40i ms after a 40i ms delay,
  cubic-bezier(.45,0,.7,1); each arrival bumps the shown number and pops the
  pill; coin sound on every other arrival.
- **Badges:** red count badge (20 high, stop, 2 dp stopDeep); pulsing red dot
  (14, 2 dp night border, scale 1.25 at 50% of 1.2 s).

### 43.2 Screens

**Home** (no solid background: the attract-mode ring shows through, with
gradients from `night` fading over 260 dp at the top and bottom):
- Top row (padding 12/12/0): **Back to Playbox** (Playbox addition, `app_back`
  icon), Settings (`i-gear`), Daily (`i-gift` in `#FF7AB6`, red dot when
  available), Remove Ads (`i-noads` in `#7CC4FF`, hidden once owned), Starter
  (`i-crown` in `#E7A3FF`, shown after the first offer until bought); coin pill
  on the right.
- Logo: `cl_sign` 70 × 70 with a 6 dp drop shadow; "CAR" (`CarDisplay` 39,
  gradient `#FFFFFF → #BFD4FF`, 4 dp `#0A3C8F` drop) over "LOOP" (46, gradient
  `#FFE27A → #FFAA1E`, 4 dp `#8A4B00` drop). (The web says "ROUNDABOUT / RUSH";
  in Playbox the game is Car Loop.) On screens under 640 dp tall: sign 52,
  31/37.
- Bottom (padding 0/16/14, gap 14): Play button (go, height 76 (66 small),
  `CarDisplay` 30, "PLAY" with "LEVEL N" under it in 600 14, breathing scale 1.03
  every 2.4 s); a row of three tiles (radius 18, 2 dp edge2, gradient, 4 dp
  drop; icon 30 + label 600 14): Garage (`i-garage` `#FFB020`), Levels (`i-grid`
  `#36A3FF`), Shop (`i-cart` `#34C771`).

**Levels:** header (back · "LEVELS" `CarDisplay` 22 · star-total pill with a
star); a 5-column grid (gap 10) of `max(unlocked + 14, 30)` tiles: aspect
1 : 1.08, radius 16, 2 dp edge2, gradient, 4 dp drop, number `CarDisplay` 19,
three 11 dp stars (on amber, off `#3A4670`); hard levels get a flame badge (22
circle, stop, top-right); the current level has a go border, glow and breathes;
locked tiles show a lock on night2 in ink3, and tapping one plays deny and shakes
it (±4 dp, 350 ms). Scroll the current level to the centre on open.

**Garage:** header (back · "GARAGE" · coin pill); preview card (margin 0/16,
radius 24, 2 dp edge, radial `#24365F → #101A33`): the turntable (190 high;
platform ellipse with a ring and shadow, a light sweep crossing it, the car
spinning at 0.8 rad/s inside a container squashed to 55% height), name
(`CarDisplay` 21), bonus line ("+N% coins from every level" / "No coin bonus",
600 13 ink2), rarity chip (radius 9, 700 11.5 caps, rarity colour, text night);
the action button (§39.4); a 3-column grid of cars (radius 16, 2 dp edge;
rarity dot 8 dp; thumbnail 44 × 70; name 600 13; status line 700 12 ink2);
selected: amber border and glow; equipped: green check badge; level-locked:
thumbnail darkened.

**Shop:** header (back · "SHOP" · coin pill without "+"):
- Starter offer card (until bought): gradient 135° `#7C3AED → #C026D3 (60%) →
  #F97316`, a "-70%" ribbon across the top-right corner, "STARTER PACK", "No
  ads, 2,000 coins and 3 of every booster.", amber price button.
- Remove Ads card (until owned): gradient 135° `#0E7490 → #2563EB`, "REMOVE
  ADS", "No banners and no breaks between levels. Bonus videos stay
  optional.", price button.
- "COINS": a free-coins row ("Free coins", "Watch a short video for 100
  coins.", ad button "+100" or the `m:ss` cooldown); four packs in a 2 × 2 grid
  (coin stacks of 1–4 coins, amount `CarDisplay` 18, price button, "POPULAR" /
  "BEST VALUE" tag on packs 2 and 3).
- "BOOSTERS": a row per booster ("{Name} ×3", "You have N.[ Usable from level
  L.]", amber coin-price button).
- "Restore purchases" link.

### 43.3 Modals (`ModalHost`) and panels

Card: width up to 360 (400 for "wide"), radius 28, padding 34/20/20, 2 dp edge2
border, gradient panel2 → panel (60%), big shadow; enters from scale .7 over
380 ms (cubic-bezier(.2,1.35,.4,1)); scrim `rgba(4,8,18,.72)`, fade 200 ms; a
ribbon tab overlapping the top edge (`CarDisplay` 14, 4 dp darker drop; sky, go,
stop, amber or ad); title `CarDisplay` 31 (go `#7CF0A8`, stop `#FF7884`, amber);
sub 500 15 ink2; a round close button (38) top-right unless the panel says
otherwise; tapping the scrim closes closable panels; Esc / Android back closes the
top closable panel.

| Panel | Content | Buttons |
| --- | --- | --- |
| Pause | ribbon "LEVEL N", "PAUSED"; three toggle tiles Sound / Music / Vibration (on: go border and icon; off: a red slash) | RESUME (go) · RESTART (amber sm, interstitial check then restart) · HOME (ghost sm → Car Loop home) |
| Settings | ribbon "SETTINGS"; toggles; rows Privacy policy, Restore purchases, Replay hints ("Show the one-time tips again"; resets `tips`, toast "Hints will show again"); **development builds only:** Developer tools (No ad fill, Short ads switches; +1,000 coins, +5 boosters, Unlock 30 levels, Reset save (tap twice)); version "Car Loop · Playbox {version}" | close |
| Complete (wide, doesn't pause, no close) | ribbon go "LEVEL N", "COMPLETE!"; three stars (middle 64, sides 52; each pops in at 350 + 260i ms with star sound i and haptic 10); chips: "m:ss left", "N close · +C" (if any), "+B% car bonus" (if any); reward (coin + amount, `CarDisplay` 34 coin colour); the multiplier bar (segments ×2 `#2F7DD6`, ×3 `#22A35D`, ×4 `#D99A12`, ×5 `#E0414F`; white needle with a pointer); next-car progress (thumbnail, "NEXT CAR · NAME", violet bar from the old to the new value over 900 ms after 700 ms, percentage counting up) | AD CLAIM ×N (ad) · "No thanks, take X" (link, after 1300 ms) |
| Fail (no close, doesn't pause) | ribbon stop "LEVEL N"; big crash or clock icon; "CRASH!" / "TIME'S UP!"; "**X of Y** cars made it in."; with revives left: an 8 s countdown ring (amber, `CarDisplay` 24) beside AD CONTINUE / AD +15 SEC (ad sm) and CONTINUE / +15 SEC · coin price (amber xs). The countdown pauses while an ad or another panel is on top; at 0 the revive box dims to 35% and stops responding, and RETRY becomes the primary button | RETRY (sky sm, or go when no revive) · Home (link) |
| Booster intro (no close) | ribbon amber "NEW BOOSTER"; big icon tile (96, radius 30, glow in the booster colour, rotating rays); name; description; chip "×2 on the house" | GOT IT |
| Booster buy | ribbon "BOOSTER"; big icon; name; description | BUY ×3 · price (amber) · AD GET 1 FREE (ad sm) |
| Not enough coins | ribbon amber "COINS"; coin icon; "NEED MORE COINS"; "You are **N** coins short." | AD GET +100 (ad) · VISIT SHOP (sm) |
| New car / Unlocked (no close, doesn't pause) | ribbon ad "NEW CAR" or amber "UNLOCKED"; car name; rarity chip ("Rare · +5% coins"); spinning turntable (150 high); "Your progress bar is full. Watch one video to drive it home." / "You reached level N. It's yours." | CLAIM CAR (ad) + "No thanks", or EQUIP NOW + "Later" |
| Starter pack (no close, doesn't pause) | ribbon ad "ONE-TIME OFFER"; crown with rays; "STARTER PACK"; "Everything you need for the busy roads ahead."; chips No ads, 2,000 coins, each booster ×3 | BUY · price · "No thanks" |
| Rate (no close, doesn't pause) | "ENJOYING THE RIDE?"; "Tap a star to rate Playbox."; five stars. Tapping star r lights 1–r and plays a star sound; after 500 ms: r ≥ 4 → the native in-app review request, else toast "Thanks for the feedback." | "Not now" |
| Daily reward | ribbon amber "DAILY REWARD"; "YOUR GIFT IS READY" / "SEE YOU TOMORROW"; "Come back every day. Day 7 is the big one." / "Next gift in H h M min."; seven tiles (3 columns; day 7 spans the row with a gift icon, gradient `#3B1F7A → #16203A`); claimed tiles dim with a green check; today's tile glows amber and breathes | AD CLAIM ×2 · CLAIM (when available) |

**Toast:** stacked under the top (76 dp), at most 3; padding 11/16, radius 14,
`rgba(10,16,32,.94)`, 2 dp edge2 border (go for good, stop for bad), 600 14.5;
enters from 14 dp above with overshoot (300 ms), stays 2.3 s, fades 250 ms.

### 43.4 Game HUD

```
GameHud (over the game view; safe area)
├─ TopRow (padding 10/12/0; three columns)
│  ├─ Pause          rbtn with i-pause
│  ├─ LevelBox       "LEVEL N" (CarDisplay 18) + HARD chip (i-flame, 700 11, stop, 2 dp drop)
│  │                 TimeRow: i-clock 17 · ClockBar · "m:ss" (CarDisplay 14, tabular)
│  └─ CoinPill
├─ CarsLeft (top 84, centred): one i-car pip (17) per car when ≤ 12 cars (off: white α .18; on: player colour, scale 1.12, glow), else a pip and "in / total"
├─ BoosterBar (bottom, above the banner; gradient night α .96 → 0 upward; padding 22/12/12; gap 12)
│  └─ BoosterButton ×4: 64×64, radius 20, 2 dp edge2, gradient, 4 dp drop; icon 32 in the booster colour;
│     count badge (24 high, go, 2 dp goDeep, 2 dp night border; amber "+" when empty);
│     locked overlay (night α .72, lock 18, "LV n"); progress ring (3 dp, booster colour, inset −5) and glow while active;
│     coach pulse + "TAP!" callout (CarDisplay 13 on amber) after the booster intro
├─ LevelIntro (34% from the top): "LEVEL N" (CarDisplay 44, glow) + tag pill; 1.7 s: 0% α 0 scale 1.5 → 15% α 1 scale 1 → 75% → 100% α 0 scale .92
├─ Coach: white bubble (max 270, radius 16, 600 15 #14203D, bold in skyDeep) at the top of the play area; pointing hands (64 dp i-hand, a tap ring every 1.1 s)
└─ TowBar (bottom = banner + 100; amber border panel): i-tow (amber) · "Tap a traffic car to tow it away." · Cancel (ghost xs)
```

**ClockBar:** width `min(190, available)`, height 14, radius 8, black α .5,
2 dp edge border; fill = time / limit, gradient go → `#8DF5B4`; ≤ 5 s after the
start: stop → `#FF8A95` with a pulsing red ring (0.6 s) and a tick sound each
second; during Slow-Mo: sky → `#9BD3FF`; before the first tap: fill at 55%
opacity.

## 44. Sound, music and haptics

### 44.1 Recipes (`CarLoopRecipes.cs`, group `cl_*`: sounds master .54, no compressor)

The web's `tone({f, f2, t = .15, type = sine, vol = .15, a = .006, lp, delay})`
is `Tone(f, f1: f2, dur: t, gain: vol, attack: a, at: delay, type, filter: lp ?
Lowpass : None, ff: lp, q: 1)`. Its `noise({t = .2, vol = .2, f = 1200, f2,
type = lowpass, q = .8, a = .01, delay})` is `Noise(dur: t, gain: vol, filter:
type, f, f1: f2, q, attack: a, at: delay)`.

| File | Recipe |
| --- | --- |
| `cl_tap.wav` | tone(150 → 340, .2, saw, .07, lp 900) + noise(.12, .04, 2600, highpass) |
| `cl_merge.wav` | tone(880, .1, .06) + tone(1320, .14, .04, delay .05) |
| `cl_close.wav` | noise(.28, .11, 3200 → 700, bandpass, q 1.2) + tone(1568, .22, .06, delay .06) + tone(2093, .25, .05, delay .13) |
| `cl_crash.wav` | noise(.8, .55, 3800 → 110) + tone(95 → 32, .55, .5) + tone(330 → 150, .28, square, .06) + noise(.35, .12, 5000, highpass, delay .05) |
| `cl_win.wav` | for i, f in [523, 659, 784, 1047]: tone(f, .3, triangle, .13, delay i × .09); tone(1568, .6, .06, delay .42); tone(2093, .5, .04, delay .5) |
| `cl_fail.wav` | for i, f in [392, 330, 262]: tone(f, .32, triangle, .12, delay i × .15) |
| `cl_coin.wav` | tone(1976, .07, square, .025) + tone(2637, .12, square, .025, delay .05) |
| `cl_click.wav` | tone(660, .05, triangle, .06) |
| `cl_star_0..2.wav` | f = [784, 988, 1175][i]: tone(f, .28, triangle, .12) + tone(2f, .18, .03, delay .04) |
| `cl_slow.wav` | tone(520 → 110, .7, saw, .06, lp 600) + noise(.6, .05, 900 → 200) |
| `cl_light.wav` | tone(880, .08, .07) + tone(1175, .1, .07, delay .12) |
| `cl_tow.wav` | tone(180 → 520, .6, square, .03, lp 900) + noise(.6, .06, 500, bandpass) |
| `cl_auto.wav` | tone(660, .06, square, .035) + tone(990, .09, square, .035, delay .07) |
| `cl_tick.wav` | tone(1250, .04, square, .035) |
| `cl_buy.wav` | for i, f in [784, 1047, 1319]: tone(f, .16, triangle, .1, delay i × .06) |
| `cl_unlock.wav` | for i, f in [523, 784, 1047, 1568]: tone(f, .35, triangle, .1, delay i × .08) |
| `cl_honk.wav` | tone(392, .16, square, .03, lp 1400) + tone(494, .16, square, .025, lp 1400) |
| `cl_deny.wav` | tone(220, .12, square, .04, lp 800) |
| `cl_whoosh.wav` | noise(.35, .06, 600 → 3000, bandpass, q .7) |

### 44.2 Music loop (`cl_music_loop.wav`, master .099, `RenderLoop`)

A gentle 4-chord loop, Cmaj7 · Am7 · Fmaj7 · G6 at 96 bpm, rendered as one
seamless 10 s loop (`RenderLoop(10, .099)`; tails past 10 s wrap onto the
start). Chords (MIDI): `[48,52,55,59] [45,48,52,55] [41,45,48,52] [43,47,50,52]`;
arpeggio order `[0,1,2,3,2,1,2,3]`; one step = 60/96/2 = 0.3125 s, 8 steps per
bar, 4 bars. `mtof(m) = 440 × 2^((m − 69)/12)`. For step `k` (bar `k / 8`,
position `s = k % 8`) at time `k × 0.3125`:
- tone(mtof(chord[arp[s]] + 12), .24, triangle, .045, lp 1700)
- if `s` is 0 or 4: tone(mtof(chord[0] − 12), .45, sine, .12)
- if `s` is odd: noise(.04, .015, 7000, highpass)

Plays on every Car Loop screen while Music is on (fade in 0.6 s on entering the
scene, out 0.4 s on leaving), ducked under ads.

### 44.3 Generated audio files and events

23 files: `cl_tap`, `cl_merge`, `cl_close`, `cl_crash`, `cl_win`, `cl_fail`,
`cl_coin`, `cl_click`, `cl_star_0`–`2`, `cl_slow`, `cl_light`, `cl_tow`,
`cl_auto`, `cl_tick`, `cl_buy`, `cl_unlock`, `cl_honk`, `cl_deny`, `cl_whoosh`,
`cl_music_loop`.

| Event | Sound |
| --- | --- |
| UI button, panel close | click |
| car released | tap |
| car merged | merge |
| close call | close |
| crash | crash |
| win | win, then honk at 380 ms |
| fail panel, time up | fail |
| coin arrives (every other) | coin |
| stars on the complete panel | star 0, 1, 2 |
| booster used | slow / light / tow / auto |
| last 5 seconds | tick each second |
| purchase, booster pack, daily claim, equip | buy |
| booster intro, car unlocked, reward earned | unlock |
| locked level or booster, can't afford | deny |

### 44.4 Haptics

| Event | Pattern |
| --- | --- |
| car released | 8 |
| close call | 12 |
| star on the complete panel | 10 |
| booster used | 15 |
| win | [20, 40, 20] |
| crash | [60, 40, 90] |
| time up | [40, 60, 40] |
| car bought | [20, 30, 20] |
| Vibration switched on | 25 |

## 45. Save section, board status and performance

### 45.1 Save (`games["car-loop"]`)

```json
{
  "unlocked": 1, "stars": { "1": 3 }, "coins": 150,
  "owned": ["zippy"], "equipped": "zippy", "adUnlock": { "patrol": 1 },
  "boosters": { "slow": 0, "light": 0, "tow": 0, "auto": 0 },
  "introSeen": { "slow": 1 }, "coachB": null, "tips": { "dual": 1 },
  "starter": false, "starterSeen": false, "rated": false,
  "daily": { "last": "2026-10-4", "day": 3 }, "carProg": 0.45, "freeCoinsAt": 0,
  "stats": { "played": 0, "won": 0, "crashes": 0, "timeups": 0, "revives": 0, "adsWatched": 0 },
  "sinceInt": 0, "retries": 0
}
```

Same fields as the web's `roundabout-rush-v1`, minus `sound`, `music`,
`haptics` and `noAds` (app settings and purchases in Playbox) and `dev`
(development builds keep it in `PlayerPrefs`). `daily.last` is the local date
as `Y-M-D` without padding; `freeCoinsAt` is Unix ms. Save after every change,
as the web does.

**Board status** (`CarLoopStatus`): `unlocked > 1 ? "Level {unlocked} ·
{coins} coins" : "New"`; Cta `unlocked > 1 ? "Continue" : "Play"`.

### 45.2 Performance

- Baked levels load instantly; `TrackCache.Get` (resample + danger sweep) takes
  a few ms on level start, so build the next level's track while the complete
  panel is up.
- Never run `LevelDef`, the bots or `ComputeDanger` on the main thread past the
  baked set; use the worker-thread path in §35.5.
- The static layer is a handful of meshes per level; cars, beams and shadows are
  pooled sprites; one draw call per material where possible (GPU instancing on
  the sprite materials).
- Budget: 60 fps with 20 cars, a crash burst (~100 particles) and Green Light on,
  on a mid-range Android phone.

---

# Part V: Shipping

## 46. Tests

**EditMode: Paint Sort**
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

**PlayMode: Paint Sort**
- Pour flow: tap source + target → animation completes within
  `tA + tB + tC + 50` ms and the board matches the engine.
- Win flow: start from a fresh save with `level` set to 4, play the solver's
  path through `BoardInput`; the Win sheet appears and the save shows level 5
  and 135 coins (120 + 10 + 5 for no boosters). Continue into level 5: the hard
  intro plays; winning it gives 170 coins.
- Resume: play 3 moves of a level, reload the scene, "Continue level N", same
  board.
- Easel: the three painting checks in §17.7 (reveal on cork, instant reset on
  undo, corked colours already painted on resume).

**EditMode: app**
- `SaveTests`: round trip; corrupt file → defaults; a `v: 1` file migrates to
  `v: 2` (music on, empty purchases, Paint Sort progress intact); unknown fields
  in a game section survive a write; "Erase all saved progress" clears `games`
  and `last` and keeps `settings` and `purchases`.
- `HubTests`: with no save, Paint Sort is featured ("Start here") and the grid is
  [Hex Tile Sort, Car Loop], neither wide, and the count reads "2"; with
  `last = "car-loop"`, Car Loop is featured with "Jump back in" and the grid is
  [Paint Sort, Hex Tile Sort]; adding a fourth, soon fake game makes the grid
  three boards with the last one wide and the count "1 coming soon"; a status of
  "Level 4 · 120 coins" shows in full on the featured board and as "Level 4" on a
  small one; Hex Tile Sort with `best = 12840` shows "Best 12,840".
- `EntitlementTests`: `carloop_starter` sets `noads` and the starter flag and adds
  2,000 coins and 3 of each booster to Car Loop's section even when the Car Loop
  scene is not loaded; restoring it again adds no coins; `noads` makes
  `ShowBanner` and `ShowInterstitial` no-ops (interstitial `done` still runs);
  rewarded ads still work.
- `AudioSynthTests` (all three groups): each recipe renders the expected length
  (± 5 ms), no NaN, each group's loudest clip peaks at −1 dBFS ± 0.05 after
  normalisation, identical bytes on two runs; `cl_music_loop` is exactly 10 s and
  its first and last 100 samples join without a step larger than the largest
  step inside the loop.
- `IconTests`: every id in §7.3 exists in `IconSet.asset` as a 128 × 128 sprite
  with some opaque pixels; `cl_coin` is not single-colour.

**EditMode: Hex Tile Sort**
- `HexBoardTests`: 19 cells in the order of Appendix D; every cell has 2–6
  neighbours, the centre has 6; `TopRunLen` and `TakeTopRun` on `[0,0,1,1]` give
  2 and `[1,1]`, leaving `[0,0]`.
- `MergeChooserTests`: every board in Appendix D gives the listed receiver,
  givers and score, including the tie-break and the `lastPlaced` bonus.
- `StackFactoryTests`: with a recording `IRandom`, `PickColour` on an empty board
  makes no 0.62 draw; `StackHeight` returns 1/2/3/4 at the thresholds .30/.70/.95
  (early) and .22/.58/.88 (after 18 clears); `GenStack` never puts two runs of
  the same colour next to each other unless the reroll guard ran out; `SeedBoard`
  places 6 stacks of 1–3 tiles of one colour, with no two neighbours sharing a
  top colour (seeds 1–200).
- `TierTests`: clears 0 → 4 colours, 6 → 4, 7 → 5, 20 → 6, 21 → 7, 100 → 7;
  `Into(10, 5) = 3/7`; `Into(30, 7) = 1`.
- `ScoreTests`: pop of 10 at combo 1 = 100; 13 at combo 3 = 480; 10 at chain 14
  uses combo 10 = 1000.

**EditMode: Car Loop**
- `CarLoopGeometryTests`: Appendix C.2 for every shape (loop length, sampled
  length and count, feeder `sm`, `Le`, `fx`, `Sy`, danger intervals, centre)
  within 1e-3; `CircDist` is symmetric; `PoseAt(s)` equals `PoseAt(s + L)` on
  the loop.
- `CarLoopLevelTests`: Appendix C.1 RNG values exactly; Appendix C.3 traffic
  positions within 1e-3; Appendix C.4 rows: shape, dir, pattern, hard, dual,
  pulse, speed, feeders and seed exactly; traffic, player, time and att exactly
  (a failure prints the row; see §35.6).
- `CarLoopBakeTests`: the shipped JSON has levels 1–300 in order, all fields
  valid (§35.5), and its rows for the levels in Appendix C.4 equal the appendix.
- `CarLoopEconomyTests`: payout examples: level 1 with 3 stars and no bonus = 39;
  level 10 (hard) with 2 stars and a Rare car = 105; level 100 (hard) with 3
  stars = 450; stars from 40% / 15% time left; the daily-reward day sequence
  (consecutive days 1→7→1, a missed day resets to 1); the interstitial gate
  (level ≥ 4, every 2nd clear, every 3rd retry, 45 s, 30 s after a rewarded).
- `CarLoopSimTests`: on level 2, releasing when `SafeAt` is false crashes within
  the merge, and releasing when it is true never crashes (2,000 random release
  times); `GreedySolve` and `RefSolve` on levels 1–10 report `Ok`.

**PlayMode: app**
- Hub: tapping each board loads its scene; coming back makes that game the
  featured board with the label "Jump back in".
- Settings: toggling Sound off mutes all three games' sounds; Music off stops
  Car Loop's loop; theme changes restyle the Hub and Paint Sort live.

**PlayMode: Hex Tile Sort** (seeded run)
- Place a stack next to a matching one: the flip finishes within
  `250 + last start + 100` ms, the receiver's data equals the board fixture, and
  the badge shows the new run.
- Feed a primed stack inside its 500 ms window: it receives, its window restarts,
  and the pop scores the larger run with the bonus.
- Fill the board: "Board full" appears only once nothing is primed, dropping or
  refilling; the best score is saved; "Play again" starts a seeded new run.
- Rotate during a resolve is ignored; rotate when idle turns the board 60° in
  360 ms and keeps every stack on its cell.

**PlayMode: Car Loop**
- Level 1 played by a script (release every 0.6 s): win, complete panel, 3
  stars, the payout matches `CarLoopEconomyTests`, level 2 unlocked, saved.
- Level 2 crash by releasing at a red light: crash effects, fail panel after
  1.15 s; coin revive (150) → state `ready`, wrecks gone, the crashed player car
  is first in the queue; the countdown pauses while the "Not enough coins" panel
  is open.
- Boosters: Slow-Mo makes the clock fall at about 0.42× (± 5%) while active;
  Tow removes the tapped traffic car and costs one only when a car is towed;
  Autopilot releases an armed car on the first safe frame.
- Mock ads: with *No ad fill* the revive ad returns `false` and nothing changes;
  a completed rewarded view of `level_multiplier` pays base × the needle value.

---

## 47. Milestones and acceptance checks

Build in this order (§1). Each row's checks must pass before the next starts.

| # | Milestone | Done when |
| --- | --- | --- |
| P0 | Foundation: project setup (§2), asmdefs, `Playbox.Common`, Core services (save, settings, theme, `SfxPlayer`, `MusicPlayer`, haptics, mock ads, mock store, log analytics), generators (`Raster`, `RasterCanvas`, `SvgIcon`, `Synth`), the icon set, the Hub with all three boards and navigation into placeholder game scenes | Save, Hub, Entitlement, Icon tests pass; the three boards match §5 in both themes (featured board, grid, chips, board art); Back from each placeholder scene returns to the Hub |
| PS1 | Paint Sort engine port and probe CLI | EngineParity, Curve, Solvability and Sawtooth tests pass; the CLI output equals Appendix B.2 |
| PS2 | Paint Sort textures and audio | Appendix A Paint Sort PNGs and §18.2 WAVs regenerate byte-identically; AudioSynth tests pass for the `sfx_*` group; audition every sound |
| PS3 | Static board: layout, vial meshes, liquid shader, symbols, cork | Levels 1, 13, 20 and 60 render in light and dark themes; hidden layers show hatched primer with '?'; side by side with web screenshots, paint colours match and the glass alphas have been tuned for Linear colour space (§2) |
| PS4 | Input, pour animation, stream, particles, glug sounds, haptics | Paint stays level while tipping; stream lands on the rising surface; pitch rises as the target fills; concurrent pours work |
| PS5 | Level flow: corking, the easel painting (§17.7), win sequence, save and resume | Win flow, Resume and Easel PlayMode tests pass; paintings match the web for levels 1, 5 and 20 |
| PS6 | Boosters, buy sheet, dead-end watcher, hint, tutorial, hard intro, hidden-paint tip | Stuck bar appears on a proven dead end within ~0.5 s; hints never spent on dead boards |
| PS7 | Lobby, level road, settings sheet, theme switching, erase progress, performance | Road matches §19.3; Auto theme follows the OS; 60 fps on a mid-range Android with 15 vials; generation never blocks the main thread; probe run for levels 1–120 recorded |
| HX1 | Hex Tile Sort engine and a headless resolver | HexBoard, MergeChooser, StackFactory, Tier and Score tests pass; a seeded headless run (instant tweens) plays 200 random placements without exceptions |
| HX2 | 3D board: meshes, `HexTile`/`HexSocket` shaders, camera fit, backdrop, stacks, badges, rotation | Side by side with web screenshots at 390 × 844 and 360 × 640: board size and position within 4 dp, tile colours, rims, gloss and side walls match after Linear tuning; the board turns ±60° cleanly |
| HX3 | Input, place, drop, flips, pops, primed timing, tray refill, particles, floats, banner, shake | Hex PlayMode tests pass; a flip lands exactly on the stack top; placing during a chain keeps the chain (combo grows) |
| HX4 | HUD, game-over veil, sounds, haptics, best score, board status | The `hex_*` group passes AudioSynth tests; best score persists across app restarts and shows on the Hub board |
| CL1 | Car Loop engine: geometry, generator, bots, simulation; baked JSON and `CarLoopBake` | CarLoopGeometry, CarLoopLevel, CarLoopBake and CarLoopSim tests pass; the bake report lists no differences (or each is explained) |
| CL2 | Rendering: car sprites, static layer, camera fit, cars moving, attract mode | Levels 1, 8, 16 and 75 match web screenshots (road, island, trees, lamps, markings, cars); the demo ring runs on the Car Loop home |
| CL3 | Gameplay: tap, collisions, clock, win/lose, effects, HUD, intro, tutorial and tips, sounds and music, haptics | Level 1 and crash PlayMode tests pass; the clock stays frozen until the first tap; close calls pay +3 |
| CL4 | Boosters, complete and fail panels, revive, after-level chain, garage, daily reward, levels screen, shop | Booster and Economy tests pass; every panel in §43.3 opens from its trigger and matches the web prototype |
| CL5 | Ads and store: banner slot, interstitial gate, every rewarded placement, Remove Ads across the app, purchases and restore, analytics events | Mock-ads PlayMode tests pass; with the real SDKs and the network's test ids, a rewarded, an interstitial and a banner show on a device, and a sandbox purchase of each product grants correctly |
| R1 | Release pass | All tests green; 60 fps in all three games on a mid-range Android and an older iPhone; no main-thread hitch over 50 ms; consent and ATT flows verified; store assets and legal links in place |

---

## 48. Appendix A: generated asset manifest

All PNGs are RGBA, straight alpha, written to
`Assets/_Project/Textures/Generated/`.

| File | Size | Import | Contents |
| --- | --- | --- | --- |
| `tex_cork.png` | 256×192 | Sprite, pivot top-centre, PPU so it is 1 unit wide | Rounded rect (radius 38) filling the image; horizontal gradient #DDAE78 → #C68D57 (45%) → #94623A; highlight band x 19..237, y 16..48 from the top, radius 16, rgba(255,236,200,.45); five pores radius 8, rgba(90,50,20,.35), centres (px from left, px from top) = (64,96), (166,70), (198,134), (112,144), (51,160) |
| `tex_frame_light.png` / `tex_frame_dark.png` | 64×64 | Sprite, 9-slice border 16, Clamp | Rounded rect radius 10; linear gradient at 145° from ps-frame to ps-frame-2 (§6.1); 2 px highlight along the top edge rgba(255,255,255,.25); horizontal grain: 40 seeded 1-px streaks of random length, alpha .05, light and dark alternating |
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
| `ui_lock.png` | 64×64 | Sprite | White padlock on a 24-unit grid scaled by 64/24: body rounded rect (5,11)–(19,21) radius 2.5; shackle stroke 2.4 with round caps from (8,11) up to (8,8), a half circle of radius 4 centred (12,8) over the top, down to (16,11) |
| `ui_play.png` | 64×64 | Sprite | White play triangle on the same grid: corners (8,5.5), (8,18.5), (19.9,12), each rounded with radius 1 |
| `tex_board_hex_tile_sort.png` | 1600×1000 | Sprite, Clamp, sRGB, no mipmaps | Hex Tile Sort's board art, exactly as specified in §5 |
| `tex_board_car_loop.png` | 1600×1000 | Sprite, Clamp, sRGB, no mipmaps | Car Loop's board art, exactly as specified in §5 |
| `ui_ring_3.png` | 64×64 | Sprite | White ring, outer radius 31, width 3 (booster progress rings with Image *Filled Radial 360*, the tap ring under the coach hand) |
| `ui_gloss.png` | 64×32 | Sprite, 9-slice border 14 | Car Loop button gloss: white α .34 at the top to 0 at the bottom, top corners radius 14, bottom corners radius 22 |
| `tex_hex_backdrop.png` | 512×1024 | Default, Clamp, sRGB | `RasterCanvas` port of Hex Tile Sort's page background: linear `#150C36` → `#0B0722` top to bottom; over it a radial ellipse (120% × 80% of the size) centred at (50%, −10%): `#3A1B6E` → transparent at 60%; and a radial ellipse (90% × 60%) centred at (50%, 108%): `#2B1160` → transparent at 62% |
| `fx_hex_blob.png` | 128×64 | Sprite | White ellipse filling the image, alpha `exp(−(d/0.6)²)` with `d` the normalised elliptical distance (contact shadows, pedestals) |
| `fx_rect.png` | 8×8 | Sprite | White square (Hex Tile Sort chips, Car Loop debris and confetti, scaled per particle) |
| `car_<id>.png`, `car_<id>_burnt.png` | 272×192 each, 24 files | Sprite, PPU 8, pivot centre, sRGB | §42 |
| `car_traffic_<hex>.png`, `car_traffic_<hex>_burnt.png` | 272×192 each, 22 files | same | §42 (sedan in each of the 11 traffic colours) |
| `car_shadow.png` | 272×192 | Sprite, PPU 8 | §42 |
| `car_beam.png` | 240×144 | Sprite, PPU 4, pivot (0, 0.5) | §42 |
| `cl_tree_a.png`, `cl_tree_b.png` | 128×128 | Sprite | Canopy disc r 60 px in `#123A33` / `#173F2E`; inner disc at (−.25r, −.3r) radius .62r in `#1B5246` / `#22573C`; highlight disc at (−.35r, −.45r) radius .3r in `rgba(160,255,200,.08)` (offsets y-down) |
| `fx_soft_disc.png` | 64×64 | Sprite | White disc r 30 with a 3 px soft edge (smoke, puffs) |
| `fx_fire.png` | 128×128 | Sprite | Radial: `rgba(255,220,120,.9)` at 0, `rgba(255,110,40,.6)` at .5, `rgba(255,60,20,0)` at 1 (alpha multiplied per particle) |
| `fx_streak.png` | 64×8 | Sprite | White capsule (sparks, stretched along the velocity) |
| `cl_turntable.png` | 512×200 | Sprite | Garage platform: shadow ellipse offset 7 px down (black α .35), ellipse filled radial `#34477A` → `#1A2647`, inner ring at 80% `rgba(160,190,255,.35)` 1.5 px |
| `cl_ellipse_mask.png` | 512×176 | Sprite | White ellipse (mask for the turntable's light sweep) |
| `cl_light_sweep.png` | 128×16 | Sprite | Horizontal white gradient α 0 → .12 → 0 |
| `cl_rays.png` | 256×256 | Sprite | Rays from the centre, 10° on and 14° off, white, alpha fading radially from 40% of the radius to 0 at the edge (rotating behind big panel icons) |
| Icons (`IconSet.asset`) | 128×128 each | Sprite | Every id in §7.3 (app, Paint Sort, Hex Tile Sort, the 33 Car Loop symbols and `cl_sign` at 256×256) |

Runtime-generated (not files): Paint Sort's vial meshes (§13.2), paint stream
ribbons (§15), hint pointer meshes (§16), painting meshes and RenderTextures
(§17), level road geometry (§19.3) and board-art RenderTexture (§5); board
slabs and chips (uGUI, §5); backdrop gradients (§6.1); Hex Tile Sort's prisms,
sockets and outline ribbons (§26.1); Car Loop's roads, island, speckles,
markings, danger-zone ribbons and signals (§41.2), tow cables and reticles
(§41.3).

Audio files: §18.2 (Paint Sort), §30.2 (Hex Tile Sort), §44.3 (Car Loop).

---

## 49. Appendix B: Paint Sort golden fixtures

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

---

## 50. Appendix C: Car Loop golden fixtures

Produced by the web engine (`roundabout/src/app.html`) with the Node approach in
§0.5. Values rounded to 4 decimals. Tolerances in §46.

### C.1 RNG

```
Mulberry32(42) first 3:              0.601103751920, 0.448290558998, 0.852465793490
Mulberry32(11*7919+17) first 3:      0.037866758648, 0.489187327912, 0.046240237774
```

### C.2 Tracks (dir 1, one feeder at tx 0)

`loopLen` is `LoopLength(shape)` (unsampled polyline); `L` and `cnt` are the
resampled loop; `sm`, `Le`, `fx`, `Sy` describe the feeder; `danger` is its
interval list; `centre` is the mean of the loop samples.

```
 circle     loopLen 703.6996 sampled L 703.6996 cnt 704 feeder sm 175.9249 Le 64.5543 fx 36 Sy 156 danger [[-22,22]] centre 0 0
 bigCircle  loopLen 816.7942 sampled L 816.7942 cnt 817 feeder sm 203.9486 Le 64.5722 fx 36.2498 Sy 173.997 danger [[-22,22]] centre 0 0
 squircle   loopLen 785.0048 sampled L 785.0048 cnt 785 feeder sm 527.0032 Le 64.5543 fx 35.7504 Sy 152 danger [[-22,22]] centre -0 0
 roundRect  loopLen 891.3022 sampled L 891.3022 cnt 891 feeder sm 608.2062 Le 64.5543 fx 36.2704 Sy 144 danger [[-22,22]] centre 0 0
 stadiumV   loopLen 734.7792 sampled L 734.7792 cnt 735 feeder sm 492.8519 Le 64.5656 fx 36.1524 Sy 181.9991 danger [[-22,22]] centre -0.0002 0.0001
 stadiumH   loopLen 782.7792 sampled L 782.7792 cnt 783 feeder sm 586.8344 Le 64.5543 fx 36.1699 Sy 124 danger [[-22,22]] centre -0.0002 0.0001
 tall       loopLen 892.437 sampled L 892.437 cnt 892 feeder sm 563.2758 Le 64.5543 fx 36.0519 Sy 194 danger [[-22,22]] centre 0 0
 tri        loopLen 606.8035 sampled L 606.8035 cnt 607 feeder sm 346.8877 Le 64.5543 fx 36.4928 Sy 119 danger [[-22,22]] centre 0 0
 hex        loopLen 748.6158 sampled L 748.6158 cnt 749 feeder sm 202.8959 Le 64.5543 fx 35.9632 Sy 154.8512 danger [[-22,22]] centre -0 -0.0002
 pent       loopLen 730.6956 sampled L 730.6956 cnt 731 feeder sm 386.8389 Le 64.5543 fx 35.8689 Sy 149.1722 danger [[-22,22]] centre 0 -0
```

### C.3 Traffic positions (`TrafficPositions(RawDef(n), L)`)

```
 level 3   pairs   [667.5543,697.5543,1034.9438,1064.9438]
 level 5   trains  [271.9073,301.9073,331.9073,623.7571,653.7571]
 level 9   random  [437.183,260.6711,296.1574,695.6295,488.8046,209.1614]
 level 37  trains  [612.1788,642.1788,672.1788,1058.3973,1088.3973,1118.3973]
```

### C.4 Level definitions (`LevelDef(n)`)

`att` is the validation attempt that passed (0 = the raw definition); `refT`
and `greedyT` are the reference and greedy bots' finishing times in seconds.
Levels 1–300 needed at most 4 attempts (167 levels: 0, 52: 1, 36: 2, 27: 3,
18: 4); clocks range from 9 to 34 s; 58 hard, 57 two-entrance, 72 rush-hour and
120 counter-clockwise levels.

```
 lvl  shape      dir pattern  hard dual pulse(amp,period)  speed traffic player feeders     seed      time att refT     greedyT
   1   circle       1   even        0     0   -                   120       0      5    [0]           104736     30    0   8.1      1.8167
   2   squircle     1   even        0     0   -                   125       2      4    [0]           209465     13    0   4.7      1.6833
   3   stadiumV     1   pairs       0     0   -                   130       4      4    [0]           314194     14    0   5.1667   1.8
   4   squircle     1   random      0     0   -                   134       4      5    [-30]         418923     15    0   6.05     1.9
   5   circle       1   trains      0     0   -                   137       5      5    [0]           523652     17    0   7.0667   1.6
   6   stadiumH     1   even        0     0   -                   140       4      6    [0]           628381     15    1   6.5333   1.9333
   7   tri          1   random      0     0   -                   142       2      6    [0]           733110     15    3   6.1333   2.0667
   8   circle      -1   pairs       0     0   -                   145       6      6    [0]           837839     16    0   6.6833   2.7
   9   hex          1   random      0     0   -                   148       6      6    [0]           942568     15    0   6.6      2.0167
  10   squircle     1   pairs       1     0   -                   152       6      7    [0]          1047297     17    1   7.8167   2.3833
  11   circle       1   even        0     0   -                   149       5      5    [0]          1152026     11    0   4.3167   1.9333
  12   tall        -1   random      0     0   -                   150       6      5    [30]         1256755     12    0   5.0167   1.95
  15   squircle     1   random      0     0   (0.162, 3.6563)     140       5      5    [0]          1570942     13    0   5.7333   1.4833
  16   roundRect    1   random      0     1   -                   153       6      7    [-75,75]     1675671     33    0   14.25    1.8
  20   hex          1   random      1     0   -                   162       3      7    [0]          2094587     17    2   8.0833   2.05
  21   roundRect   -1   even        0     1   -                   156       6      6    [-75,75]     2199316     15    0   6.1667   1.1
  25   circle      -1   pairs       1     0   -                   165       5      6    [0]          2618232     12    0   5.7833   1.8667
  30   roundRect   -1   even        1     0   -                   169       4      7    [0]          3141877     14    2   6.7667   2.2667
  37   tall         1   trains      0     0   -                   168       6      7    [0]          3874980     17    0   8.45     1.7833
  50   squircle     1   random      1     0   -                   184       7      6    [0]          5236457     13    0   6.9      2.3
  60   squircle     1   even        1     0   -                   191       7      6    [0]          6283747     11    0   5.7167   1.8667
  61   roundRect   -1   trains      0     1   -                   181       8      7    [-75,75]     6388476     16    0   8.2      1.3167
  75   tri          1   random      1     0   (0.27, 3.9208)      179       5      5    [0]          7854682      9    0   4.65     1.4333
 100   tri          1   trains      1     0   -                   192       6      5    [30]        10472907      9    0   4.8333   1.3333
 150   hex          1   even        1     0   -                   200       3      7    [30]        15709357     12    3   5.7833   1.65
 300   circle       1   even        1     0   -                   200       6      6    [30]        31418707     12    0   6.8667   1.9333
```

---

## 51. Appendix D: Hex Tile Sort fixtures

Produced by running the web's `scoreMerge` and `bestMerge` on constructed
boards (§0.5). Stacks are listed bottom to top; colours are indices into
`HexConfig.Faces` (0 coral, 1 amber, 2 lime, 3 cyan, 4 violet); every cell not
listed is empty; nothing is primed or dropping unless marked.

**Cell order** (`HexBoard.Cells`):

```
(-2,0) (-2,1) (-2,2) (-1,-1) (-1,0) (-1,1) (-1,2) (0,-2) (0,-1) (0,0) (0,1) (0,2) (1,-2) (1,-1) (1,0) (1,1) (2,-2) (2,-1) (2,0)
```

**Board A:** `(0,0) [0,0,1,1]`, `(1,0) [2,1,1,1]`, `(0,1) [1]`, `(1,-1) [2,2]`,
`(-1,0) [3,3,3,3,3,3,3,3]`, `(-1,1) [3,3]`.

| Case | Receiver | Givers | Score |
| --- | --- | --- | --- |
| A, `lastPlaced = null` | (-1,0) | [(-1,1)] | 1530 (a tie with (-1,1) as receiver; the earlier cell wins) |
| A, `lastPlaced = (-1,1)` | (-1,1) | [(-1,0)] | 1540 (the +10 breaks the tie) |
| A without the two colour-3 stacks | (0,0) | [(1,0), (0,1)] | 316 |

Candidate scores on "A without colour 3", for `ScoreMerge` tests:

| Receiver | Givers | Score | Why |
| --- | --- | --- | --- |
| (0,0) | [(1,0), (0,1)] | 316 | total run 6 → 132; (1,0) exposes lime next to (1,-1)'s lime run of 2 → +114; (0,1) empties → +70 |
| (1,0) | [(0,0), (0,1)] | 202 | |
| (0,1) | [(1,0), (0,0)] | 246 | |

**Board B (primed receiver):** `(0,0) [4 ×10]` primed, `(1,0) [4,4]`,
`(0,-1) [1,4]` → receiver (0,0), givers [(1,0), (0,-1)], score 1848 (total 13 →
1478; primed +300; (1,0) empties +70).

**Pop scores:** run 10 at combo 1 → 100; run 13 at combo 3 → 480; run 10 with
chain 14 → combo 10 → 1000.
