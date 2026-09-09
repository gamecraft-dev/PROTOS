# Neon Cannon — Art Asset Requirements for the Unity Port

What you need to source or commission to rebuild `neon-cannon/index.html` in Unity —
and, just as importantly, what you do **not** need, because it can be generated inside
Unity with a shader, a mesh or a built-in effect.

**Scope:** the browser prototype is the reference for **gameplay and art style only**.
The Unity build ships on Google Play as a complete product, so music, sound, haptics,
pause, restart, quit and the store listing are all in scope (§3).

**The short version:** the HTML build contains **zero image files**. Every pixel is
drawn procedurally on a canvas at runtime, so almost none of it needs an artist.

- **Matching the prototype's gameplay and art** costs **two free typefaces**
  (§1.1–1.2) and nothing else. No paid plugin anywhere, the paint effect included
  (§2.5). Every screen it has is text, rounded rectangles and circles (§3.1).
- **Shipping it on Google Play** adds four things the prototype has none of: a
  **free icon font** (§3.3), **audio** — 13 SFX and 2 music loops, the largest single
  procurement in the project (§3.4), **haptics** (§3.5), and the **store listing
  graphics** Google requires before it will accept an upload (§3.6).
- Everything else is a generated texture you can author in ten minutes, or a shader.

---

## 1. Must be sourced externally

These cannot be generated from nothing and are hard requirements.

### 1.1 Typefaces — the only real art dependency

| Font | Role | Source | Licence |
|---|---|---|---|
| **Monoton** | Wave banner, wave-clear banner, `WAVE n CLEARED` panel, logo, `CRUSHED` — see §1.2 | Google Fonts | SIL Open Font License 1.1 |
| **Chakra Petch** | All HUD, orb numbers, console, panels, body text. Weights 400 / 600 / 700 | Google Fonts | SIL Open Font License 1.1 |

Both are free for commercial use and redistributable under the OFL, including
embedding in a game build. Keep a copy of `OFL.txt` alongside them in
`Assets/NeonCannon/Fonts/`.

Monoton is not a generic display face — it is a single-weight face whose glyphs are
drawn as concentric parallel strokes, so they read as bent glass tubing rather than as
text with a glow on it. That is why the title looks like a sign rather than a sci-fi
logo, and no substitution keeps it (§1.2). Chakra Petch is the angular technical
counterpart carrying the numerals.

**Chakra Petch is a Thai + Latin family** (Cadson Demak). Opening the `.ttf` shows
Thai glyphs, which is expected and harmless — its Latin coverage is complete, and the
character-set setting below excludes the Thai entirely. Measured from the shipping
font files:

| | Chakra Petch | Monoton |
|---|---|---|
| Glyphs mapped | 725 | 371 |
| Thai glyphs | **87** — subset them away | 0 |
| Latin basic / Latin-1 / ext-A | 95 / 95 / 127 | 95 / 94 / 119 |
| `×` U+00D7 and `·` U+00B7 | both present | both present |
| Units per em | 1000 | 2048 |
| OpenType features | `aalt ccmp frac kern liga locl mark mkmk ordn subs sups` | `kern` |

**Font Asset Creator settings**

| Setting | Monoton | Chakra Petch (Regular **and** Bold) |
|---|---|---|
| Sampling Point Size | Auto Sizing | Auto Sizing |
| Padding | 9 | 9 |
| Packing Method | Optimum | Optimum |
| Atlas Resolution | 1024 × 1024 (512² also fits) | 1024 × 1024 |
| **Character Set** | **Custom Characters:** `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789` + space | **Extended ASCII** |
| Render Mode | **SDFAA** | **SDFAA** |
| Get Kerning Pairs | On | On |
| Atlas Population Mode | Static (set after generating) | Static |

**Extended ASCII is the setting that matters for Chakra Petch.** It covers ASCII plus
Latin-1, which includes both `×` and `·`, and stops well short of U+0E00 — so none of
the 87 Thai glyphs enter the atlas. Never generate this font with Unicode Range over
the whole face.

Monoton needs only letters, digits and space: it renders the logo, `Wave n`, `Clear`,
`CRUSHED` and `WAVE n CLEARED`, and nothing else in the game uses it.

Two weights of Chakra Petch are enough. The browser build uses 400, 600 and 700, but
600 appears in exactly two places (upgrade prices, damage floaters) — map it to 700
and nobody will see the difference.

After generating, check the reported Sampling Point Size. Below ~40 the atlas is
overcrowded: raise it to 2048² or drop Chakra Petch to plain ASCII.

**Numerals are not tabular, and there is no font feature that makes them so.**
Measured digit advances (units per 1000 em):

| Font | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| Chakra Petch Regular | 628 | **358** | 550 | 579 | 555 | 582 | 598 | 498 | 614 | 603 |
| Chakra Petch Bold | 652 | **382** | 574 | 603 | 579 | 606 | 622 | 522 | 638 | 627 |

A `1` is roughly 40% narrower than a `0`, so a counter visibly shifts as its digits
change. The font exposes **no `tnum` feature**, so this cannot be fixed in the Font
Features panel — an earlier draft of this document said it could, and that was wrong.

Fix it in TextMeshPro instead, with the monospacing tag on counters that change while
being read:

```
<mspace=0.66em>1234</mspace>
```

`0.66em` clears the widest digit in Bold (0.652em); use it for both weights. Apply it
to the scrap counter and the wave number. It is **not** needed for orb HP numbers —
those are centred on a moving orb, where the shift is invisible — nor for prices,
which only change on purchase.

Monoton's digits are non-tabular too, by a wider margin, but it only ever renders
briefly-shown centred banners, so it needs no treatment.

**Unity import steps**

| Step | Detail |
|---|---|
| Import | Drop the `.ttf` into `Assets/NeonCannon/Fonts/` |
| Convert | Window → TextMeshPro → Font Asset Creator |
| Material | HDR face colour, intensity ~2.2. No Outline, no Underlay — bloom does the glow |
| Fallback | Assign a system font fallback so a missing glyph never renders as a box |

**If you would rather not deal with `<mspace>` at all**, the only Google font I checked
that is genuinely tabular out of the box is **Titillium Web** (all ten digits at 560,
Latin-only, 396 glyphs). It is a plainer, more corporate face and loses the angular
technical character Chakra Petch gives the HUD, which is why it is not the pick — but
it is a valid swap and needs no per-field tags.

### 1.2 The arcade banner lettering — this is Monoton, and no PNGs are needed

The wave announcement (`Wave 2` / `Incoming`), the wave-clear announcement
(`Clear` / `+46 scrap`), the `NEON CANNON` logo and the `CRUSHED` game-over
headline all share one typeface, and it is the single strongest identity element in
the game.

| | |
|---|---|
| **Font** | **Monoton**, regular 400 — the only weight it has |
| **Where** | Wave banner title, wave-clear banner title, start logo, game-over headline |
| **Source** | Google Fonts · SIL Open Font License 1.1 · free to embed in a build |
| **PNGs required?** | **No.** See below |

**Why it looks like that.** Monoton is not a generic sci-fi display face — each glyph
is drawn as a set of *concentric parallel strokes*, which is what makes it read as a
bent glass neon tube rather than as text with a glow filter. That multi-stroke
construction is the arcade quality; it comes from the typeface itself, not from the
CSS. Substituting any other display face loses it, and the effect cannot be recovered
by adding more bloom.

**No PNGs are required, and using them would be worse.** The banner text is dynamic —
it interpolates the wave number, and the wave count is unbounded — so a pre-rendered
sprite per banner is not even possible without an atlas of digits. Render it as live
text:

| Step | Setting |
|---|---|
| TMP Font Asset | Monoton `.ttf` → Font Asset Creator, **SDF**, 1024², padding 9 |
| Characters | `0-9 A-Z a-z + space` is enough for every string that uses this face |
| Material | TMP SDF shader, **HDR** face colour at intensity ~2.2, URP Bloom does the halo |
| Do **not** add | Outline, underlay, or a bevel — the tube strokes are the letterform. Extra outline fills the gaps between them and turns the glyph into a solid blob |

A PNG would only become necessary if you **replaced Monoton with hand-lettered
artwork** — a custom drawn wordmark for the logo, say. Even then, keep the two
*banners* as live text, because of the interpolated wave number. Budget for that only
if someone specifically wants a bespoke logo; the shipped design does not need it.

**One porting note that does not apply to Unity.** In the browser build this face is
inlined into the page as a base64 woff2 rather than linked from the CDN. The reason:
the wave banner is on screen for 1.7 s, which is shorter than a cold font fetch, so
with a normal `font-display: swap` link the banner rendered in the *fallback* serif
for exactly the moments that matter, and only looked right once the font was cached.
Unity has no equivalent failure — the TMP font asset is compiled into the build and is
present at frame zero. Nothing to guard against; noted only so the inlining in the
HTML source does not look like an arbitrary choice.

### 1.3 Application icon and store graphics

The HTML uses an emoji favicon, which does not port. The shipped build needs a real
icon plus the Play Store listing graphics — **specced in §3.6**, since Google's
requirements (adaptive layers, safe zones, the feature graphic) are more particular
than "draw an icon".

This is the project's only genuinely commissioned artwork. The obvious subject is the
cannon silhouette in cyan on the `#07030f` ground, with paint splatter behind it for
the feature graphic.

---

## 2. Generate in Unity — no artist needed

Every item below exists in the HTML build only as canvas drawing code. Each maps onto
a Unity technique. **None of these require a sourced asset** — they are shader and
tooling work, not art production.

### 2.1 Orbs

| Element | Technique |
|---|---|
| Neon ring | Shader Graph on a quad: SDF circle, `abs(length(uv - 0.5) - r) - width`, smoothstepped. Resolution-independent, and ring width is a shader property so all five tiers share one material. |
| Interior fill | Radial gradient in the same shader, alpha driven by a `_Flash` property |
| Health arc | Same shader with a polar-angle mask: `atan2` on the UV, compared to a `_Fill` property (0..1). One extra node, no second object. |
| Ground pool / shadow | Additive quad with a radial falloff, scaled and tinted per frame |
| Number | TextMeshPro child, world-space |

Five tiers differ only in `_Hue`, `_Radius` and ring width — a single material with a
`MaterialPropertyBlock` per orb avoids five materials and keeps batching intact.

### 2.2 Cannon

| Element | Technique |
|---|---|
| Wheels | `LineRenderer` circle, or a generated `Mesh` ring; three chords as additional line segments. Rotates with the `spin` value. |
| Chassis trapezoid | Generated `Mesh` (4 verts) with an unlit additive material, plus a `LineRenderer` outline |
| Barrel | Rounded-rect quad, same material |
| Muzzle flash | Additive quad with the shared radial-glow shader, scaled by `recoil` |
| Shield arc | Arc `LineRenderer` spanning 194°–345°, violet, alpha pulsing |

All of it is neon outline work — line renderers and generated meshes are a closer
match to the source than sprites would be, and they stay crisp at any resolution.

### 2.3 Backdrop and ground

| Element | Technique |
|---|---|
| Vertical gradient | Full-screen quad, 3-stop gradient in a shader |
| Receding grid | Shader Graph, or 26 `LineRenderer`s. The shader is cheaper: compute the horizontal rules as `frac()` bands in a squared UV, and the verticals as a radial fan from a vanishing point. |
| Ground line + glow | Quad with an emissive band; bloom does the halo |
| Scrolling dashes | Same quad, UV offset scrolled at 0.34 u/s, dash pattern from `step(frac(u * n), 0.4)` |

### 2.4 Bullets, particles, floaters

| Element | Technique |
|---|---|
| Bullet | Two stacked capsule quads (wide translucent cyan + narrow white core), or a `TrailRenderer` with a 0.013 s time. Additive blend. |
| Explosion / impact shards | One `ParticleSystem` in additive mode with `Emit(EmitParams)` for bursts. Stretched Billboard render mode gives the streak-along-velocity look for free. |
| Damage numbers | Pooled TextMeshPro, world-space, rising and fading |
| Scrap streaks | Pooled TextMeshPro following a smoothstep path to the HUD counter |

The particle system needs a particle texture — see §3.1, or use Unity's built-in
`Default-Particle`.

### 2.5 Paint splatter — zero textures, zero plugins

**The HTML paint effect is the approved target, and reproducing it exactly needs no
art assets and no Asset Store packages at all.** Every shape in it is an ellipse:

| What you see | What the HTML actually draws |
|---|---|
| Flying droplet | One ellipse stretched along velocity + one smaller lighter ellipse offset up-left as a wet highlight |
| Ground pool | One squashed ellipse + a brighter core ellipse + 3 randomly thrown satellite ellipses |
| Splat on the cannon | One ellipse + one highlight ellipse, clipped to the cannon outline |
| Drip | One tall narrow ellipse |

Irregularity comes from **randomised size, rotation, offset and satellite placement
per stamp**, not from an authored silhouette. So one small Shader Graph — an SDF
ellipse with a second offset ellipse as a highlight mask, tinted per instance — serves
every paint element in the game.

| # | Asset | Needed for 1:1? | Notes |
|---|---|---|---|
| P1 | Ellipse + highlight SDF shader | **Yes** | ~10 nodes. Replaces all paint textures |
| P2 | Droplet sprite (64², Alpha8) | Optional | Only if you would rather ship a texture than a shader. A plain filled ellipse, **not** a soft glow — Unity's `Default-Particle` is too soft and will not match |
| P3 | Hand-drawn splat masks ×6–8 | **No** | Would look *different from*, not closer to, the approved effect |
| P4 | Splat normal map | **No** | Only for the "wetter than HTML" upgrade in §17.9.3 of the port spec |

> **This reverses an earlier recommendation in this document.** While the target was
> "better than the HTML", authored splat masks were the right call, because
> hand-thrown ink beats stamped ellipses. Now that the HTML effect itself is the
> approved look, masks would move *away* from it. If you later decide you want
> richer splatter than the browser build, P3 and P4 come back — see §17.9.3.

**Colour comes from code, never from a texture**, so if you do use P2 keep it
greyscale: every droplet is tinted at runtime from the orb's hue at 96% saturation /
60% lightness.

**No fluid-simulation package is required.** The HTML runs no fluid simulation of any
kind — droplets are independent ballistic particles. Obi Fluid and Zibra Liquids are
paid Asset Store licences and would be bought to solve a problem this effect does not
have.

### 2.6 Post-processing and screen effects

| Element | Technique |
|---|---|
| **Neon glow** | **URP Bloom** in a Global Volume. This is what sells the entire look — do not try to fake it with sprite halos. |
| Vignette | URP Vignette override |
| Danger flash | Full-screen additive quad, magenta gradient, alpha driven by the threat value |
| Camera shake | Transform offset on the camera; no asset |
| Chromatic aberration | URP override, optional, ~0.05 — the HTML has none, so leave it off for strict parity |

### 2.7 UI chrome

| Element | Technique |
|---|---|
| Rounded panel borders | 9-sliced `Image`, or a rounded-rect SDF shader (preferred — one material serves every corner radius) |
| Console button top rule | 2 px `Image` in the accent colour, emissive |
| Shield pips | Small ring sprite or the same SDF circle shader |
| Slider track / thumb | Unity `Slider` with a custom rounded-rect track and an SDF circle thumb |
| Button glow | Emissive material + bloom, not a pre-blurred sprite |

---

---

## 3. Everything the shipped game needs

The browser prototype is the reference for **gameplay and art style only**. The Unity
build ships on Google Play as a complete product, so music, sound, haptics, pause,
restart and quit are all **in scope and required** — they are not optional extras and
not "parity gaps".

This section is the complete list, split into what the prototype already covers, what
has to be built on top, and what Google Play demands before it will accept an upload.

### 3.1 Surfaces the prototype already has — no art required

| # | Surface | Contents | Assets |
|---|---|---|---|
| S1 | **Start screen** | `NEON CANNON` logo (Monoton), tagline, three how-to lines, Start button, best-run line | **None** |
| S2 | **HUD bar** | Wave number, three shield pips, scrap counter | **None** |
| S3 | **Wave banner** | `Wave n` + subtitle, 1.7 s sweep | **None** |
| S4 | **Wave-clear banner** | `Clear` + `+n scrap` | **None** |
| S5 | **Upgrade console** | Four buttons: Damage / Rate / Barrels / Shield | **None** |
| S6 | **Tuner drawer** | Three labelled sliders + Reset (ship it inside Settings, §3.2) | **None** |
| S7 | **Level failed panel** | `CRUSHED`, three-cell tally, **Rebuild** | **None** |
| S8 | **Level complete panel** | `WAVE n CLEARED`, five stats, upgrade console, **Next Wave** | **None** |

All eight are text, rounded rectangles and circles. One rounded-rect SDF shader and
one circle SDF shader cover every one of them. **Zero PNGs.**

### 3.2 Surfaces the shipped build adds — required

None of these exist in the prototype in any form. Verified by grep: `audio`, `sound`,
`music` and `pause` appear **zero times** in the browser source.

| # | Surface | Contents | Assets |
|---|---|---|---|
| S9 | **Pause button** | Small icon, top-right of the HUD, in-play only | Pause icon (§3.3) |
| S10 | **Pause panel** | Resume · Restart · Settings · Quit, current wave and score | 4 icons |
| S11 | **Settings panel** | Music toggle, SFX toggle, Haptics toggle, Reduced motion toggle, the tuner drawer, Credits, Restore/Reset progress | 5–6 icons |
| S12 | **Quit confirmation** | "Abandon this run?" · Cancel / Quit — the run is lost, so it needs a gate | None |
| S13 | **Boot / loading screen** | Logo + progress while the scene loads, TMP atlases warm and pools prewarm | None |
| S14 | **Restart confirmation** | Only if Restart is reachable mid-run from Pause | None |

Two rules that matter for a Play release:

- **The pause button must be reachable one-handed** and must not sit where a drag to
  move the cannon begins. Top-right of the HUD bar, outside the playfield input area,
  same as the TUNE button it replaces.
- **Pausing must freeze the simulation, not the UI.** Use the `GameState` flag from
  §4 of the port spec, never `Time.timeScale = 0`, or panel tweens and the banner
  animation freeze with it.

### 3.3 Icons — one free icon font, still no PNGs

The shipped controls give the project its first icons. Ten glyphs cover everything:

| Icon | Used by |
|---|---|
| Pause | S9 |
| Play / Resume | S10 |
| Restart / Replay | S10, S7 |
| Home / Quit | S10 |
| Settings gear | S10 |
| Close ✕ | S10, S11 |
| Volume on / Volume off | S11 |
| Music on / Music off | S11 |
| Vibration | S11 |

Pause, Play and Close are trivial geometry. The rest — the circular restart arrow, the
speaker, the gear, the note — are not worth hand-building.

**Source: [Material Symbols](https://fonts.google.com/icons), Outlined weight, Apache
License 2.0.** Free for commercial use and redistribution. Run it through the
TextMeshPro Font Asset Creator exactly like the two text faces (SDF, 1024², padding 9)
and place icons as TMP text.

Doing it as a font rather than sprites means icons inherit **HDR tint, bloom
participation, resolution independence and one consistent stroke weight** from the
type system already in place. A PNG icon set gets none of that and will look bolted on
beside the neon.

Take the **Outlined** weight, not Filled or Rounded. The game's entire visual language
is glowing outline; a solid-filled icon reads as a foreign object in it.

| # | Asset | Format | Source |
|---|---|---|---|
| I1 | Material Symbols Outlined, subset to ~10 glyphs | TMP SDF font asset | Google Fonts, Apache 2.0, free |

### 3.4 Audio — required

The prototype has none, so all of this is new. It is the largest single procurement in
the project.

**Sound effects — 13 cues**

| Cue | Notes |
|---|---|
| Shot | See the voice-limiting warning below — this one will make or break the mix |
| Bullet hits orb | Extremely frequent. Short, quiet, heavily pitch-varied |
| Orb splits | Pitched down by tier |
| Orb destroyed | Pitched by tier; tier 4 wants real weight |
| Orb bounces on ground | Pitched by tier, low volume |
| Paint splat | Wet accent as paint lands |
| Shield absorbs a hit | Must cut through everything else — this is the "you nearly died" cue |
| Upgrade purchased | Short, bright, satisfying; the player will hear it hundreds of times |
| Scrap collected | Optional; risks clutter at high kill rates |
| Wave start | Stinger under the banner |
| Wave clear | Stinger under the Level Complete panel |
| Game over | |
| UI tap | One sound for every button in the game |

**Music — 2 loops:** a menu loop and a gameplay loop. Synthwave / outrun suits the
palette. A second, denser gameplay layer to fade in on later waves is a cheap way to
sell escalation, and is worth speccing now rather than retrofitting.

**Where to get it:** a royalty-free library, not a commission. This is stock-suitable
material. Whatever the source, keep the licence documents in the repo — Google Play
will not ask, but a rights holder might.

**The one hard engineering problem: the shot sound.** At maxed fire rate the game
fires **22 volleys per second across 5 barrels = 110 bullets a second**. Playing a
one-shot per bullet is 110 voices a second and will sound like white noise and blow
the audio budget.

| Fire rate | Approach |
|---|---|
| Low (early game) | One `PlayOneShot` per **volley**, never per bullet, with ±10% pitch jitter |
| Above ~12 volleys/s | Cross-fade to a **looping** firing layer whose pitch and volume track the fire rate, and stop emitting one-shots entirely |

Cap the shot channel at ~6 concurrent voices regardless. This is the single most
common way a game in this genre ends up sounding cheap.

**Unity import settings**

| Content | Source | Load Type | Compression |
|---|---|---|---|
| Music loops | `.ogg` | Streaming | Vorbis, ~70% |
| Short SFX (< 0.3 s) | `.wav` | Decompress On Load | ADPCM |
| Longer SFX | `.wav` | Compressed In Memory | Vorbis |

**Mixer:** one `AudioMixer` with `Master → Music` and `Master → SFX`, exposing
`MusicVolume` and `SfxVolume`. Set them in **decibels**, not linearly:

```csharp
mixer.SetFloat("MusicVolume", on ? Mathf.Log10(Mathf.Max(v, 0.0001f)) * 20f : -80f);
```

A linear 0–1 slider driven straight into volume sounds wrong to the ear and mutes far
too late. `-80 dB` is silence.

### 3.5 Haptics — required

| Event | Strength |
|---|---|
| Bullet hits orb | None — 110/s would be unusable |
| Orb destroyed | Light tick, tier 0–2; medium, tier 3–4 |
| Shield absorbs a hit | Heavy |
| Game over | Heavy, longer |
| Upgrade purchased | Light tick |
| Button press | Light tick |

**Do not use `Handheld.Vibrate()`.** It is a fixed ~500 ms buzz with no control, and
using it per orb kill will make players turn haptics off in the first minute.

Call Android's `VibrationEffect` directly through `AndroidJavaObject` (API 26+,
`createOneShot(ms, amplitude)` for ticks and `createWaveform` for patterns). It is
maybe 40 lines, has no dependency, and gives real amplitude control. Asset Store
haptics packages exist and are fine, but check the current licence yourself — I would
not rely on my knowledge of their pricing.

Always gate on the Settings toggle **and** on device support, and default haptics to
**on** — it is expected on mobile.

### 3.6 Google Play store assets — required before upload

These are art, they are not optional, and they are easy to forget until the day of
submission. Verify current requirements in the Play Console, since Google changes
them.

| # | Asset | Spec | Notes |
|---|---|---|---|
| G1 | **Adaptive app icon** | Foreground + background layers, 108 × 108 dp, with all meaning inside the central 72 × 72 dp safe zone | Android 8+. Launchers mask this to circles, squircles and squares — anything outside the safe zone gets cropped |
| G2 | **Play Console icon** | 512 × 512 PNG, 32-bit with alpha | The store listing icon, separate from G1 |
| G3 | **Feature graphic** | 1024 × 500 PNG or JPEG | Required. Shown at the top of the listing. No text near the edges — it gets cropped in some placements |
| G4 | **Phone screenshots** | Minimum 2, up to 8. 16:9 or 9:16 | Capture from the real build. The paint splatter mid-burst is the strongest frame this game has |
| G5 | **Tablet screenshots** | 7" and 10" sets | Only if you declare tablet support |
| G6 | **Promo video** | YouTube URL | Optional but it lifts conversion in this genre |

Non-art submission requirements, listed so they are not a surprise: a **privacy policy
URL**, the **Data safety** declaration, a content rating questionnaire, and Google's
current **target API level** minimum. None need an artist; all block release.

### 3.7 Decisions this document cannot make for you

| Question | Why it matters here |
|---|---|
| **Ads or IAP?** | Genre standard is a rewarded-ad revive after death and an ad between waves. A revive changes the Level Failed panel (S7) and adds an ad-provider SDK. Decide before building that panel, not after |
| **Localisation?** | The game is almost entirely numbers. English-only is defensible; the only real strings are ~15 labels. Cheap now, expensive to retrofit |
| **Cloud save?** | Only `best wave` and settings persist. Play Games Services save is nice but not needed |

## 4. Small generated textures — author once, no artist

These are textures rather than shaders, but each is a few minutes of work in any image
editor (or a 20-line editor script). Listed so nothing is a surprise mid-build.

| # | Asset | Size | Format | Used by |
|---|---|---|---|---|
| 1 | Radial glow | 256 × 256 | Alpha8 / R8, mip-mapped | Muzzle flash, orb ground pools, scrap glow, generic bloom seeds |
| 2 | Particle shard | 32 × 64 | Alpha8 | The additive particle system (or use Unity's `Default-Particle`) |
| 3 | Soft-edged circle | 128 × 128 | Alpha8 | Shield pips, slider thumb, any non-shader circle |
| 4 | Scanline strip | 4 × 4 | RGBA32, **Point filter, Repeat wrap** | CRT overlay. 1 row at ~20% black, 3 rows clear. Point filtering is essential — bilinear turns the lines into grey mush. |
| 5 | 9-slice panel frame | 48 × 48 | RGBA32, border 16 | Console buttons, panels, tuner drawer — only if you skip the SDF shader |
| 6 | 1 × 1 white | 1 × 1 | RGBA32 | Solid fills, gradient tinting |

**All six can be produced by an editor script** rather than drawn — radial gradients,
a repeating strip and a rounded rect are a handful of lines each against
`Texture2D.SetPixels`. Doing it that way keeps them regenerable and version-controlled
as code.

---

## 5. Explicitly not required

| Item | Why not |
|---|---|
| **Sprite sheets / character art** | There are no characters and no sprite animation. Every moving thing is a primitive. |
| **Orb textures (5 tiers)** | One SDF ring shader with a hue parameter covers all five. |
| **Pre-blurred glow sprites** | Bloom post-processing produces the glow. Baked halos would double up and look muddy. |
| **Background illustration** | The backdrop is a gradient plus a procedural grid. |
| **Explosion sprite sheets** | Particles are untextured streaks. |
| **Hand-drawn UI icons** | The ten icons the shipped build needs come from a free icon font (§3.3), not from artwork. |
| **Localisation assets** | Single language for launch; the character set is ASCII plus two symbols. Revisit per §3.7. |

Note that **audio and icons are no longer on this list** — they were, while the target
was a port of the browser build. A shipped Play release requires both; see §3.3–3.5.

---

## 6. Colour reference

Not an asset, but the values the shaders and materials need. Author every neon colour
as an **HDR colour in Linear space** — the intensity is what pushes it past the bloom
threshold. In gamma space, or at intensity 1.0, none of this glows.

| Token | Hex | HDR intensity | Applied to |
|---|---|---|---|
| Void | `#07030f` | — | Outer background |
| Deep | `#0e0820` | — | Playfield ground |
| Panel | `#150d2a` | — | Console and panel fills |
| Edge | `#2c1a52` | — | Borders, grid lines |
| Cyan | `#00eaff` | 2.2 | Cannon, bullets, ground line, wave number |
| Magenta | `#ff2d95` | 2.0 | Wheels, danger vignette, tier-3 orbs, `CRUSHED` |
| Violet | `#8b5cff` | 1.8 | Shields, tuner, grid |
| Lime | `#c6ff3d` | 2.0 | Scrap |
| Amber | `#ffb52e` | 2.0 | Fire rate, tier-2 orbs |
| Ink | `#ece2ff` | 1.0 | Body text, orb numbers |
| Muted | `#8d7bb8` | — | Labels, disabled states |

Orb hues are HSL at 100% saturation: tier 0 = 190°, tier 1 = 100°, tier 2 = 45°,
tier 3 = 325°, tier 4 = 272°. Ring lightness is 64%, rising to 94% on the hit flash.

---

## 7. Procurement summary

Ordered by what blocks what. "Blocking" means the game cannot ship without it.

| # | Item | Effort | Blocking? |
|---|---|---|---|
| 1 | Monoton + Chakra Petch → TMP SDF assets (§1.1–1.2) | ~30 min | **Yes.** Nothing renders type without them, and Monoton is the arcade identity |
| 2 | URP 2D renderer + bloom volume, Linear colour space | ~30 min | **Yes.** The look does not exist without bloom |
| 3 | **Audio: 13 SFX + 2 music loops (§3.4)** | **days, or a library licence** | **Yes.** Largest single procurement in the project. Start it first — it has the longest lead time and everything else is same-day work |
| 4 | Orb SDF ring shader — ring, fill and health arc in one (§2.1) | ~2–4 h | Yes for orbs |
| 5 | Paint ellipse + highlight SDF shader (§2.5) | ~1 h | Yes for paint. Replaces every paint texture |
| 6 | Rounded-rect + circle SDF shaders for UI (§2.7, §3.1) | ~1–2 h | Yes for all eight panels. 9-slice sprites work as a stand-in |
| 7 | Material Symbols Outlined → TMP SDF asset (§3.3) | ~15 min | **Yes.** Pause, settings and audio toggles need icons |
| 8 | Haptics via `VibrationEffect` (§3.5) | ~40 lines | **Yes** on mobile. No asset, no dependency |
| 9 | Six generated textures (§4), ideally via an editor script | ~1–2 h | Partially — placeholders work meanwhile |
| 10 | Backdrop grid shader (§2.3) | ~2 h | No — `LineRenderer`s work as a stand-in |
| 11 | **Play Store graphics: adaptive icon, 512² icon, 1024×500 feature graphic, ≥2 screenshots (§3.6)** | ~1 day | **Yes at submission.** Google will not accept the upload without them |

**No PNG lettering is required anywhere.** Both banners, the logo and the game-over
headline are live TextMeshPro text in Monoton — §1.2 explains why a sprite would
actively be worse.

### What actually has to be bought or commissioned

| | |
|---|---|
| **Fonts** | Three, all free: Monoton, Chakra Petch, Material Symbols Outlined |
| **Audio** | 13 SFX + 2 music loops. Royalty-free library, not a commission |
| **Artwork** | Play Store graphics only (§3.6) — the icon and feature graphic |
| **Paid plugins** | **None.** Not for paint, not for fluid, not for haptics |

Everything else is shader and tooling work rather than art production — the direct
consequence of the original being drawn in code rather than assembled from images.

**The two things most likely to bite you late:** audio has the longest lead time of
anything here and is easy to leave until the end, and the Play Store graphics (§3.6)
get discovered on submission day. Both are worth starting before the code is finished.
