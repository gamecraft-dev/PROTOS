# Neon Cannon — Art Asset Requirements for the Unity Port

What you need to source or commission to rebuild `neon-cannon/index.html` in Unity as
a 1:1 visual replica, and — just as importantly — what you do **not** need, because it
can be generated inside Unity with a shader, a mesh or a built-in effect.

**The short version:** the HTML build contains **zero image files**. Every pixel is
drawn procedurally on a canvas at runtime, so almost none of it needs an artist. For a
1:1 duplicate the only thing to source is **two free typefaces** (§1.1–1.2). No paid
plugin is required anywhere, the paint effect included (§2.5). Everything else is
either a generated texture you can author in ten minutes, or a shader.

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

**Unity setup required for both:**

| Step | Detail |
|---|---|
| Import | Drop the `.ttf` into `Assets/NeonCannon/Fonts/` |
| Convert | Window → TextMeshPro → Font Asset Creator |
| Atlas | 1024 × 1024, **SDF (Signed Distance Field)** render mode |
| Char set | ASCII + `×` (U+00D7, used by the tuner readouts) + `·` (U+00B7, used in labels) |
| Padding | 9 (needed headroom for the glow/dilate on the material) |
| Fallback | Assign a system font fallback so a missing glyph never renders as a box |

Chakra Petch also needs **tabular figures** for the HUD counters, or numbers will
jitter as they change. If the SDF asset does not expose the `tnum` feature, the
practical fix is a fixed-width TMP text container per digit group, or enabling the
font feature in the TMP font asset's Font Features panel.

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

### 1.3 Application icon

| Asset | Spec |
|---|---|
| App icon | 1024 × 1024 PNG, plus the platform-derived sizes Unity generates |

The HTML uses an emoji favicon, which does not port. This is genuinely new art — a
small piece, but it needs someone to draw it. The obvious subject is the cannon
silhouette in cyan on the `#07030f` ground.

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

## 3. Small generated textures — author once, no artist

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

## 4. Explicitly not required

| Item | Why not |
|---|---|
| **Sprite sheets / character art** | There are no characters and no sprite animation. Every moving thing is a primitive. |
| **Orb textures (5 tiers)** | One SDF ring shader with a hue parameter covers all five. |
| **Pre-blurred glow sprites** | Bloom post-processing produces the glow. Baked halos would double up and look muddy. |
| **Background illustration** | The backdrop is a gradient plus a procedural grid. |
| **Explosion sprite sheets** | Particles are untextured streaks. |
| **UI icon set** | The console is text-labelled; there are no icons in the source. |
| **Audio (music, SFX)** | The HTML build has **no audio whatsoever**. Adding sound is new design work, not part of a 1:1 replica. Flagged here so it is a deliberate decision rather than an omission. |
| **Localisation assets** | Single language, and the character set is ASCII plus two symbols. |

---

## 5. Colour reference

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

## 6. Procurement summary

| Priority | Item | Effort | Blocking? |
|---|---|---|---|
| 1 | Monoton + Chakra Petch, converted to TMP SDF assets | ~30 min | **Yes** — nothing renders type without them, and Monoton carries the arcade identity (§1.2) |
| 2 | URP 2D renderer + bloom volume configured, Linear colour space | ~30 min | **Yes** — the look does not exist without bloom |
| 3 | Six generated textures (§3), ideally via an editor script | ~1–2 h | Partially — placeholders work meanwhile |
| 4 | Orb SDF ring shader (ring + fill + health arc in one) | ~2–4 h | Yes for orbs |
| 5 | Rounded-rect SDF shader for UI | ~1–2 h | No — 9-slice sprites work as a stand-in |
| 6 | Backdrop grid shader | ~2 h | No — `LineRenderer`s work as a stand-in |
| 7 | Paint ellipse + highlight SDF shader (§2.5) | ~1 h | Yes for paint — replaces every paint texture |
| 8 | App icon | ~1 h | Only for store submission |

**No PNG lettering is required anywhere.** Both banners, the logo and the game-over
headline are live TextMeshPro text in Monoton — see §1.2 for why a sprite would
actively be worse.

**Total genuinely external procurement: two free fonts. No paid plugins, no
commissioned art.** Everything else is shader and tooling work rather than art
production — the direct consequence of the original being drawn in code rather than
assembled from images.
