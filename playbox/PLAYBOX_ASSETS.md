# Playbox: assets you need to make or supply

`PLAYBOX_UNITY_PLAN.md` has the agent generate every mesh, shader, texture,
sprite, icon, particle, sound and music loop the three games need, so the whole
app runs without anything from you. This file lists what the agent **can't**
make: things that need a person, a licence, an account or a store console, and
art you may want in place of the generated stand-ins.

It has one section per scope. Section 1 covers the whole app; sections 2–4
cover one game each.

**Priority labels**

- **Required**: the app can't ship without it.
- **Recommended**: ships without it, but it's what turns a prototype look into a
  store-quality one.
- **Optional**: polish, live-ops or later.

**Where things plug in.** Every item names its slot in the Unity project, so you
can drop a file in and see it replace the generated version: `UiSkin.asset`
(sprites), `IconSet.asset` (icons), `FontSet.asset` (fonts), `SfxLibrary.asset`
(sounds), the game's music clip, `AdConfig.asset` (ad ids), and
`ProductCatalog.asset` (store ids).

---

## Delivery rules (every section)

- **Images:** PNG, 32-bit with transparency, sRGB. No JPG for anything with
  edges. Keep layered sources (PSD, Figma, Blender) separately.
- **Resolution:** the sizes given are the delivery size (already 2–3× for
  phones). Don't upscale; deliver at least this big.
- **Naming:** `area_name_variant.png`, lowercase, e.g. `cl_car_vento_body.png`,
  `ps_btn_primary_normal.png`, `hex_icon_rotate_left.png`. Prefix with the game:
  `app_`, `ps_`, `hex_`, `cl_`.
- **UI pieces:** 9-slice PNGs at 3×, each with **normal** and **pressed** states
  (and **disabled** where marked), with the slice borders noted.
- **Icons:** single colour (white) on transparent at 128 × 128 so they can be
  tinted, unless marked full colour.
- **Audio:** WAV, 48 kHz, 16- or 24-bit, trimmed with no leading silence. Sound
  effects peak around −3 dBFS; music at −16 LUFS integrated. The agent imports
  them compressed and mixes them.
- **Licences:** anything you didn't make yourself must be licensed for
  commercial use in apps and in ads (buyout or written licence). Keep the
  licence files with the assets.

---

## Summary

| Section | Required | Recommended | Optional |
| --- | --- | --- | --- |
| 1. Playbox app | name, app icon, splash logo, store listing, 6 font families, accounts and ids, ad and purchase setup, analytics config, legal pages | brand sheet, review of the UI strings | localisation, promo video, crash reporting, remote config |
| 2. Paint Sort | nothing beyond section 1 | wall illustrations, UI skin | icon set, music loop |
| 3. Hex Tile Sort | nothing beyond section 1 | — | tile material, icon set, music loop, sound pass |
| 4. Car Loop | its ad units and store products (set up in section 1) | car art, track art, sound pass | VFX textures, UI kit, icons, music, extra cars |

---

## 1. Playbox app (shared by all three games)

### 1.1 Name and branding

| Item | Spec | Priority |
| --- | --- | --- |
| Final app name | Check store search and trademarks. "Playbox" is the working name; the game names (Paint Sort, Hex Tile Sort, Car Loop) stay as they are | Required |
| Logo mark | Vector (SVG or AI) plus a 1024 px PNG; used on the splash and the Hub's top row (replaces the generated mark) | Required |
| Wordmark | "Playbox" lockup, vector plus a 2048 px PNG | Required |
| App icon master | 1024 × 1024 PNG, no transparency, no rounded corners (the stores round them) | Required |
| Android adaptive icon | Foreground and background layers, 432 × 432 each, the subject inside the 264 px safe circle | Required |
| Splash screen | Logo on the app background (`#EEF1F6` light / `#0E1220` dark), portrait 1290 × 2796, safe-area aware. Unity shows it for at most 1.2 s | Required |
| Brand sheet | One page: logo, colours (the plan's theme tokens), fonts, do/don't | Recommended |

### 1.2 Store listing

| Item | Spec | Priority |
| --- | --- | --- |
| iPhone screenshots | 6.9" 1320 × 2868 and 6.5" 1284 × 2778, 5–8 each; show the Hub and each game | Required |
| iPad screenshots | 13" 2064 × 2752, 5–8 | Required if iPad is supported |
| Google Play screenshots | Phone, 1080 × 1920 or larger, 4–8 | Required |
| Google Play feature graphic | 1024 × 500 | Required |
| Store text | Title, subtitle, short and full description, keywords, what's new | Required |
| App preview / promo video | 15–30 s portrait, 886 × 1920 (App Store) and a YouTube link (Play) | Optional |
| UA ad creatives | 3–5 short videos (6–15 s) and banner sizes | Optional |

### 1.3 Fonts

All six are on Google Fonts under the SIL Open Font License (free for commercial
use and embedding). Download the TTFs and say which languages you plan, so the
agent builds TextMeshPro atlases with the right glyphs. Drop them in
`Assets/_Project/Fonts/`; the plan's `FontSet` maps them to roles.

| Font | Weights | Used by | Priority |
| --- | --- | --- | --- |
| **Lilita One** | 400 | Hub and Paint Sort: titles, buttons, numbers | Required |
| **Figtree** | 500–800 | Hub and Paint Sort: body text | Required |
| **Baloo 2** | 600–800 | Hex Tile Sort: score, badges, titles, floats | Required |
| **Inter** | 500–700 | Hex Tile Sort: labels | Required |
| **Bungee** | 400 | Car Loop: titles, big numbers, level numbers | Required |
| **Fredoka** | 400–700 | Car Loop: all other text | Required |

Bungee and Lilita One have no Cyrillic or CJK; pick fallback fonts if those
languages are planned, and check their licences.

### 1.4 Accounts, ids and SDKs

Only you can create these. The agent writes all the integration code, and the
build runs with mock ads, a mock store and log-only analytics until they arrive.

| Item | Detail | Priority |
| --- | --- | --- |
| Apple Developer account | Organisation or individual | Required |
| Google Play Console account | | Required |
| Bundle / package id | e.g. `com.yourstudio.playbox` | Required |
| Signing | iOS certificates and profiles; Android upload keystore (back it up) | Required |
| Ad mediation choice and account | AppLovin MAX, Unity LevelPlay or AdMob. Tell the agent which, and import that SDK's Unity package | Required (Car Loop shows ads) |
| Ad unit ids | Banner, interstitial and rewarded, each for iOS and Android (6 ids), plus the network's test ids for development; they go in `AdConfig.asset` | Required |
| `app-ads.txt` | Hosted at the root of your developer website | Required |
| Consent | Google UMP or another CMP for GDPR and US state privacy; set up its messages in the network's console | Required |
| iOS tracking prompt text | The `NSUserTrackingUsageDescription` sentence, e.g. "Your data will be used to show you more relevant ads." | Required |
| In-app products | Create in both consoles, with prices: `noads` (non-consumable, $3.99), `carloop_starter` (non-consumable, $1.99), `carloop_coins1`–`carloop_coins4` (consumable: $0.99, $2.99, $4.99, $9.99). If your store ids differ, give the mapping for `ProductCatalog.asset` | Required |
| Sandbox / test accounts | App Store sandbox testers and Play licence testers, to test purchases on devices | Required |
| Analytics | A Firebase project: `GoogleService-Info.plist` and `google-services.json`, and the Firebase Analytics Unity SDK (or GameAnalytics keys) | Required |
| Crash reporting | Firebase Crashlytics or a Sentry project | Optional |
| Remote Config | Same Firebase project; the keys mirror Car Loop's economy and ad settings | Optional |

### 1.5 Legal and support

| Item | Detail | Priority |
| --- | --- | --- |
| Privacy policy URL | Must cover ads, analytics, purchases and the consent choices; opened from Settings in the Hub and in Car Loop | Required |
| Terms of use URL | | Required |
| Support email and website | Shown in the stores and in Settings | Required |
| Age rating questionnaires | App Store and Google Play (IARC) | Required |
| Google Play data-safety form | Declares ads, analytics and purchase data | Required |
| App Privacy details (App Store) | Same data, Apple's form | Required |

### 1.6 Text and localisation

| Item | Priority |
| --- | --- |
| Review of the UI strings (the agent exports them from the `StringTable` assets to a spreadsheet) | Recommended |
| Translations: start with EN, ES, PT-BR, FR, DE, RU, JA, KO, ZH (simplified) | Optional |

---

## 2. Paint Sort

Everything in Paint Sort is generated: vial meshes, the liquid and stream
shaders, the painting on the easel, cork, frame, symbols, particles, icons,
and all 46 sounds. **Nothing here is required** beyond section 1. These items
replace generated stand-ins.

### 2.1 Art

| Item | Spec | Slot | Priority |
| --- | --- | --- | --- |
| Wall illustrations | Three backgrounds behind the vials: normal, hard, super hard. Portrait 1290 × 2796, soft and low-contrast so paint colours read on top; match the light and dark themes (6 files) or deliver one set and let the theme tint it. They replace the two-colour gradients | `UiSkin.ps_wall_{normal,hard,super}_{light,dark}` | Recommended |
| UI skin | Buttons (primary, hard red, super-hard violet, ghost; normal / pressed / disabled), booster tile, sheet background, coin pill, top-bar buttons, stuck bar, win-sheet frame. 9-slice at 3× | `UiSkin.ps_*` | Recommended |
| Easel frame | A wooden frame for the painting (9-slice, border ~16 px at 1×) to replace the generated gradient frame | `UiSkin.ps_frame` | Optional |
| Cork | 256 × 192 cork top, pivot top-centre | `UiSkin.ps_cork` | Optional |
| Paint Sort logo | A "Paint Sort" wordmark for the lobby, replacing the coloured-letter text | `UiSkin.ps_wordmark` | Optional |

### 2.2 Icons (single colour, 128 × 128)

Restart, undo, hint, add vial, back, menu, settings, play, coin (full colour).
Replace the generated `ps_*` icons. **Optional.**

### 2.3 Audio

| Item | Spec | Priority |
| --- | --- | --- |
| Music loop | 60–90 s seamless, calm and light, sits under the pour sounds. Paint Sort has no music in the plan; this adds it (the agent wires it to the Music setting) | Optional |
| Sound pass | Replacements for any of the 46 generated sounds (glug, pour bed, plop, cork chimes, bonk, undo, hint, coin, win, hard-level intros). Keep the glug as 12 pitched variants so the filling effect still works | Optional |

### 2.4 Store

Two or three of the app's screenshots should show Paint Sort (a pour in
progress and a finished painting). Covered by section 1.2.

---

## 3. Hex Tile Sort

Hex Tile Sort is built in 3D from generated hex prisms and two custom shaders,
with generated icons and 25 generated sounds. **Nothing here is required**
beyond section 1 (its fonts, Baloo 2 and Inter, are listed in 1.3).

### 3.1 Art

| Item | Spec | Slot | Priority |
| --- | --- | --- | --- |
| Tile material | A top-face texture or normal map for the hex tiles (256 × 256, greyscale so it can be tinted to the 7 colours), e.g. a soft bevel or glaze. The shader keeps the plan's colours and rim | `HexTile` material `_Detail` | Optional |
| Board backdrop | Portrait 1290 × 2796 in the game's plum palette (`#3A1B6E`, `#150C36`, `#0B0722`), replacing the generated gradient backdrop | `UiSkin.hex_backdrop` | Optional |
| HUD skin | Stat panels, icon buttons, the "Play again" button (normal / pressed), game-over card. 9-slice at 3× | `UiSkin.hex_*` | Optional |

### 3.2 Icons (single colour, 128 × 128)

Sound on, sound off, restart, rotate left, rotate right, back. Replace the
generated `hex_*` icons. **Optional.**

### 3.3 Audio

| Item | Spec | Priority |
| --- | --- | --- |
| Sound pass | Place, tile flip (11 rising variants), clear (8 rising variants by combo), pick, prime, bad drop, game over | Optional |
| Music loop | 60–90 s seamless, upbeat and light. Hex Tile Sort has no music in the plan | Optional |

---

## 4. Car Loop

Car Loop is the game with ads and purchases, so its section of the accounts work
in 1.4 (ad unit ids, the five Car Loop store products, consent) is what makes it
shippable. Its art and audio are all generated stand-ins: the agent ports the
prototype's procedural cars, roads, trees, effects, icons, 22 sounds and the
music loop. The art below is what a polished release would replace them with.

### 4.1 Required for Car Loop

| Item | Where it is set up | Priority |
| --- | --- | --- |
| Ad unit ids (banner, interstitial, rewarded × iOS/Android) | 1.4 | Required |
| Store products `noads`, `carloop_starter`, `carloop_coins1`–`4` | 1.4 | Required |
| Privacy policy that covers ads and purchases | 1.5 | Required |
| Fonts Bungee and Fredoka | 1.3 | Required |

### 4.2 Player cars

Twelve skins, all on the **same 24 × 13 footprint** (a 1.85 : 1 rectangle).
Skins never change the hitbox, so the outline can vary inside that box but must
not overhang it by more than a few percent. Every car sprite points **right
(+X)**, centred on its pivot, with no baked shadow (the game draws one shared
soft shadow).

**Per car:**

| Item | Spec | Used in |
| --- | --- | --- |
| In-game sprite | 192 × 104 px, top-down, pointing right | ring, queue, level-complete thumbnail |
| Lights layer | Same canvas; headlights and taillights only, on transparent | headlight glow, honk flash on win |
| Wreck sprite | Same size, burnt and crumpled | crash wreckage |
| Garage render | 768 × 416 px, same angle, more detail | garage turntable, New Car panel |
| Grid thumbnail | 160 × 256 px, pointing **up** | garage grid, progress bar |

*Alternative:* one low-poly 3D model per car (≤ 3,000 triangles, one 512 px
texture atlas, pivot at centre, +X forward). The agent can then render the
sprites and make the garage a real 3D turntable. Pick one route for all cars.

| Car | Look | Rarity | Extras |
| --- | --- | --- | --- |
| Zippy | small rounded compact, orange-yellow | Common | |
| City Cab | yellow taxi, roof sign | Common | |
| Mint Hatch | mint hatchback | Common | |
| Patrol | black-and-white police car | Rare | light bar, 2 frames (red on / blue on) |
| Ranger | orange pickup with open bed | Rare | |
| Vento GT | red sports coupé, white centre stripe | Rare | |
| Medic | white ambulance, red stripe and cross | Rare | light bar, 2 frames |
| Brute | dark muscle car, twin amber stripes, hood scoop | Epic | |
| Hauler | blue panel van | Epic | |
| Bolt R | cyan open-wheel racer with wings | Epic | |
| Aurum | gold supercar, big rear wing | Legendary | metallic sheen (the shader can add the shine) |
| Neon X | dark angular cyber car with magenta edge glow | Legendary | separate glow layer |

Priority: **Recommended** (the generated cars are faithful to the prototype but
read as placeholder art in a store listing). **Optional:** 8–12 more skins for
live-ops (seasonal, event, purchase-exclusive).

### 4.3 Traffic cars

Traffic is recoloured per level (ten colours). Deliver bodies in **greyscale
with a body mask** so they can be tinted in-engine.

| Item | Spec | Priority |
| --- | --- | --- |
| Sedan | 192 × 104 px greyscale body + mask + lights layer + wreck | Recommended |
| Hatchback | same | Recommended |
| SUV | same | Recommended |
| Bus (2× length) | 384 × 120 px, same layers; for a planned "slow bus" mechanic | Optional |

### 4.4 Track and environment

Roads are generated from the track geometry, so road textures must **tile along
the road's length**. Road width is 30 units; the texture runs across that width.

| Item | Spec | Priority |
| --- | --- | --- |
| Asphalt strip | 256 × 256 px, tiles horizontally, subtle grain | Recommended |
| Road edge and curb strip | 256 × 32 px, tiles; light rim + dark outline | Recommended |
| Edge line | 256 × 8 px, tiles | Optional |
| Centre dash | 64 × 8 px (one dash, one gap) | Optional |
| Stop line with give-way triangles | 256 × 96 px decal | Optional |
| Direction chevron | 64 × 64 px decal, low contrast | Optional |
| Island ground | 512 × 512 px tileable night grass, very dark | Recommended |
| Background ground | 512 × 512 px tileable dark pavement or park | Recommended |
| Trees | 4 variants, 128 × 128 px top-down canopy | Recommended |
| Bushes / hedges | 3 variants, 96 × 96 px | Optional |
| Street lamp | 48 × 48 px head + a 256 × 256 px light pool | Optional |
| Rooftops / buildings for the screen edges | 4–6 variants, 256–512 px | Optional |
| Scorch decal | 128 × 128 px | Optional |
| Skid marks | 256 × 64 px, 2 variants | Optional |
| Traffic signal (Green Light booster) | 48 × 112 px housing + 3 lamp glows | Optional |
| Danger-zone stripe | 64 × 64 px tileable hazard stripe | Optional |

Style: a top-down night-time toy diorama. Deep navy ground (`#0B1222`), slate
roads, warm lamp light, saturated cars with glowing headlights.

### 4.5 Visual effects textures

The agent builds the particle systems; these replace the generated textures.

| Item | Spec | Used for | Priority |
| --- | --- | --- | --- |
| Smoke puff | 3 variants, 128 × 128 px, soft greyscale | release smoke, crash smoke, wreck smoke | Optional |
| Fire / explosion | 16-frame flipbook, 256 × 256 px per frame | crash | Optional |
| Spark streak | 64 × 16 px, additive | crash | Optional |
| Debris shards | 6 sprites, 32 × 32 px, tintable | crash | Optional |
| Shockwave ring | 256 × 256 px | crash, merge pulse, win pulse | Optional |
| Soft radial glow | 256 × 256 px | island flash, lamps, signal | Optional |
| Headlight beam cone | 256 × 128 px, additive | every car | Optional |
| Confetti pieces | 6 shapes, 32 × 32 px, white | level complete | Optional |
| Light rays / burst | 512 × 512 px | booster intro, new car, reward | Optional |
| Coin sparkle | 64 × 64 px | coin fly-in | Optional |
| Crane hook and cable | hook 64 × 96 px, cable 8 × 64 px tiling | Tow Truck | Optional |
| Autopilot badge | 64 × 64 px | armed car | Optional |
| Target reticle | 128 × 128 px | Tow Truck targeting | Optional |
| Speed lines | 4 variants, 256 × 32 px | rush-hour surge | Optional |

### 4.6 UI kit

9-slice at 3× with normal and pressed states. The prototype's raised look: a
lighter top, a darker 5 px base and a white gloss on the upper half. Colours:
green `#34C771`, amber `#FFC23D`, violet `#8E5CFF` (anything that plays an ad),
red `#FF4D5E`, blue `#36A3FF`.

| Component | States / variants | Priority |
| --- | --- | --- |
| Primary button | green, amber, violet (ad), red, blue, dark × normal / pressed / disabled | Optional |
| "AD" tag | small play-icon pill inside violet buttons | Optional |
| Panel / card | dark panel with border and inner highlight | Optional |
| Ribbon / header tab | green, amber, red, blue, violet | Optional |
| Close (X) button, round icon button (46 px base) | | Optional |
| Coin pill with "+" | | Optional |
| Notification dot, count badge, amber "+" badge | | Optional |
| Home tiles (Garage, Levels, Shop), big Play button | | Optional |
| Level tile | unlocked, current (glow), locked, 0–3 stars, hard marker | Optional |
| Booster button | normal, count, empty (+), locked (level), active ring, "TAP!" callout | Optional |
| Clock bar | track + fill (green, low red, Slow-Mo blue, waiting dim) | Optional |
| Car pips, loading bar, car progress bar | | Optional |
| Multiplier bar | 7 segments (×2 ×3 ×4 ×5 ×4 ×3 ×2) + needle | Optional |
| Revive countdown ring | amber, 8 steps | Optional |
| Stars | filled, empty; large and small | Optional |
| Toggle tile, switch | on / off | Optional |
| Daily reward tile | normal, today (glow), claimed, day-7 wide card | Optional |
| Shop offer banners, coin pack cards (4 coin piles, "Popular" / "Best value") | | Optional |
| Booster row, rarity chips (Common, Rare, Epic, Legendary) | | Optional |
| Garage turntable | platform ellipse + light sweep | Optional |
| Toast | neutral, success, error | Optional |
| Tutorial bubble + pointing hand with tap ring | | Optional |
| Level intro banner | "LEVEL 12" + tag (Hard / Two roads / Rush hour / Reversed) | Optional |

### 4.7 Icons

36 single-colour icons at 128 × 128, plus full-colour coin, star and a coin
pile in 4 sizes for the shop. Replace the generated `cl_*` icons. **Optional.**

| Group | Icons |
| --- | --- |
| Navigation | pause, play, settings, back, home, close, check, chevron, plus, retry |
| Screens | garage, levels grid, shop cart, daily gift, crown (offer), no-ads |
| Settings | sound on/off, music on/off, vibration on/off, privacy document, restore |
| Boosters | Slow-Mo (hourglass), Green Light (traffic light), Tow Truck (hook), Autopilot (steering wheel) |
| Game | clock, flame (hard), crash burst, car, lock, video / ad, star, coin |

Car Loop's logo mark (the roundabout sign) is generated; a hand-drawn one can
replace `cl_sign` (vector + 512 px PNG). **Optional.**

### 4.8 Audio

The generated sounds and music are faithful to the prototype's synthesised
placeholders. Real recordings make the biggest difference to how the game feels.

**Sound effects** (Recommended as a set; any one can be replaced on its own):

| # | Sound | Notes |
| --- | --- | --- |
| 1 | Car launch | short rev and tyre chirp leaving the stop line (3 variants) |
| 2 | Merge | small soft chime when a car joins the ring |
| 3 | Close call | whoosh + bright ping |
| 4 | Crash | metal impact + glass + boom (3 variants) |
| 5 | Wreck sizzle | short smoke / hiss tail |
| 6 | Clock tick | last 5 seconds |
| 7 | Time's up | buzzer |
| 8 | Level complete | short fanfare, 1.5–2 s |
| 9 | Level failed | short descending sting |
| 10 | Car honks | 2–3 cheerful honks for the win |
| 11 | Star 1 / 2 / 3 | rising pitches |
| 12 | Coin collect | single + rapid multi-coin |
| 13 | Multiplier needle tick | |
| 14 | Button tap, panel open / close, toggle | |
| 15 | Error / not allowed | |
| 16 | Slow-Mo on / off | pitch-down whoom and recovery |
| 17 | Green Light on | two-tone signal beep |
| 18 | Tow Truck | crane winch + lift-off |
| 19 | Autopilot arm / go | robotic blip |
| 20 | Booster unlock, new car, reward granted | reveal fanfares |
| 21 | Purchase success, daily reward claim | |
| 22 | Revive | whoosh back to life |
| 23 | Level intro, hard level intro | swoosh as "LEVEL 12" lands |
| 24 | Rush-hour surge | engine swell (Optional) |
| 25 | Ambient traffic bed | quiet city loop under gameplay, 30–60 s (Optional) |

**Music:**

| Track | Length | Notes | Priority |
| --- | --- | --- | --- |
| Home / menu loop | 60–90 s, seamless | relaxed, warm, light | Recommended |
| Gameplay loop | 90–120 s, seamless | upbeat, driving, not busy; sits under the effects | Recommended |
| Hard level / rush-hour loop | 60–90 s | more tension, same key as gameplay so it can crossfade | Optional |
| Win / lose stingers | 2–3 s each | can replace sounds 8 and 9 | Optional |

### 4.9 Car Loop store assets

Two or three of the app's screenshots should show Car Loop (a merge into busy
traffic, the garage). A Car Loop playable ad (HTML5, under 5 MB) for user
acquisition can start from the web prototype. **Optional.**

---

## Quick start: the smallest set for a first store build

1. Final app name, bundle id, signing.
2. App icon, logo, splash.
3. The six font families (1.3).
4. Ad mediation choice, its SDK, test ad ids, then the real ad unit ids.
5. The six store products created in both consoles, plus sandbox testers.
6. Firebase config files.
7. Privacy policy, terms and support email.
8. Screenshots and store text.

Everything else in sections 2–4 can follow after launch, one slot at a time.
