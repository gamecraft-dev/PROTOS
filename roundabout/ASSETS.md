# Roundabout Rush: assets for the Unity build

The prototype has **no asset files**. Every car, tree, icon and effect is drawn in
code; every sound is synthesised; every ad and purchase is faked. That was right
for proving the game, but none of it is shippable art. This is the list of what
someone with art, audio or store-console access has to make or set up. I can
build everything else in Unity.

Each table marks priority:

- **MVP**: needed for a soft launch.
- **Later**: polish or live-ops.

Screens referenced below are in the prototype; open `index.html` to see where
each asset lives.

---

## What I can do without you, and what I can't

| I can build in Unity | You need to provide |
| --- | --- |
| All gameplay code, level generator, bots, save, economy, boosters | Car art (player skins and traffic) |
| Road meshes generated from splines, using your road textures | Road, ground, prop and decal textures |
| Particle systems and shaders (glow, tint, flash, dissolve), using your textures | VFX textures and flipbooks |
| UI layout, animation, transitions, 9-slicing, using your UI kit | The UI kit, icons, logo, app icon |
| Audio system: mixing, pooling, ducking under ads, music loop switching | Sound effects and music |
| Ad, IAP, analytics and remote-config integration code | The accounts, app IDs, ad unit IDs and product IDs |
| Placeholder art (the prototype's procedural cars can be ported as stand-ins) | Store listing art, screenshots, video, legal pages |

## Delivery rules

- **Format:** PNG, 32-bit with transparency, sRGB. No JPG for anything with
  edges. Layered source files (PSD, Figma, Blender) kept separately.
- **Resolution:** sizes below are the delivery size (already at 2× or 3× for
  phones). Don't upscale; deliver at least this big.
- **Orientation:** every car and vehicle sprite points **right (+X)**, centred
  on its pivot, with no baked drop shadow. The game draws one shared soft shadow.
- **Naming:** `area_name_variant.png`, lowercase, e.g. `car_vento_body.png`,
  `ui_btn_green_normal.png`, `fx_smoke_puff_01.png`.
- **Style:** a top-down night-time toy diorama. Deep navy ground (#0B1222),
  slate roads, warm lamp light, saturated cars with glowing headlights. The UI
  is chunky and bright on top of it (green #34C771, amber #FFC23D, violet
  #8E5CFF for anything that plays an ad, red #FF4D5E, blue #36A3FF). Match the
  prototype screenshots unless you are deliberately restyling.

## Summary

| Area | Count | Priority |
| --- | --- | --- |
| Player cars | 12 cars (in-game sprite, garage render, thumbnail; extras for 3) | MVP |
| Traffic cars | 3 body styles, tintable | MVP |
| Track and environment | ~20 textures / sprites | MVP |
| VFX | ~18 textures / flipbooks | MVP |
| UI kit | ~45 components and states | MVP |
| Icons | 36 | MVP |
| Branding and store | ~25 deliverables | MVP |
| Fonts | 2 families | MVP |
| Sound effects | 32 | MVP |
| Music | 3 tracks + 2 stingers | MVP (2), Later (1) |
| Accounts, IDs, legal | ~20 items | MVP |

---

## 1. Player cars

Twelve skins, all on the **same 24 × 13 footprint** (a 1.85 : 1 rectangle). Skins
never change the hitbox, so the outline can vary inside that box but must not
overhang it by more than a few percent.

**Per car, deliver:**

| Item | Spec | Used in |
| --- | --- | --- |
| In-game sprite | 192 × 104 px, top-down, pointing right | ring, queue, level-complete thumbnail |
| Lights layer | same canvas size; headlights and taillights only, on transparent | headlight glow, honk flash on win |
| Wreck sprite | same size, burnt and crumpled | crash wreckage |
| Garage render | 768 × 416 px, same top-down angle, higher detail | garage turntable, New Car popup |
| Grid thumbnail | 160 × 256 px, pointing **up** | garage grid, progress bar |

*Alternative:* one low-poly 3D model per car (≤ 3,000 triangles, one 512 px
texture atlas, pivot at centre, +X forward). I can then render the sprites and
make the garage a real 3D turntable. Pick one route for all cars.

| Car | Look | Rarity | Extras needed |
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
| Aurum | gold supercar, big rear wing | Legendary | metallic sheen (I can add the shine in a shader) |
| Neon X | dark angular cyber car with magenta edge glow | Legendary | separate glow layer |

**Later:** 8–12 more skins for live-ops (seasonal, event, IAP-exclusive).

## 2. Traffic cars

Traffic is recoloured per level (ten colours in the prototype). Deliver the
bodies in **greyscale with a body mask** so I can tint them in-engine.

| Item | Spec | Priority |
| --- | --- | --- |
| Sedan | 192 × 104 px greyscale body + mask + lights layer + wreck | MVP |
| Hatchback | same | MVP |
| SUV | same | MVP |
| Bus (2× length) | 384 × 120 px, same layers | Later: planned "slow bus" mechanic |
| Ambulance with siren | reuse Medic | Later: planned "never block it" mechanic |

## 3. Track and environment

The roads are generated from splines, so the textures must **tile along the
road's length**. Road width is 30 units: the texture is drawn across that width.

| Item | Spec | Priority |
| --- | --- | --- |
| Asphalt road strip | 256 × 256 px, tiles horizontally; asphalt with subtle grain | MVP |
| Road edge and curb strip | 256 × 32 px, tiles horizontally; light rim + dark outline | MVP |
| Edge line | 256 × 8 px, tiles | MVP |
| Centre dash | 64 × 8 px (one dash and one gap) | MVP |
| Stop line with give-way triangles | 256 × 96 px decal | MVP |
| Direction chevron | 64 × 64 px decal, low contrast | MVP |
| Junction blend / mouth patch | 256 × 256 px, optional if the mesh blends well | Later |
| Island ground | 512 × 512 px tileable night grass, very dark | MVP |
| Background ground | 512 × 512 px tileable dark pavement or park | MVP |
| Trees | 4 variants, 128 × 128 px top-down canopy | MVP |
| Bushes / hedges | 3 variants, 96 × 96 px | Later |
| Street lamp | 48 × 48 px head + separate light-pool sprite 256 × 256 px | MVP |
| Rooftops / buildings for the screen edges | 4–6 variants, 256–512 px | Later |
| Scorch decal | 128 × 128 px | MVP |
| Skid marks | 256 × 64 px, 2 variants | Later |
| Traffic signal (Green Light booster) | 48 × 112 px housing + 3 lamp glows (red, amber, green) | MVP |
| Danger-zone stripe | 64 × 64 px tileable hazard stripe | Later (the prototype uses a flat tint) |

## 4. Visual effects

I will build the particle systems; these are the textures they need.

| Item | Spec | Used for |
| --- | --- | --- |
| Smoke puff | 3 variants, 128 × 128 px, soft greyscale | release tire smoke, crash smoke, wreck smoke |
| Fire / explosion | 16-frame flipbook, 256 × 256 px per frame | crash |
| Spark streak | 64 × 16 px, additive | crash |
| Debris shards | 6 small sprites, 32 × 32 px, tintable | crash |
| Shockwave ring | 256 × 256 px | crash, merge pulse, win pulse |
| Soft radial glow | 256 × 256 px | island flash green / red, lamp, signal |
| Headlight beam cone | 256 × 128 px, additive | every car |
| Confetti pieces | 6 shapes, 32 × 32 px, white (tinted in-engine) | level complete |
| Light rays / burst | 512 × 512 px | booster intro, new car, reward granted |
| Coin sparkle | 64 × 64 px | coin fly-in |
| Crane hook and cable | hook 64 × 96 px, cable 8 × 64 px tiling | Tow Truck |
| Autopilot badge | 64 × 64 px | armed car marker |
| Target reticle | 128 × 128 px | Tow Truck targeting |
| Slow-Mo screen vignette | 1024 × 1024 px edge gradient | Slow-Mo |
| Speed lines / wind streaks | 4 variants, 256 × 32 px | Later: rush-hour surge |

## 5. UI kit

Deliver each component as a 9-slice PNG at 3× (e.g. a button at 3× is about
180 px tall), with a **normal** and a **pressed** state. The prototype uses a
raised "3D" look: a lighter top, a darker 5 px base, and a white gloss on the
upper half.

| Component | States / variants | Priority |
| --- | --- | --- |
| Primary button | green, amber, violet (ad), red, blue, dark × normal / pressed / disabled | MVP |
| "AD" tag | small play-icon pill that sits inside violet buttons | MVP |
| Panel / card | dark panel with border and inner highlight | MVP |
| Ribbon / header tab | green, amber, red, blue, violet | MVP |
| Close (X) button | round | MVP |
| Round icon button | 46 px base (pause, settings, back, home-screen shortcuts) | MVP |
| Coin pill | with "+" button | MVP |
| Notification dot / count badge | red dot; green count; amber "+" | MVP |
| Home tile | Garage / Levels / Shop | MVP |
| Big Play button | wider, taller primary button | MVP |
| Level tile | unlocked, current (glow), locked, 0–3 stars, hard marker | MVP |
| Booster button | normal, count badge, empty (+), locked (level label), active ring, "TAP!" coach callout | MVP |
| Clock bar | track + fill (green, low = red pulse, Slow-Mo = blue, waiting = dim) | MVP |
| Car pips row | small car silhouette, off / on | MVP |
| Loading bar | splash | MVP |
| Car progress bar | violet fill + car thumbnail slot | MVP |
| Multiplier bar | 7 segments (×2 ×3 ×4 ×5 ×4 ×3 ×2) + needle | MVP |
| Revive countdown ring | amber ring, 8-step | MVP |
| Star | filled, empty; large for level complete, small for tiles | MVP |
| Toggle tile | sound / music / vibration on and off | MVP |
| Switch | on / off | MVP |
| Daily reward tile | normal, today (glow), claimed (tick), day-7 wide card | MVP |
| Shop offer banner | Starter Pack (with discount tag), Remove Ads | MVP |
| Coin pack card | 4 sizes of coin pile art + "Popular" / "Best value" tags | MVP |
| Booster row | icon well + buy button | MVP |
| Rarity chip | Common, Rare, Epic, Legendary | MVP |
| Garage turntable | platform ellipse + light sweep | MVP |
| Toast | neutral, success, error | MVP |
| Tutorial bubble + pointing hand | hand with a tap ring | MVP |
| Level intro banner | "LEVEL 12" + tag (Hard / Two roads / Rush hour / Reversed) | MVP |
| Speech / tip variants | | Later |

## 6. Icons

36 icons, single colour on transparent so I can tint them, 128 × 128 px, plus
the full-colour coin and star.

| Group | Icons |
| --- | --- |
| Navigation | pause, play, settings, back, home, close, check, chevron, plus, retry |
| Screens | garage, levels grid, shop cart, daily gift, crown (offer), no-ads |
| Settings | sound on, sound off, music on, music off, vibration on, vibration off, privacy document, restore |
| Boosters | Slow-Mo (hourglass), Green Light (traffic light), Tow Truck (hook), Autopilot (steering wheel) |
| Game | clock, flame (hard), crash burst, car, lock, video / ad, star, coin |

Coin and star need full-colour versions plus a coin pile in 4 sizes for the shop.

## 7. Branding and store

| Item | Spec | Priority |
| --- | --- | --- |
| Final game name | trademark and store search check; "Roundabout Rush" is a working title | MVP |
| Logo mark | roundabout traffic sign (blue disc, three white arrows), vector | MVP |
| Wordmark | game title lockup, vector + 2048 px PNG | MVP |
| App icon master | 1024 × 1024 px, no transparency, no rounded corners | MVP |
| Android adaptive icon | foreground + background layers, 432 × 432 px each | MVP |
| Splash / loading screen | portrait 1290 × 2796 px safe-area aware | MVP |
| iPhone screenshots | 6.9" 1320 × 2868 and 6.5" 1284 × 2778, 5–8 each | MVP |
| iPad screenshots | 13" 2064 × 2752, 5–8 | MVP if iPad is supported |
| Google Play screenshots | phone 1080 × 1920 or larger, 4–8 | MVP |
| Google Play feature graphic | 1024 × 500 px | MVP |
| App preview / promo video | 15–30 s, portrait, 886 × 1920 (App Store) / YouTube link (Play) | Later |
| Store text | title, subtitle, short and full description, keywords, what's new | MVP |
| UA ad creatives | 3–5 short videos (6–15 s) and banner sizes | Later |
| Playable ad | HTML5, < 5 MB | Later (the prototype is a head start) |

## 8. Fonts

| Font | Use | Licence |
| --- | --- | --- |
| **Bungee** (Google Fonts) | logo, big numbers, panel titles | SIL Open Font License: free for commercial use and embedding |
| **Fredoka** 400–700 (Google Fonts) | all other UI text | SIL Open Font License |

Download the TTF files and decide the languages, so I can build TextMeshPro
atlases with the right glyphs. Bungee has no Cyrillic or CJK; pick fallback
fonts if those languages are planned. Different fonts mean checking their
licence for app embedding.

## 9. Audio

All sound in the prototype is synthesised placeholders. Deliver **WAV, 48 kHz,
16-bit or 24-bit** masters, trimmed with no leading silence. I will import as
compressed (Vorbis / ADPCM) and mix them. Aim for short, punchy, toy-like sounds
that read on a phone speaker.

### Sound effects

| # | Sound | Notes |
| --- | --- | --- |
| 1 | Car launch | short rev and tyre chirp when a car leaves the stop line (3 variants) |
| 2 | Merge | small soft chime when a car joins the ring |
| 3 | Close call | whoosh + bright ping |
| 4 | Crash | metal impact + glass + boom (3 variants) |
| 5 | Wreck sizzle | short smoke / hiss tail |
| 6 | Clock tick | last 5 seconds |
| 7 | Time's up | buzzer |
| 8 | Level complete | short fanfare, 1.5–2 s |
| 9 | Level failed | short descending sting |
| 10 | Car honks | 2–3 cheerful honks for the win moment |
| 11 | Star 1 / 2 / 3 | rising pitches |
| 12 | Coin collect | single + rapid multi-coin |
| 13 | Coin count-up | short loop |
| 14 | Multiplier needle tick | |
| 15 | Button tap | |
| 16 | Panel open / close | |
| 17 | Toggle on / off | |
| 18 | Error / not allowed | |
| 19 | Slow-Mo on / off | pitch-down whoom and recovery |
| 20 | Green Light on | two-tone signal beep |
| 21 | Tow Truck | crane winch + lift-off (the car leaving the screen) |
| 22 | Autopilot arm / go | robotic blip |
| 23 | Booster unlock | reveal fanfare |
| 24 | New car unlocked | bigger reveal |
| 25 | Purchase success | cash register / sparkle |
| 26 | Reward granted | after a rewarded video |
| 27 | Daily reward claim | gift open |
| 28 | Revive | whoosh back to life |
| 29 | Level intro | short swoosh as "LEVEL 12" lands |
| 30 | Hard level intro | heavier version |
| 31 | Rush hour surge | engine swell (Later) |
| 32 | Ambient traffic bed | quiet city loop under gameplay, 30–60 s (Later) |

### Music

| Track | Length | Notes | Priority |
| --- | --- | --- | --- |
| Home / menu loop | 60–90 s, seamless | relaxed, warm, light | MVP |
| Gameplay loop | 90–120 s, seamless | upbeat, driving, not busy; must sit under SFX | MVP |
| Hard level / rush hour loop | 60–90 s | more tension; same key as gameplay so it can crossfade | Later |
| Win stinger / lose stinger | 2–3 s each | can replace SFX 8 and 9 | MVP |

Deliver music at −16 LUFS integrated and effects peaking around −3 dBFS. Music
is licensed for commercial use in apps and ads (buyout or written licence).

## 10. Text and localisation

| Item | Priority |
| --- | --- |
| UI strings (roughly 150–200; I can extract them from the prototype into a spreadsheet) | MVP |
| Tutorial and tip lines | MVP |
| Store listing copy | MVP |
| Translations: start with EN, ES, PT-BR, FR, DE, RU, JA, KO, ZH (simplified) | Later |

## 11. Accounts, IDs and legal

Not art, but the game can't ship without them, and only you can create them.

| Item | Detail | Priority |
| --- | --- | --- |
| Apple Developer account | organisation or individual | MVP |
| Google Play Console account | | MVP |
| Bundle / package ID | e.g. `com.yourstudio.roundaboutrush` | MVP |
| Signing | iOS certificates and profiles; Android upload keystore (back it up) | MVP |
| Ad mediation account | AppLovin MAX, Unity LevelPlay or AdMob | MVP |
| Ad unit IDs | banner, interstitial, rewarded, each for iOS and Android | MVP |
| `app-ads.txt` | hosted on your developer website domain | MVP |
| Consent | Google UMP or another CMP for GDPR / US state privacy | MVP |
| iOS App Tracking Transparency | prompt text for `NSUserTrackingUsageDescription` | MVP |
| IAP products | `noads` (non-consumable), `starter` (non-consumable), `coins1`–`coins4` (consumable), created in both consoles with prices | MVP |
| Analytics | Firebase project (`GoogleService-Info.plist`, `google-services.json`) or GameAnalytics keys | MVP |
| Remote Config | same Firebase project; keys mirror `ECON` and `ADS` | Later |
| Privacy policy URL | must mention ads, analytics, purchases | MVP |
| Terms of use URL | | MVP |
| Support email and website | shown in Settings and the stores | MVP |
| Age rating questionnaires and Play data-safety form | | MVP |
| Crash reporting | Firebase Crashlytics or Sentry project | Later |

---

## Quick start: the smallest set to see it running in Unity

If you want a playable Unity build fast and the rest later, these 15 items are enough:

1. One player car sprite (Zippy) and one traffic sedan (greyscale + mask).
2. Asphalt strip, curb strip, centre dash, stop line.
3. Island and background ground tiles.
4. One tree, one lamp with light pool.
5. Smoke puff, explosion flipbook, glow.
6. Green, amber and violet button; panel; ribbon; coin pill.
7. Icon set (even a free licensed pack to start).
8. Bungee and Fredoka TTFs.
9. Launch, merge, crash, win and click sounds.
10. One gameplay music loop.
11. Ad mediation test IDs (every network provides test units).
12. App icon draft.
13. Final name decision.
14. Privacy policy URL.
15. Bundle ID.
