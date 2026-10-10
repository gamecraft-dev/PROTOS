# Birthday slice (Cake Sort)

The game asset for the Birthday cake's slice: frosted all the way down the outside. Built by `../cake_slice.py` in Blender 4.2 and checked
by the same script; everything here is generated. Rebuild with (from `playbox/art/cake-sort/`):

    blender -b -P cake_slice.py -- --cake birthday --out birthday --glb --views hero,game,single,lodviews

## Files

| File | What it is |
| --- | --- |
| `birthday_slice.glb` | The game mesh: one mesh, one material, 1030 triangles, 512 albedo + normal atlas (embedded) |
| `textures/BirthdaySlice_albedo.png`, `BirthdaySlice_normal.png` | The same atlas as loose files (512); `*_1024.png` are the bake masters |
| `renders/hero.png`, `game_cake.png`, `game_single.png` | The hi-res model (render only, about 126,658 triangles) |
| `renders/lod_game_cake.png`, `lod_game_single.png` | The GLB as the game camera sees it, with the outline drawn by an inverted hull |
| `renders/*_alpha_0001.png` | Each render again on a transparent background (for UI art) |
| `stats.json` | Every check's numbers from the last build |

The build also saves `birthday_slice.blend` (both versions, lights and cameras) next to these; it is not kept in the
repository, since the script rebuilds it.

## Units and orientation

- Radius 1, pivot at the cake's centre (the slice's point). Height 0.71 (the game camera is pitched 42.84
  degrees down, so it shows as 0.52 R on screen); the topping reaches 1.208.
- In Blender the slice spans 0..60 degrees from +X toward +Y. The GLB is +Y up: the slice lies in the
  XZ plane from +X toward -Z. glTFast and UnityGLTF negate X, so in Unity it runs from -X toward -Z.
  Slot k of a plate is the slice turned 60 k degrees about Y.
- Six slices tile a whole cake: no visible overlap with copies at +60/-60/180 degrees, and no ray from
  the game camera reaches a sponge cut face from outside (see Checks).

## Material

One material: base colour and tangent-space normal from the atlas, roughness 0.45, single-sided
(backface culling on). Sponge faces that are always covered get no texture space. The material also carries
Blender's clearcoat and specular values (KHR_materials_clearcoat, KHR_materials_specular); URP ignores them,
and the slice's look comes from the toon slice shader, not from these.

The candle's flame is part of the mesh, baked as a flat warm yellow (#FFC94A). The game's 2D candle flickers;
in Unity give the flame's few triangles (the topmost, above y 1.08) an unlit or emissive look in the slice
shader, or hide them and draw a flame sprite or particle at the wick (about y 1.09 at the slice's middle).

## The outline (an inverted hull, in the slice shader's outline pass)

Ink colour for this cake: `#18304A`. Smooth normals for the shell are stored in the second and third
texture-coordinate sets, because the cut faces split the shading normals and a hull built from them would
crack at the corners.

In Unity, after glTFast or UnityGLTF (both negate X on positions and normals and flip v on every
texture-coordinate set):

    outlineNormal = normalize(float3(-uv1.x, 1 - uv1.y, uv2.x))   // object space
    weight        = 1 - uv2.y
    // shell: cull front faces, colour #18304A, and push each vertex out by a fixed number of screen
    // pixels, so the line keeps its weight at every plate size (in object units it would vanish: at the
    // counter a plate is about 76 px across at 2x, R about 29 px, so 0.015 R is under half a pixel):
    float4 pos = TransformObjectToHClip(positionOS);
    float3 nWS = TransformObjectToWorldDir(outlineNormal);
    float2 nCS = SafeNormalize(float3(mul((float3x3)UNITY_MATRIX_VP, nWS).xy, 0)).xy;   // no NaN facing the camera
    float  px  = _OutlinePx * weight * step(0.5, weight);        // _OutlinePx about 2.5 at 2x, 1.5 at 1x
    pos.xy    += nCS * (2.0 * px / _ScreenParams.xy) * pos.w;
    // (if it must stay in object units, use about 0.09 R at the 76 px plate.) The previews here draw
    // the shell in object units, 0.015 R, which is about 4 px at their 900 px scale.
    // weight 1: the cake; 0.5: the coat's lip at the counter (where the normal points down and out)
    // weight 0.25: piped cream: no shell, no ink
    // weight 0: the topping: no shell (it would poke through what it sits on); instead ink the
    //           surface at grazing angles: lerp(albedo, ink, smoothstep(0.62, 0.8, facing)),
    //           facing = 1 - |dot(N, V)| (Blender's Layer Weight 'Facing', blend 0.2)

As written in the file (glTF space, before any importer): TEXCOORD_1 = (nx, ny), TEXCOORD_2 =
(nz, weight). A check that reads the GLB the way those importers do and applies the formula above
finds 115 of 115 smooth shell vertices with dot(outline normal,
normal) over 0.5 (worst 1.0); at hard edges (188 vertices) the shell normal is the
bisector of the faces that meet there (worst dot 0.354); weights found: {'0.0': 94, '0.25': 700, '0.5': 21, '1.0': 282}.
TEXCOORD_0 (the atlas) spans [0.008, 0.991] and never equals TEXCOORD_1.

## Checks (from the last build)

| Check | Result |
| --- | --- |
| GLB re-imported | 1 mesh, 1030 triangles, origin [0.0, 0.0, 0.0], materials 1, double-sided [False], vertex colours none |
| Top of the cake stays in the wedge | [0.0, 60.0] degrees |
| Visible overlaps with neighbours (hi-res / game) | [0, 0, 0] / [0, 0, 0] |
| Rays reaching sponge cut faces from outside (whole cake) | 0 of 90,884 |
| First hits on back faces (game mesh: lone slice / whole cake; 12 headings, a ray every 0.006, grid kept off the seam planes) | 0 of 293,187 / 0 of 1,091,448 |
| Topping normals bent past tangent z 0.3 | 0.0% of 1920 samples |
