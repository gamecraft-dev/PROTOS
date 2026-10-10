# Cake Sort: one cake's slice, built and rendered in Blender 4.2, with its game asset (GLB).
#
#   blender -b -P cake_slice.py -- --cake NAME --out DIR [--quick] [--views hero,game,single,lodviews] [--glb]
#
# NAME is one of the cakes in cake_specs.py (strawberry, chocolate, lemon, matcha, blueberry, birthday,
# mango, cookies, redvelvet, caramel). Units: the slice radius is 1. The slice is a sixth of a cake with
# its point at the origin (the plate centre) and spans 0..60 degrees from +X toward +Y, Z up. Its height
# is 0.71: the game camera is pitched 42.84 degrees down, so vertical lengths show at cos(42.84) = 0.733
# and this gives the 0.52 R the game draws on screen.
import bpy, bmesh, math, sys, os, json
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default
CAKE = arg('--cake', 'strawberry')
OUT = arg('--out', '/tmp/' + CAKE)
QUICK = '--quick' in argv
VIEWS = (arg('--views', 'hero,game,single')).split(',')
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[sys.argv.index('-P') + 1])))
from cake_common import *
from cake_specs import SPECS
import cake_toppings as TOP

SPEC = SPECS[CAKE]
TITLE = SPEC['title']
ASSET = ''.join(ch for ch in TITLE.title() if ch.isalnum()) + 'Slice'      # StrawberrySlice, CookiesCreamSlice, ...
COAT = SPEC['coat']
FULL = COAT['style'] == 'full'           # a coat all the way down the outside (else bare sides)

def mix_hex(a, b, k):
    ca, cb = lin(a), lin(b)
    return tuple(ca[i] * (1 - k) + cb[i] * k for i in range(3)) + (1.0,)

# ---------------------------------------------------------------- materials
SPG = SPEC['sponge']
SPONGE, SPONGE_LIGHT, PORE, CRUST = lin(SPG['base']), lin(SPG['light']), lin(SPG['pore']), lin(SPG['crust'])
INK = lin(SPEC['ink'])
# the fillings (bottom to top, in z), riding one slow wave with the sponge
CREAM_BANDS = [(lo, hi) for lo, hi, *_ in SPEC['bands']]
CRUST_TOP = 0.085                  # about 12% of the height

def sponge_material():
    m = principled('Sponge', SPONGE, rough=0.85, sss=0.12, sss_radius=(1, .7, .4), sss_scale=0.03)
    t = NT(m); bsdf = t.n['Principled BSDF']
    tc = t.node('ShaderNodeTexCoord'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Object'], sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    r = t.math('SQRT', t.math('ADD', t.math('MULTIPLY', x, x), t.math('MULTIPLY', y, y)))
    wave = t.math('ADD', t.math('MULTIPLY', t.math('SINE', t.math('ADD', t.math('MULTIPLY', r, 7.2), 0.9)), 0.022),
                  t.math('MULTIPLY', t.math('SINE', t.math('MULTIPLY', r, 19.0)), 0.005))
    ze = t.math('ADD', z, wave)
    def band_t(lo, hi):            # 0..1 across a band, clamped
        return t.math('DIVIDE', t.math('SUBTRACT', ze, lo), hi - lo)
    def near(edge, w):             # 1 on a line at z = edge, fading out over w
        return t.math('SUBTRACT', 1.0, t.math('DIVIDE', t.math('ABSOLUTE', t.math('SUBTRACT', ze, edge)), w), clamp=True)
    # the fillings, grouped by colour: a mask each; cream ones get a puffy rounded profile across the band
    e = 0.004
    groups = {}
    for lo, hi, col, shade, kind in SPEC['bands']:
        groups.setdefault((col, shade, kind), []).append((lo, hi))
    masks = []
    for (col, shade, kind), bands in groups.items():
        stops = [(0.0, (0, 0, 0))]
        for lo, hi in bands:
            stops += [(lo - e, (0, 0, 0)), (lo + e, (1, 1, 1)), (hi - e, (1, 1, 1)), (hi + e, (0, 0, 0))]
        masks.append((t.ramp(ze, stops), col, shade, kind, bands))
    puff = None
    for mask, col, shade, kind, bands in masks:
        if kind != 'cream': continue
        for lo, hi in bands:
            bt = t.math('MINIMUM', t.math('MAXIMUM', band_t(lo, hi), 0.0), 1.0)
            p = t.math('POWER', t.math('SINE', t.math('MULTIPLY', bt, math.pi)), 0.45)
            puff = p if puff is None else t.math('MAXIMUM', puff, p)
    # under each band the sponge sits in the filling's soft shadow
    shade = None
    for lo, hi in CREAM_BANDS:
        sh = t.math('SUBTRACT', 1.0, t.math('DIVIDE', t.math('SUBTRACT', lo, ze), 0.04), clamp=True)
        sh = t.math('MULTIPLY', sh, t.math('LESS_THAN', ze, lo))
        shade = sh if shade is None else t.math('MAXIMUM', shade, sh)
    # sponge: mottled, pores at about a third strength, a clean crust band with a wavy top
    noi = t.node('ShaderNodeTexNoise', in_Scale=18.0, in_Detail=6.0, in_Roughness=0.6)
    t.link(tc.outputs['Object'], noi.inputs['Vector'])
    vor = t.node('ShaderNodeTexVoronoi', in_Scale=48.0, in_Randomness=1.0)
    t.link(tc.outputs['Object'], vor.inputs['Vector'])
    pores = t.ramp(vor.outputs['Distance'], [(0.0, (1, 1, 1)), (0.15, (1, 1, 1)), (0.28, (0, 0, 0)), (1.0, (0, 0, 0))])
    vor2 = t.node('ShaderNodeTexVoronoi', in_Scale=120.0, in_Randomness=1.0)
    t.link(tc.outputs['Object'], vor2.inputs['Vector'])
    pores2 = t.ramp(vor2.outputs['Distance'], [(0.0, (1, 1, 1)), (0.12, (1, 1, 1)), (0.24, (0, 0, 0)), (1.0, (0, 0, 0))])
    pore_all = t.math('MAXIMUM', pores, t.math('MULTIPLY', pores2, 0.8))
    base = t.mix(noi.outputs['Fac'], SPONGE, SPONGE_LIGHT)
    base = t.mix(t.math('MULTIPLY', pore_all, 0.38), base, PORE)
    base = t.mix(t.math('MULTIPLY', shade, 0.45), base, lin(SPG['shade']))
    crust_f = t.ramp(ze, [(0.0, (1, 1, 1)), (CRUST_TOP - 0.006, (1, 1, 1)), (CRUST_TOP + 0.006, (0, 0, 0)), (1.0, (0, 0, 0))])
    crust_col = t.mix(t.ramp(ze, [(0.0, (1, 1, 1)), (0.03, (0, 0, 0)), (1.0, (0, 0, 0))]), CRUST, lin(SPG['crust_dark']))
    base = t.mix(crust_f, base, crust_col)
    col = base; any_mask = None; soft_mask = None
    for mask, c, sh, kind, bands in masks:
        fill = t.mix(t.math('MULTIPLY', noi.outputs['Fac'], 0.1), lin(c), lin(sh))
        col = t.mix(mask, col, fill)
        any_mask = mask if any_mask is None else t.math('MAXIMUM', any_mask, mask)
        if kind == 'cream': soft_mask = mask if soft_mask is None else t.math('MAXIMUM', soft_mask, mask)
    # ink lines at half weight along the edges of the fillings and the top of the crust
    ink = None
    for edge in [v for band in CREAM_BANDS for v in band] + [CRUST_TOP]:
        ln = near(edge, 0.0045)
        ink = ln if ink is None else t.math('MAXIMUM', ink, ln)
    col = t.mix(t.math('MULTIPLY', ink, 0.7), col, INK)
    t.link(col, bsdf.inputs['Base Color'])
    rough = t.node('ShaderNodeMapRange', in_To_Min=0.85, in_To_Max=0.4)
    t.link(any_mask, rough.inputs['Value']); t.link(rough.outputs['Result'], bsdf.inputs['Roughness'])
    if soft_mask is not any_mask:              # jam, curd, ganache, caramel: glossier still
        jam = t.math('SUBTRACT', any_mask, soft_mask) if soft_mask is not None else any_mask
        r2 = t.node('ShaderNodeMapRange', in_To_Min=0.0, in_To_Max=-0.22)
        t.link(jam, r2.inputs['Value'])
        t.link(t.math('ADD', rough.outputs['Result'], r2.outputs['Result']), bsdf.inputs['Roughness'])
    # relief: puffy cream standing proud, the sponge full of little holes
    h = t.math('SUBTRACT', t.math('MULTIPLY', puff, 1.0) if puff is not None else 0.0,
               t.math('MULTIPLY', t.math('MULTIPLY', pore_all, 0.3), t.math('SUBTRACT', 1.0, any_mask)))
    h = t.math('ADD', h, t.math('MULTIPLY', noi.outputs['Fac'], 0.12))
    bump = t.node('ShaderNodeBump', in_Strength=0.75, in_Distance=0.012)
    t.link(h, bump.inputs['Height']); t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def coat_material():
    """The coat: a glossy glaze (deeper toward its edges, where it turns away: wet depth) or a matte
    buttercream / cream cheese frosting with a soft spatula texture."""
    if COAT['kind'] == 'glaze':
        m = principled('Glaze', COAT['base'], rough=COAT['rough'], coat=COAT['coat'], coat_rough=COAT['coat_rough'], sss=COAT['sss'],
                       sss_radius=COAT['sss_radius'], sss_scale=0.03, spec=0.5)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc = t.node('ShaderNodeTexCoord'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Object'], sep.inputs[0])
        col = t.ramp(sep.outputs[2], [(p, lin(c)) for p, c in COAT['ramp']])
        lw = t.node('ShaderNodeLayerWeight', in_Blend=0.45)
        vd = t.node('ShaderNodeValue', name='ViewDep'); vd.outputs[0].default_value = 1.0     # 0 while baking
        edge = t.math('MULTIPLY', t.math('POWER', lw.outputs['Facing'], 1.6), vd.outputs[0])
        col = t.mix(t.math('MULTIPLY', edge, 0.75), col, lin(COAT['edge']))
        t.link(col, bsdf.inputs['Base Color'])
        noi = t.node('ShaderNodeTexNoise', in_Scale=6.0, in_Detail=2.0)
        t.link(tc.outputs['Object'], noi.inputs['Vector'])
        bump = t.node('ShaderNodeBump', in_Strength=0.06, in_Distance=0.01)
        t.link(noi.outputs['Fac'], bump.inputs['Height']); t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    m = principled('Glaze', COAT['base'], rough=COAT['rough'], coat=COAT['coat'], coat_rough=0.2, sss=COAT['sss'],
                   sss_radius=COAT['sss_radius'], sss_scale=0.02, spec=0.4)
    t = NT(m); bsdf = t.n['Principled BSDF']
    tc = t.node('ShaderNodeTexCoord'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Object'], sep.inputs[0])
    col = t.ramp(sep.outputs[2], [(p, lin(c)) for p, c in COAT['ramp']])
    # buttercream: broad soft spatula strokes and a fine grain
    noi = t.node('ShaderNodeTexNoise', in_Scale=4.5, in_Detail=3.0, in_Roughness=0.55)
    t.link(tc.outputs['Object'], noi.inputs['Vector'])
    fine = t.node('ShaderNodeTexNoise', in_Scale=60.0, in_Detail=2.0)
    t.link(tc.outputs['Object'], fine.inputs['Vector'])
    col = t.mix(t.math('MULTIPLY', t.math('SUBTRACT', noi.outputs['Fac'], 0.5), 0.35), col, lin(COAT['ramp'][-1][1]))
    pat = SPEC.get('pattern') or {}
    if pat.get('kind') == 'dust':
        # matcha dusted over the top: fine darker specks on what faces up
        nz = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Normal'], nz.inputs[0])
        up = t.math('MULTIPLY', t.math('SUBTRACT', nz.outputs[2], 0.55, clamp=True), 2.2, clamp=True)
        spk = t.node('ShaderNodeTexNoise', in_Scale=140.0, in_Detail=1.0)
        t.link(tc.outputs['Object'], spk.inputs['Vector'])
        dots = t.ramp(spk.outputs['Fac'], [(0.0, (0, 0, 0)), (0.58, (0, 0, 0)), (0.64, (1, 1, 1)), (1.0, (1, 1, 1))])
        cloud = t.node('ShaderNodeTexNoise', in_Scale=9.0, in_Detail=2.0)
        t.link(tc.outputs['Object'], cloud.inputs['Vector'])
        dust = t.math('MULTIPLY', t.math('ADD', t.math('MULTIPLY', dots, 0.75), t.math('MULTIPLY', cloud.outputs['Fac'], 0.25)), up)
        col = t.mix(t.math('MULTIPLY', dust, 0.8), col, lin(pat['colour']))
    t.link(col, bsdf.inputs['Base Color'])
    h = t.math('ADD', t.math('MULTIPLY', noi.outputs['Fac'], 1.0), t.math('MULTIPLY', fine.outputs['Fac'], 0.15))
    bump = t.node('ShaderNodeBump', in_Strength=0.22, in_Distance=0.012)
    t.link(h, bump.inputs['Height']); t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m

MAT = {
    'sponge': sponge_material(),
    'glaze': coat_material(),
    'cream': principled('Whipped cream', SPEC['pipe'] or '#FBF0DE', rough=0.48, coat=0.1, sss=0.35, sss_radius=(1, .9, .7), sss_scale=0.02),
    'plate': principled('Plate', '#FFFFFF', rough=0.18, coat=0.4),
    'plate_rim': principled('Plate rim', '#F6A8C2', rough=0.3, coat=0.3),
}

# ---------------------------------------------------------------- the sponge body
def build_body():
    bm = bmesh.new()
    n_arc = 48
    outline = [Vector((0, 0))] + [Vector((math.cos(SEG * i / n_arc), math.sin(SEG * i / n_arc))) * R for i in range(n_arc + 1)]
    bot = [bm.verts.new((p.x, p.y, 0.0)) for p in outline]
    top = [bm.verts.new((p.x, p.y, SPONGE_TOP)) for p in outline]
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        f.smooth = 0 < i < n - 1 and j != 0           # the curved outside is smooth, the cut faces flat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for e in bm.edges:
        e.smooth = all(f.smooth for f in e.link_faces)
    obj = mesh_obj('Sponge', bm, smooth=False)
    obj.data.materials.append(MAT['sponge'])
    bev = obj.modifiers.new('Soft edges', 'BEVEL'); bev.width = 0.012; bev.segments = 3; bev.limit_method = 'ANGLE'
    bev.harden_normals = False
    return obj

# ---------------------------------------------------------------- the glaze shell
DRIPS = {   # per cut face: (where along the face from the tip, how far down, how wide)
    # three broad drips a face, so even the low-poly glaze gives each a rounded tip
    'A': [(0.2, 0.065, 0.075), (0.5, 0.135, 0.08), (0.8, 0.095, 0.075)],
    'B': [(0.24, 0.1, 0.08), (0.55, 0.06, 0.075), (0.83, 0.125, 0.07)],
    # down bare sides (a naked cake's glaze): broad drips round the outside, none at the rim corners
    'arc': [(0.18, 0.09, 0.06), (0.41, 0.15, 0.065), (0.62, 0.07, 0.055), (0.83, 0.12, 0.06)],
} if COAT['drips'] == 'glaze' else {'A': [], 'B': [], 'arc': []}
BAND = COAT['band']                # how far the coat reaches down a cut face between drips
ARC_K = 0.4 if COAT['style'] == 'cap' else 1.0     # a thick cream cap sits nearly flush with the bare sides

def edge_ts(n_edge):
    # even steps, plus a few close to the rim, where the coat turns the corner and runs to the counter
    ts = [i / n_edge for i in range(n_edge)]
    for extra in (0.962, 0.976, 0.99):
        if min(abs(extra - t) for t in ts) > 0.006: ts.append(extra)
    return sorted(ts)

def perimeter(n_edge=40, n_arc=56):
    nA, nB = Vector((0, -1)), Vector((-math.sin(SEG), math.cos(SEG)))
    pts, ts = [], edge_ts(n_edge)
    for t in ts:
        pts.append([Vector((t * R, 0)), nA.copy(), 'A', t])
    for i in range(n_arc + 1):                               # both rim corners belong to the arc
        a = SEG * i / n_arc
        pts.append([Vector((math.cos(a), math.sin(a))) * R, Vector((math.cos(a), math.sin(a))), 'arc', i / n_arc])
    for t in sorted(ts[1:], reverse=True):
        pts.append([Vector((math.cos(SEG) * t, math.sin(SEG) * t)) * R, nB.copy(), 'B', t])
    # the tip bisects the two cut faces; the rim corners take the arc's normal, which runs along the
    # cut plane, so nothing there crosses into the neighbouring slice
    pts[0][1] = (nA + nB).normalized()
    return pts

GLAZE_FLOOR = [0.012]
def glaze_bottom(kind, t):
    """z of the bottom of the glaze skirt at this point of the outline."""
    full = GLAZE_FLOOR[0] + 0.006 * math.sin(t * 40)
    if kind == 'arc' and FULL:
        return full
    if kind == 'arc':                                          # bare sides: a band round the outside, with drips
        d = BAND + 0.008 * math.sin(t * 29) * math.sin(math.pi * t)
        for c, ln, w in DRIPS['arc']:
            d = max(d, BAND + ln * math.exp(-abs((t - c) / w) ** 2.2))
        return H_TOP - d
    wave = 0.01 * math.sin(t * 23 + (0 if kind == 'A' else 2))
    if not FULL: wave *= 1 - smoothstep(0.85, 1.0, t)          # meets the outside's band level at the rim corner
    d = BAND + wave
    for c, ln, w in DRIPS[kind]:
        d = max(d, BAND + ln * math.exp(-abs((t - c) / w) ** 2.2))
    z = H_TOP - d
    if not FULL: return z
    # near the rim the coat runs all the way down: it is the frosting on the outside, seen in section
    return z + (full - z) * smoothstep(0.955, 1.0, t)

# The glaze's cross-section, top to bottom: (offset off the outside, offset off a cut face, z).
# On the outside it rolls over the edge and stands off the sponge. On a cut face it stays inside the
# wedge above the top of the sponge (so in a whole cake it never crosses into the next slice); below
# that only its band and drips stand out, where in a whole cake they are buried in the next sponge.
def cut_k(z):
    return smoothstep(H_BODY - 0.008, H_BODY - 0.04, z)
GLAZE_ROWS = [
    (0.55, -0.45, lambda k, t: H_TOP - 0.004),                  # the rolled edge
    (0.92, -0.12, lambda k, t: H_TOP - 0.024),
    (1.0, 0.0, lambda k, t: H_BODY - 0.008),
    (1.0, 1.0, lambda k, t: glaze_bottom(k, t) + 0.035),
    (0.95, 0.95, lambda k, t: glaze_bottom(k, t) + 0.006),
    (0.55, 0.55, lambda k, t: glaze_bottom(k, t) - 0.004),        # the drip's rounded end, tucking in
    (0.1, 0.1, lambda k, t: glaze_bottom(k, t) + 0.012),
]

def build_glaze(name='Glaze', n_edge=40, n_arc=56, caps=(0.25, 0.5, 0.7, 0.84, 0.93, 0.975), rows=GLAZE_ROWS, subsurf=True, sharp_corners=False):
    P = perimeter(n_edge, n_arc)
    N = len(P)
    pos = []
    for s in caps:                                              # the cap, gently domed
        pos.append([(CENTROID + (p - CENTROID) * s).to_3d() + Vector((0, 0, H_TOP + 0.012 * (1 - s * s))) for p, n, k, t in P])
    for off_arc, off_cut, zf in rows:
        row = []
        for p, n, k, t in P:
            z = zf(k, t)
            # (a thick cream cap sits nearly flush down the sides, but its top edge rolls out like a glaze's: two
            # rim points meeting at a corner then stay apart, and the outline shell does not fold between them)
            off = off_arc * (ARC_K if off_arc >= 1.0 else 1.0) if k == 'arc' else (off_cut * cut_k(z) if off_cut > 0 else off_cut)
            # where the coat turns the rim corner it lies flat on the face; the smoothed (subdivided) coat
            # stands a little further off, or smoothing sinks it into the sponge
            # (the band's top row too, just enough near the rim that it does not reach into the next slice)
            flush = 0.2 if subsurf else 0.08
            if FULL and k != 'arc' and off > 0:
                off = off + (flush - off) * smoothstep(0.9, 0.958, t)
            elif FULL and k != 'arc' and off == 0 and subsurf:
                off = 0.08 * smoothstep(0.9, 0.958, t)
            if FULL and GLAZE_FLOOR[0] == 0.0 and zf is rows[-1][2] and (k == 'arc' and z < 0.04 or k != 'arc' and t > 0.985):
                z = 0.0                                          # the game mesh's coat meets the counter, no notch
            row.append((p + n * GLAZE_E * off).to_3d() + Vector((0, 0, z)))
        pos.append(row)
    bm = bmesh.new()
    centre = bm.verts.new((CENTROID.x, CENTROID.y, H_TOP + 0.012))
    V = [[bm.verts.new(p) for p in row] for row in pos]
    for i in range(N):
        bm.faces.new((centre, V[0][i], V[0][(i + 1) % N]))
    for r in range(len(V) - 1):
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((V[r][i], V[r + 1][i], V[r + 1][j], V[r][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sharp_corners:
        # the coat turning the rim corner: keep the cut-face strip and the outside from sharing normals
        cols = [i for i in range(N) if P[i][2] != P[i - 1][2] and i != 0]
        for r in range(len(caps), len(V) - 1):
            for c in cols:
                e = bm.edges.get((V[r][c], V[r + 1][c]))
                if e: e.smooth = False
        if COAT['kind'] == 'frosting':
            # matte frosting shows smooth shading streaking along the long top triangles when the rim's normals
            # lean out: keep the flat top's normals to itself (a glossy glaze keeps its smooth rolled highlight)
            for i in range(N):
                e = bm.edges.get((V[0][i], V[0][(i + 1) % N]))
                if e: e.smooth = False
    obj = mesh_obj(name, bm)
    obj.data.materials.append(MAT['glaze'])
    if subsurf:
        sub = obj.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    return obj

# ---------------------------------------------------------------- piped cream (TOP_SPOT: where the topping stands)
CREAM_H = 0.13                     # how tall the rosette rises

def build_cream(name='Whipped cream', star_n=42, turns=2.8, n=84, res=8, core=(24, 12)):
    star = bpy.data.curves.new(name + ' nozzle', 'CURVE'); star.dimensions = '2D'
    sp = star.splines.new('POLY'); pts = []
    for i in range(star_n):
        a = i / star_n * math.tau; r = 0.05 * (1 + 0.22 * math.cos(7 * a))      # seven rounded ridges
        pts.append((math.cos(a) * r, math.sin(a) * r, 0, 1))
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = c
    sp.use_cyclic_u = True
    star_obj = link(bpy.data.objects.new(name + ' nozzle', star)); star_obj.hide_render = True; star_obj.hide_viewport = True
    cu = bpy.data.curves.new(name + ' swirl', 'CURVE'); cu.dimensions = '3D'
    cu.bevel_mode = 'OBJECT'; cu.bevel_object = star_obj; cu.use_fill_caps = True
    cu.resolution_u = res; cu.twist_mode = 'MINIMUM'
    sp = cu.splines.new('NURBS')
    # piped the way a pastry chef does: out from the middle to make the base, then round and up to a
    # low peak, so the start of the bead is hidden inside the swirl from every side
    sp.points.add(n - 1)
    for i, p in enumerate(sp.points):
        u = i / (n - 1)
        a = u * turns * math.tau
        if u < 0.25:
            rr = 0.14 * (u / 0.25) ** 0.6; z = 0.035
        else:
            w = (u - 0.25) / 0.75
            rr = 0.14 * (1 - 0.55 * w ** 1.1); z = 0.04 + CREAM_H * w ** 0.9
        p.co = (math.cos(a) * rr, math.sin(a) * rr, z, 1)
        p.radius = 1.12 - 0.42 * max(0.0, (u - 0.25) / 0.75) ** 1.4
        p.tilt = u * 18.0                                  # the ridges twist as the cream is piped
    sp.use_endpoint_u = True; sp.order_u = 3
    tmp = link(bpy.data.objects.new(name + ' tmp', cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    # a soft core inside the swirl, so its middle never shows dark between the coils and the berry
    if core:
        cbm = bmesh.new(); cbm.from_mesh(me)
        bmesh.ops.create_uvsphere(cbm, u_segments=core[0], v_segments=core[1], radius=1.0,
                                  matrix=Matrix.Translation((0, 0, 0.075)) @ Matrix.Diagonal((0.085, 0.085, 0.065, 1)))
        if SPEC['topping'] != 'strawberry':
            # the berry fills the top of the swirl; a topping that sits higher would show its hollow, so fill it
            bmesh.ops.create_uvsphere(cbm, u_segments=core[0], v_segments=core[1], radius=1.0,
                                      matrix=Matrix.Translation((0, 0, 0.135)) @ Matrix.Diagonal((0.07, 0.07, 0.055, 1)))
        cbm.to_mesh(me); cbm.free()
    # the curve's bevel faces come out pointing inward: turn them out (engines cull back faces)
    cbm = bmesh.new(); cbm.from_mesh(me)
    bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
    if sum(f.calc_area() * f.normal.dot(f.calc_center_median()) for f in cbm.faces) < 0:
        bmesh.ops.reverse_faces(cbm, faces=cbm.faces)
    cbm.to_mesh(me); cbm.free()
    obj = link(bpy.data.objects.new(name, me))
    for p in me.polygons: p.use_smooth = True
    me.materials.clear(); me.materials.append(MAT['cream'])
    obj.location = TOP_SPOT - Vector((0, 0, 0.03))
    return obj

def build_cream_lod(name='Cream LOD', na=28, twist=1.6):
    """The rosette at game resolution, drawn rather than decimated (a coarse sweep of the piped bead
    crumples): three stacked tiers stepping in toward a soft peak, and seven rounded ridges that twist
    as they rise. The mesh columns follow the ridges round, so each crest stays on one column."""
    prof = [(0.0, 0.17), (0.02, 0.198), (0.042, 0.212), (0.064, 0.2), (0.08, 0.168),      # (z, radius): the base tier,
            (0.088, 0.132),                                                              # a tuck,
            (0.1, 0.156), (0.122, 0.164), (0.14, 0.142), (0.148, 0.098),                  # the second tier, a tuck,
            (0.175, 0.098), (0.2, 0.05)]                                                 # the third, mostly in the berry
    zt = prof[-1][0]
    bm = bmesh.new(); rings = []
    for z, r in prof:
        row = []
        for j in range(na):
            a = j / na * math.tau + twist * z / zt
            # rounded crests, sharp valleys, as a star nozzle pipes them
            rr = r * (1 + 0.1 * (2 * ((1 + math.cos(7 * j / na * math.tau)) / 2) ** 0.5 - 1))
            row.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z)))
        rings.append(row)
    peak = bm.verts.new((0.01, 0.004, 0.218))
    for i in range(len(rings) - 1):
        for j in range(na):
            k = (j + 1) % na
            bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    for j in range(na):
        bm.faces.new((rings[-1][j], rings[-1][(j + 1) % na], peak))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = mesh_obj(name, bm)
    obj.data.materials.append(MAT['cream'])
    obj.location = TOP_SPOT - Vector((0, 0, 0.03))
    return obj

# ---------------------------------------------------------------- ganache / caramel run down the outside
def build_drip_skin(name='Drips'):
    """A darker layer poured at the rim: over the rolled edge and down the frosted outside in drips. A thin
    skin standing a little off the coat; its ends sit in the cut planes, so in a whole cake it is one ring."""
    od = SPEC['outer_drips']
    n_arc = 72
    drips = [(0.1, 0.11, 0.045), (0.27, 0.2, 0.05), (0.46, 0.09, 0.04), (0.63, 0.24, 0.05), (0.84, 0.14, 0.045)]
    def bottom(t):
        d = 0.085 + 0.008 * math.sin(t * 31)
        for c, ln, w in drips:
            d = max(d, 0.085 + ln * math.exp(-abs((t - c) / w) ** 2.2))
        return H_TOP - d
    rows = [  # (on the top: how far in from the rim, off the outside, z)
        (0.035, None, lambda t: H_TOP + 0.006),
        (0.0, 0.55 + 0.38, lambda t: H_TOP - 0.001),
        (0.0, 0.92 + 0.38, lambda t: H_TOP - 0.022),
        (0.0, 1.0 + 0.36, lambda t: min(H_BODY - 0.01, bottom(t) + 0.04)),
        (0.0, 1.0 + 0.34, lambda t: bottom(t) + 0.008),
        (0.0, 1.0 + 0.12, lambda t: bottom(t) - 0.002),             # the rounded end of each drip, tucking in
        (0.0, 1.0 + 0.0, lambda t: bottom(t) + 0.01),
    ]
    bm = bmesh.new(); V = []
    for inset, off, zf in rows:
        row = []
        for i in range(n_arc + 1):
            t = i / n_arc; a = SEG * t; n = Vector((math.cos(a), math.sin(a)))
            p = n * (R - inset) if off is None else n * (R + GLAZE_E * off)
            row.append(bm.verts.new((p.x, p.y, zf(t))))
        V.append(row)
    for r in range(len(V) - 1):
        for i in range(n_arc):
            bm.faces.new((V[r][i], V[r][i + 1], V[r + 1][i + 1], V[r + 1][i]))
    bm.normal_update()
    if sum(f.normal.dot(f.calc_center_median().to_2d().to_3d()) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    obj = mesh_obj(name, bm)
    m = principled('Drip', od['colour'], rough=0.16, coat=0.7, coat_rough=0.05, sss=0.1, sss_radius=(1, .5, .25), sss_scale=0.02)
    t_ = NT(m); bsdf = t_.n['Principled BSDF']
    tc, sep = t_.obj_xyz()
    t_.link(t_.ramp(sep.outputs[2], [(0.45, lin(od['colour'])), (0.72, lin(od['light']))]), bsdf.inputs['Base Color'])
    obj.data.materials.append(m)
    sub = obj.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    return obj

# ---------------------------------------------------------------- assemble one slice
def coat_height(coat, xy):
    """The top of the (smoothed) coat at a point, so what sits on it sits on it."""
    for m in coat.modifiers:
        if m.type == 'SUBSURF': lv = m.levels; m.levels = m.render_levels
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = coat.evaluated_get(dg); me = ev.to_mesh()
    tree = BVHTree.FromPolygons([coat.matrix_world @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    ev.to_mesh_clear()
    for m in coat.modifiers:
        if m.type == 'SUBSURF': m.levels = lv
    hit = tree.ray_cast(Vector((xy[0], xy[1], 2.0)), Vector((0, 0, -1)))[0]
    return tree, hit.z

def build_slice():
    coll = bpy.data.collections.new(TITLE + ' slice'); scene.collection.children.link(coll)
    parts = [build_body(), build_glaze()]
    if SPEC['pipe']: parts.append(build_cream())
    tree, top_z = coat_height(parts[1], TOP_SPOT.xy)
    env = dict(top_z=top_z, coat_tree=tree, piped=bool(SPEC['pipe']), lod=False)
    TOPPING.update(TOP.build(SPEC, env))
    parts += TOPPING['parts']
    extras = []
    if SPEC.get('outer_drips'): extras.append(build_drip_skin())
    if SPEC.get('pattern'): extras += TOP.build_pattern(SPEC, env)
    parts += extras
    slice_root = bpy.data.objects.new(TITLE + ' slice', None)
    coll.objects.link(slice_root)
    root = TOPPING['root']
    for o in parts + [root]:
        for c in o.users_collection: c.objects.unlink(o)
        coll.objects.link(o)
    for o in parts[:3 if SPEC['pipe'] else 2] + extras + [root]: o.parent = slice_root
    return slice_root, coll, parts, extras

TOPPING = {}
slice_root, slice_coll, PARTS, EXTRAS = build_slice()
BODY, COAT_OBJ = PARTS[0], PARTS[1]
CREAM_OBJ = PARTS[2] if SPEC['pipe'] else None

# ---------------------------------------------------------------- stats for the technical review
def stats():
    saved = []
    for o in PARTS:                                          # count at the render levels, not the viewport's
        for m in o.modifiers:
            if m.type == 'SUBSURF': saved.append((m, m.levels)); m.levels = m.render_levels
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out = {'objects': {}, 'tris_render': 0}
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in PARTS:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        me.calc_loop_triangles()
        tris = len(me.loop_triangles)
        out['objects'][o.name] = tris; out['tris_render'] += tris
        for v in me.vertices:
            w = o.matrix_world @ v.co
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
        ev.to_mesh_clear()
    # the sponge must be an exact sixth: every vertex between 0 and 60 degrees, within radius 1
    body = PARTS[0]; angs = []
    for v in body.data.vertices:
        if v.co.xy.length > 1e-6: angs.append(math.degrees(math.atan2(v.co.y, v.co.x)))
    out['body_angle_range_deg'] = [round(min(angs), 4), round(max(angs), 4)]
    out['body_max_radius'] = round(max(v.co.xy.length for v in body.data.vertices), 5)
    out['bounds_min'] = [round(x, 4) for x in lo]; out['bounds_max'] = [round(x, 4) for x in hi]
    out['pivot'] = list(slice_root.location)
    for m, lv in saved: m.levels = lv
    return out

# ---------------------------------------------------------------- lights, world, look
def setup_look():
    w = bpy.data.worlds.new('Studio'); scene.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0
    nt.links.new(sep.outputs[2], mr.inputs['Value'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); els = rp.color_ramp.elements
    els[0].position, els[0].color = 0.35, (0.62, 0.52, 0.48, 1)
    els[1].position, els[1].color = 0.75, (1.0, 0.96, 0.94, 1)
    nt.links.new(mr.outputs['Result'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 0.45
    def area(name, loc, energy, size, color=(1, 1, 1), target=(0.5, 0.3, 0.3)):
        ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
        o = link(bpy.data.objects.new(name, ld)); o.location = loc
        d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return o
    area('Key', (-2.6, -2.4, 3.6), 330, 2.4, (1.0, 0.97, 0.94))
    area('Fill', (3.2, -2.0, 1.6), 90, 3.0, (0.94, 0.96, 1.0))
    area('Rim', (2.6, 3.0, 1.4), 170, 1.4, (1.0, 0.95, 0.95))
    area('Top', (-0.6, -0.4, 4.2), 35, 5.0)
    # a broad, dim softbox behind: a soft highlight across the glossy top, toward its front edge
    sb = area('Softbox', (-0.4, 3.4, 3.1), 32, 4.0, (1.0, 0.98, 0.97), target=(0.5, 0.2, 0.7))
    sb.data.shape = 'RECTANGLE'; sb.data.size = 4.5; sb.data.size_y = 1.0
    sc = scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = 24 if QUICK else 110; sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = -0.25
    try: sc.view_settings.look = 'Medium High Contrast'
    except Exception: pass
    # ink outlines, like an illustration (the tiny seeds are left without)
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'
    vl = bpy.context.view_layer; fs = vl.freestyle_settings
    fs.crease_angle = math.radians(120)
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new('Ink')
    ls.select_by_visibility = True; ls.select_by_edge_types = True
    ls.select_silhouette = True; ls.select_border = True; ls.select_crease = False; ls.select_external_contour = True
    # three kinds of line: bold ink round the slice (seeds, berry and cream left out), a contour-only
    # line round the berry (no rings round its seeds and dimples), and half-weight warm lines on the cream
    def coll(name):
        c = bpy.data.collections.new(name); scene.collection.children.link(c); return c
    nol, berry_c, cream_c, leaf_c = coll('No main lines'), coll('Berry lines'), coll('Cream lines'), coll('Leaf lines')
    ls.select_by_collection = True; ls.collection = nol; ls.collection_negation = 'EXCLUSIVE'
    ls.linestyle = ls.linestyle or bpy.data.linestyles.new('Ink')
    ls.linestyle.color = INK[:3]; ls.linestyle.alpha = 1.0
    def lineset(name, c, sil, color, rel):
        l = fs.linesets.new(name)
        l.select_by_visibility = True; l.select_by_edge_types = True
        l.select_silhouette = sil; l.select_border = False; l.select_crease = False; l.select_external_contour = True
        l.select_by_collection = True; l.collection = c; l.collection_negation = 'INCLUSIVE'
        l.linestyle = bpy.data.linestyles.new(name); l.linestyle.color = color
        LINE_WEIGHTS.append((l.linestyle, rel))
    LINE_WEIGHTS.append((ls.linestyle, 1.0))
    lineset('Berry ink', berry_c, False, INK[:3], 0.8)
    lineset('Cream ink', cream_c, False, (lin('#8A5A40') if CAKE == 'strawberry' else mix_hex(SPEC['pipe'] or '#FBF0DE', SPEC['ink'], 0.55))[:3], 0.5)
    lineset('Leaf ink', leaf_c, False, lin(TOPPING.get('detail_ink', '#1E4D22'))[:3], 0.55)
    return nol, berry_c, cream_c, leaf_c

LINE_WEIGHTS = []
def set_line_weight(px):
    for style, rel in LINE_WEIGHTS: style.thickness = px * rel

NO_LINES, BERRY_LINES, CREAM_LINES, LEAF_LINES = setup_look()
# the topping and the cream get their own lines (contour only), the pattern on top none
for o in TOPPING['parts'] + ([CREAM_OBJ] if CREAM_OBJ else []) + [o for o in EXTRAS if o.name != 'Drips']: NO_LINES.objects.link(o)
# (the strawberry's seeds share the berry's outline, so one sitting on the edge carries the line instead of breaking
# it: it is external contour only, so seeds on the berry's face, with the berry behind them, get no line)
for o in TOPPING['parts']:
    grp = TOPPING['lines'].get(o.name)
    if grp == 'main': BERRY_LINES.objects.link(o)
    elif grp == 'detail': LEAF_LINES.objects.link(o)
if CREAM_OBJ: CREAM_LINES.objects.link(CREAM_OBJ)

# ---------------------------------------------------------------- tiling: a slice against rotated copies of itself
from mathutils.bvhtree import BVHTree
def world_tris(objs, rot=0.0, render_levels=True):
    saved = []
    if render_levels:
        for o in objs:
            for m in o.modifiers:
                if m.type == 'SUBSURF': saved.append((m, m.levels)); m.levels = m.render_levels
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    R_ = Matrix.Rotation(rot, 4, 'Z'); verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles()
        base = len(verts)
        verts += [R_ @ o.matrix_world @ v.co for v in me.vertices]
        polys += [tuple(base + i for i in t.vertices) for t in me.loop_triangles]
        ev.to_mesh_clear()
    for m, lv in saved: m.levels = lv
    return verts, polys

def overlap_report(objs, label):
    """Intersecting triangle pairs between the slice and copies turned 60 and 180 degrees, split into
    'visible' (both above the top of the sponge, where crossing would show as a seam) and 'buried'."""
    v0, p0 = world_tris(objs)
    t0 = BVHTree.FromPolygons(v0, p0)
    out = {}
    for deg in (60, -60, 180):
        v1, p1 = world_tris(objs, math.radians(deg))
        pairs = t0.overlap(BVHTree.FromPolygons(v1, p1))
        vis = 0
        for i, j in pairs:
            if min(v0[k].z for k in p0[i]) > H_BODY - 0.002 and min(v1[k].z for k in p1[j]) > H_BODY - 0.002: vis += 1
        out[f'{deg:+d}deg'] = {'visible_pairs': vis, 'buried_pairs': len(pairs) - vis}
    print('OVERLAP', label, json.dumps(out))
    return out

# ---------------------------------------------------------------- the game asset: one low-poly mesh, a baked atlas
# Each part of the game mesh, by its material: its id (kept in a 'part' attribute through the join), the hi-res
# objects it is baked from, a flat colour or a flat normal instead of a projected bake, and its share of texels.
# Ids: 0 the sponge (cut faces; hidden top and bottom), 5 the sponge's bare outside, 1 the coat, 2 the cream,
# 3 and 4 the topping (its main piece and its detail).
REG = {
    'Sponge': dict(part=0, src=['Sponge']),
    'Sponge hidden': dict(part=0, src=['Sponge'], uv=0.02),
    'Sponge outside': dict(part=5, src=['Sponge']),
    'Glaze': dict(part=1, src=['Glaze'] + [o.name for o in EXTRAS], **(dict(cage=0.06, ray=0.14) if EXTRAS else {})),
    'Whipped cream': dict(part=2, src=['Whipped cream'], flat_colour=True, flat_normal=True, uv=0.35),
}

def build_lod():
    parts = []
    # sponge: a closed wedge, so the outline shell has a volume to follow; only the two cut faces are
    # ever seen (the top, the outside and the bottom are covered), so those get no texture space
    hidden = MAT['sponge'].copy(); hidden.name = 'Sponge hidden'
    outside = MAT['sponge'].copy(); outside.name = 'Sponge outside'   # a bare-sided cake shows its layers outside
    bm = bmesh.new(); n_arc = 10
    ring = [Vector((0, 0))] + [Vector((math.cos(SEG * i / n_arc), math.sin(SEG * i / n_arc))) for i in range(n_arc + 1)]
    bot = [bm.verts.new((p.x, p.y, 0)) for p in ring]; top = [bm.verts.new((p.x, p.y, SPONGE_TOP)) for p in ring]
    bm.faces.new(list(reversed(bot))).material_index = 1; bm.faces.new(top).material_index = 1
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        cut = i == 0 or j == 0
        f.material_index = 0 if cut else (1 if FULL else 2); f.smooth = not cut
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for e in bm.edges: e.smooth = all(f.smooth for f in e.link_faces)
    sp = mesh_obj('Sponge LOD', bm, smooth=False)
    sp.data.materials.append(MAT['sponge']); sp.data.materials.append(hidden)
    if not FULL: sp.data.materials.append(outside)
    parts.append(sp)
    GLAZE_FLOOR[0] = 0.0                                      # reach the counter: there is no sponge outside behind it
    parts.append(build_glaze('Glaze LOD', n_edge=18, n_arc=14, caps=(), rows=[GLAZE_ROWS[i] for i in (0, 2, 4)],
                             subsurf=False, sharp_corners=True))
    GLAZE_FLOOR[0] = 0.012
    if SPEC['pipe']: parts.append(build_cream_lod())
    tl = TOP.build(SPEC, dict(TOPPING['env'], lod=True))
    REG.update(tl['reg'])
    root, bparts = tl['root'], tl['parts']
    parts += bparts
    bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
        # remember which part each point belongs to (it survives the join)
        att = o.data.attributes.new('part', 'INT', 'POINT')
        fat = o.data.attributes.new('part_face', 'INT', 'FACE')        # exact per face (a point can sit on two parts)
        for poly in o.data.polygons:
            pid_ = REG[o.data.materials[poly.material_index].name]['part']
            fat.data[poly.index].value = pid_
            for vi in poly.vertices:
                att.data[vi].value = pid_
    if root: bpy.data.objects.remove(root)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    lod = bpy.context.view_layer.objects.active
    lod.name = lod.data.name = ASSET
    # tris and quads only (end caps and cones make n-gons; tangents and engines want neither)
    bm = bmesh.new(); bm.from_mesh(lod.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    for v in bm.verts: v.co.z = max(v.co.z, 0.0)          # nothing below the plate
    bm.to_mesh(lod.data); bm.free()
    for p in lod.data.polygons:
        if lod.data.materials[p.material_index].name not in ('Sponge', 'Sponge hidden'): p.use_smooth = True
    return lod

def unwrap(lod):
    bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.context.view_layer.objects.active = lod
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01, area_weight=0.0, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    # give the topping more texels: it is small but it is what tells the cakes apart; one flat colour (the
    # cream) needs little space; what is never seen (the sponge under the coat) shrinks to a speck
    me = lod.data; uv = me.uv_layers.active.data
    scale = {i: REG[m.name].get('uv', 1.0) for i, m in enumerate(me.materials)}
    for p in me.polygons:
        k = scale[p.material_index]
        if k != 1.0:
            for li in p.loop_indices: uv[li].uv *= k
    scene.tool_settings.use_uv_select_sync = True              # mesh selection = UV selection, so the pack sees every island
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    us = [d.uv for d in lod.data.uv_layers.active.data]
    lo, hi = min(min(u.x, u.y) for u in us), max(max(u.x, u.y) for u in us)
    assert lo >= -1e-4 and hi <= 1 + 1e-4, f'UVs outside the atlas: {lo} .. {hi}'

def outline_normals(lod):
    """Smooth normals averaged over every face that meets at a point, for an inverted-hull outline:
    the flat cut faces split the shading normals, which would crack a hull at the corners."""
    me = lod.data
    acc = {}
    key = lambda co: (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    # each distinct shading normal at the point counts once: on a smooth surface that is the shading
    # normal itself; at a hard edge (flat faces, or a smooth group meeting another) it is the bisector
    dirs = {}
    for li, loop in enumerate(me.loops):
        n_ = me.corner_normals[li].vector
        lst = dirs.setdefault(key(me.vertices[loop.vertex_index].co), [])
        if not any(d.dot(n_) > 0.999 for d in lst): lst.append(n_.copy())
    for k_, lst in dirs.items():
        acc[k_] = sum(lst, Vector())
    attr = me.color_attributes.new('OutlineNormal', 'FLOAT_COLOR', 'POINT')
    part = me.attributes['part'].data
    for v in me.vertices:
        n = acc[key(v.co)].normalized()
        # alpha, the outline weight: 1 the cake gets the full shell (0.5 on the glaze lip at the counter, where
        # the averaged normal points down and out); 0.25 the cream: no shell and no ink; 0 the berry and its
        # leaves: no shell (it would poke through the cream), inked by the shader at grazing angles instead
        pv = part[v.index].value
        w_ = 1.0 if pv in (0, 5) else (0.5 if FULL and v.co.z < 0.03 else 1.0) if pv == 1 else (0.25 if pv == 2 else 0.0)
        attr.data[v.index].color = (n.x * 0.5 + 0.5, n.y * 0.5 + 0.5, n.z * 0.5 + 0.5, w_)
    # for the engine: the same normal in glTF space (x, z, -y), with the shell weight, in TEXCOORD_1 and
    # TEXCOORD_2 (the exporter writes v as 1 - v, so store 1 - value to read back the value)
    # (look layers up by name each time: adding a layer reallocates them, and an older reference can then
    # point at the wrong one)
    main = me.uv_layers.active.name
    before = [tuple(d.uv) for d in me.uv_layers[main].data]
    me.uv_layers.new(name='OutlineN_xy'); me.uv_layers.new(name='OutlineN_zw')
    xy, zw = me.uv_layers['OutlineN_xy'].data, me.uv_layers['OutlineN_zw'].data
    col = me.color_attributes['OutlineNormal'].data
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index; c = col[vi].color
            n = Vector((c[0] * 2 - 1, c[1] * 2 - 1, c[2] * 2 - 1))
            xy[li].uv = (n.x, 1 - n.z); zw[li].uv = (-n.y, 1 - c[3])
    me.uv_layers.active = me.uv_layers[main]; me.uv_layers[main].active_render = True
    assert [tuple(d.uv) for d in me.uv_layers[main].data] == before, 'the atlas UVs changed'
    assert me.uv_layers.active.name == main and me.uv_layers[main].active_render
    me.color_attributes.active_color = me.color_attributes['OutlineNormal']

def bake(lod, size=1024):
    """Bake the hi-res look into one atlas. The game mesh is split by part for the bake, and each part
    is baked only from its own hi-res part, so nothing bleeds across (no glaze pink in the cream)."""
    for m in bpy.data.materials:                             # nothing view-dependent in a bake
        if m.node_tree and 'ViewDep' in m.node_tree.nodes: m.node_tree.nodes['ViewDep'].outputs[0].default_value = 0.0
    alb = bpy.data.images.new(ASSET + '_albedo', size, size, alpha=True); alb.generated_color = (0, 0, 0, 0)
    nrm = bpy.data.images.new(ASSET + '_normal', size, size, alpha=True); nrm.colorspace_settings.name = 'Non-Color'
    nrm.generated_color = (0.5, 0.5, 1.0, 0.0)
    mat = bpy.data.materials.new(ASSET); mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes['Principled BSDF']
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = alb
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = nrm
    nm = nt.nodes.new('ShaderNodeNormalMap')
    bsdf.inputs['Roughness'].default_value = 0.45; bsdf.inputs['Coat Weight'].default_value = 0.1
    bsdf.inputs['Specular IOR Level'].default_value = 0.35
    # split by part
    bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.context.view_layer.objects.active = lod
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='MATERIAL'); bpy.ops.object.mode_set(mode='OBJECT')
    pieces = [o for o in bpy.context.selected_objects]
    jobs, flat_normal, flat_colour = [], set(), {}
    for o in pieces:
        mname = o.data.materials[o.data.polygons[0].material_index].name
        reg = REG[mname]; o['reg_name'] = mname
        src = [bpy.data.objects[nm_] for nm_ in reg['src']]
        if reg.get('flat_normal'): flat_normal.add(o)                 # its game mesh already carries the shape
        if reg.get('flat_colour'):                                     # one colour: take it from the material, so no
            flat_colour[o] = tuple(o.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)  # ray can miss
        o.data.materials.clear(); o.data.materials.append(mat)
        for p in o.data.polygons: p.material_index = 0
        jobs.append((o, src))
    sc = scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 8
    bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.02; bk.max_ray_distance = 0.06
    bk.margin = 4; bk.use_clear = False
    bk.margin_type = 'EXTEND'      # the default (adjacent faces) blends edge texels with the empty black around them
    for node, kind in ((ta, 'DIFFUSE'), (tn, 'NORMAL')):
        nt.nodes.active = node
        for o, src in jobs:
            reg = REG[o['reg_name']]
            bk.cage_extrusion = reg.get('cage', 0.02); bk.max_ray_distance = reg.get('ray', 0.06)
            bpy.ops.object.select_all(action='DESELECT')
            for x in src: x.hide_render = False; x.select_set(True)
            o.hide_render = False; o.select_set(True); bpy.context.view_layer.objects.active = o
            if kind == 'DIFFUSE' and o in flat_colour:
                fm = principled('Flat bake', flat_colour[o]); fi = fm.node_tree.nodes.new('ShaderNodeTexImage'); fi.image = alb
                fm.node_tree.nodes.active = fi; o.data.materials[0] = fm
                bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
                bk.use_selected_to_active = False; bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}); bk.use_selected_to_active = True
                o.data.materials[0] = mat; bpy.data.materials.remove(fm)
            elif kind == 'DIFFUSE': bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
            elif o in flat_normal:
                bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
                bk.use_selected_to_active = False; bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT'); bk.use_selected_to_active = True
            else: bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT')
    # back to one mesh
    bpy.ops.object.select_all(action='DESELECT')
    for o, _ in jobs: o.select_set(True)
    bpy.context.view_layer.objects.active = jobs[0][0]
    bpy.ops.object.join()
    lod = bpy.context.view_layer.objects.active; lod.name = lod.data.name = ASSET
    fill_background(alb, None); fill_background(nrm, (0.5, 0.5, 1.0))
    os.makedirs(os.path.join(OUT, 'textures'), exist_ok=True)
    for img in (alb, nrm):
        img.filepath_raw = os.path.join(OUT, 'textures', img.name + '_1024.png'); img.file_format = 'PNG'; img.save()
    for img in (alb, nrm):                                   # the game uses a 512 atlas
        img.scale(512, 512); img.filepath_raw = os.path.join(OUT, 'textures', img.name + '.png'); img.save()
    nt.links.new(ta.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    for m in bpy.data.materials:
        if m.node_tree and 'ViewDep' in m.node_tree.nodes: m.node_tree.nodes['ViewDep'].outputs[0].default_value = 1.0
    return lod, mat

def fill_background(img, colour, grow=24):
    """Fill the texels no island covers: grow the islands outward a few texels (so filtering and mips
    at island edges pick up the island's own colour), then a flat colour for the rest."""
    import numpy as np
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    filled = a[..., 3] > 0.5
    rgb = a[..., :3].copy()
    for _ in range(grow):
        acc = np.zeros_like(rgb); cnt = np.zeros((h, w), np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m = np.roll(filled, (dy, dx), (0, 1)); c = np.roll(rgb, (dy, dx), (0, 1))
            acc += c * m[..., None]; cnt += m
        new = (~filled) & (cnt > 0)
        rgb[new] = acc[new] / cnt[new][:, None]; filled = filled | new
    rest = colour if colour is not None else rgb[a[..., 3] > 0.5].mean(axis=0)
    rgb[~filled] = rest
    a[..., :3] = rgb; a[..., 3] = 1.0
    img.pixels[:] = a.ravel()

def preview_material(mat):
    """For the previews only: ink the topping at grazing angles (in Unity the slice shader does the same,
    driven by the outline colour's alpha), since the topping is left out of the outline shell."""
    m = mat.copy(); m.name = ASSET + ' preview'; nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']; base_link = bsdf.inputs['Base Color'].links[0].from_socket
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'OutlineNormal'
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.2
    rm = nt.nodes.new('ShaderNodeMapRange'); rm.inputs['From Min'].default_value = 0.62; rm.inputs['From Max'].default_value = 0.8
    nt.links.new(lw.outputs['Facing'], rm.inputs['Value'])
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'LESS_THAN'; inv.inputs[1].default_value = 0.1
    nt.links.new(at.outputs['Alpha'], inv.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    nt.links.new(rm.outputs['Result'], mul.inputs[0]); nt.links.new(inv.outputs[0], mul.inputs[1])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    nt.links.new(mul.outputs[0], mx.inputs['Factor']); nt.links.new(base_link, mx.inputs['A']); mx.inputs['B'].default_value = INK
    nt.links.new(mx.outputs['Result'], bsdf.inputs['Base Color'])
    return m

def outline_hull(lod, width=0.015):
    """The inverted-hull outline Unity will draw: the mesh pushed out along the averaged outline normals,
    faces flipped, ink on the side facing away. Cycles has no backface culling, so the near side of the
    hull is made transparent with the Backfacing output instead."""
    me = lod.data.copy(); me.name = ASSET + ' outline'
    attr = me.color_attributes['OutlineNormal']
    for v in me.vertices:
        c = attr.data[v.index].color
        v.co += Vector((c[0] * 2 - 1, c[1] * 2 - 1, c[2] * 2 - 1)).normalized() * width * (c[3] if c[3] >= 0.5 else 0.0)
    bm = bmesh.new(); bm.from_mesh(me)
    alpha = bm.verts.layers.float_color.get('OutlineNormal')
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if any(v[alpha][3] < 0.5 for v in f.verts)], context='FACES')
    bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new('Outline ink'); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); geo = nt.nodes.new('ShaderNodeNewGeometry')
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = INK; em.inputs['Strength'].default_value = 1.0
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(geo.outputs['Backfacing'], mx.inputs['Fac'])
    nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    me.materials.clear(); me.materials.append(m)
    return me

def hull_object(me, rot):
    h = link(bpy.data.objects.new('Outline', me)); h.rotation_euler = (0, 0, rot)
    h.visible_shadow = False; h.visible_diffuse = False; h.visible_glossy = False; h.visible_transmission = False
    return h

def tri_count(o):
    me = o.data; me.calc_loop_triangles(); return len(me.loop_triangles)

def seam_rays(lod, step=0.012):
    """Six copies of the game mesh as a whole cake; cast a grid of rays from the game camera's pitch at
    several headings and count the ones whose first hit is a sponge cut face (seen from outside = a gap).
    The grid is kept off the seam planes (see backface_hits): a ray exactly in one grazes the cut faces."""
    me = lod.data; me.calc_loop_triangles(); part = me.attributes['part_face'].data
    verts, polys, pid = [], [], []
    for k in range(6):
        Rk = Matrix.Rotation(SEG * k, 4, 'Z'); base = len(verts)
        verts += [Rk @ (lod.matrix_world @ v.co) for v in me.vertices]
        for t in me.loop_triangles:
            polys.append(tuple(base + i for i in t.vertices)); pid.append(part[t.polygon_index].value)
    tree = BVHTree.FromPolygons(verts, polys)
    p = math.radians(42.84); hits = leaks = 0
    for az in (0, 15, 30, 45):
        a = math.radians(az)
        d = Vector((math.sin(a) * math.cos(p), math.cos(a) * math.cos(p), -math.sin(p)))
        right = Vector((math.cos(a), -math.sin(a), 0)); up = right.cross(d).normalized()
        n = int(2.8 / step)
        for i in range(n):
            for j in range(n):
                o = right * (-1.4 + (i + 0.37) * step) + up * (-1.4 + (j + 0.37) * step) + Vector((0, 0, 0.35)) - d * 6
                loc, nor, idx, dist = tree.ray_cast(o, d, 20)
                if idx is None: continue
                hits += 1; leaks += pid[idx] == 0
    return {'rays_hitting_cake': hits, 'rays_hitting_sponge_from_outside': leaks}

def backface_hits(objs, step=0.006, label=''):
    """Rays from the game camera (12 headings) at the given objects, as one lone slice and as a whole
    cake: how many first hit a triangle facing away from the ray (which an engine culls: a hole).
    The grid is shifted 0.37 of a step so no ray runs exactly in a seam plane: such a ray grazes faces
    lying in that plane, where a ray-triangle hit is undefined (it reported points off the mesh)."""
    out = {}
    for name, copies in (('lone slice', 1), ('whole cake', 6)):
        verts, polys = [], []
        for k in range(copies):
            Rk = Matrix.Rotation(SEG * k, 4, 'Z')
            for o in objs:
                me = o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(); me.calc_loop_triangles()
                base = len(verts); mw = Rk @ o.matrix_world
                verts += [mw @ v.co for v in me.vertices]; polys += [tuple(base + i for i in t.vertices) for t in me.loop_triangles]
                o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
        tree = BVHTree.FromPolygons(verts, polys)
        p = math.radians(42.84); back = hits = graze = 0
        for az in range(0, 360, 30):
            a = math.radians(az)
            d = Vector((math.sin(a) * math.cos(p), math.cos(a) * math.cos(p), -math.sin(p)))
            right = Vector((math.cos(a), -math.sin(a), 0)); up = right.cross(d).normalized()
            n = int(2.8 / step) if copies > 1 else int(1.4 / step)
            c0 = Vector((0, 0, 0.35)) if copies > 1 else Vector((0.45, 0.28, 0.4))
            for i in range(n):
                for j in range(n):
                    o_ = c0 + right * (-n * step / 2 + (i + 0.37) * step) + up * (-n * step / 2 + (j + 0.37) * step) - d * 6
                    loc, nor, idx, dist = tree.ray_cast(o_, d, 20)
                    if idx is None: continue
                    hits += 1
                    if nor.dot(d) > 0:
                        # a hole lets neighbouring rays through too; a lone ray that slips between two triangles
                        # exactly on their shared edge (the ray caster is not watertight; a GPU is) is not a hole
                        near = 0
                        for e in (right, -right, up, -up):
                            h = tree.ray_cast(o_ + e * 0.0005, d, 20)
                            near += h[2] is not None and h[1].dot(d) > 0
                        if near >= 3: back += 1
                        else: graze += 1
        out[name] = {'rays_hitting': hits, 'first_hits_on_back_faces': back, 'lone_edge_grazes': graze}
    print('BACKFACES', label, json.dumps(out))
    return out

def green_share(image_path, cam, berry_centres, radius_px=48):
    """Share of green among red and green pixels round each berry in a render (red must dominate)."""
    import numpy as np
    from bpy_extras.object_utils import world_to_camera_view
    img = bpy.data.images.load(image_path); w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    out = []
    for c in berry_centres:
        v = world_to_camera_view(scene, cam, c); cx, cy = int(v.x * w), int(v.y * h)
        ys, xs = np.mgrid[max(0, cy - radius_px):min(h, cy + radius_px), max(0, cx - radius_px):min(w, cx + radius_px)]
        m = (xs - cx) ** 2 + (ys - cy) ** 2 <= radius_px ** 2
        px = a[ys[m], xs[m], :3]
        r, g, b = px[:, 0], px[:, 1], px[:, 2]
        red = (r > 0.3) & (g < 0.35 * r) & (b < 0.45 * r)
        green = (g > 1.15 * r) & (g > 1.1 * b) & (g > 0.15)
        out.append(round(float(green.sum()) / max(1, int(red.sum() + green.sum())), 2))
    bpy.data.images.remove(img)
    return out

def unity_decode_check(path):
    """Read the GLB the way glTFast / UnityGLTF bring it into Unity (X negated on positions and normals,
    v flipped on every texture coordinate set) and check the decoding documented in the README:
    outline normal = normalize(-uv1.x, 1 - uv1.y, uv2.x), weight = 1 - uv2.y."""
    import struct
    data = open(path, 'rb').read()
    jl = struct.unpack_from('<I', data, 12)[0]; js = json.loads(data[20:20 + jl])
    bin_ = data[20 + jl + 8:]
    def acc(i):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
        n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); stride = bv.get('byteStride', 4 * n)
        return [struct.unpack_from('<' + 'f' * n, bin_, off + k * stride) for k in range(a['count'])]
    prim = js['meshes'][0]['primitives'][0]['attributes']
    N = acc(prim['NORMAL']); U1 = acc(prim['TEXCOORD_1']); U2 = acc(prim['TEXCOORD_2']); U0 = acc(prim['TEXCOORD_0'])
    P_ = acc(prim['POSITION']); normals_at = {}
    for pp, n in zip(P_, N):
        normals_at.setdefault(tuple(round(x, 4) for x in pp), set()).add(tuple(round(x, 2) for x in n))
    good = tot = 0; worst = 1.0; weights = {}; hard = 0; hard_worst = 1.0
    for pp, n, u1, u2 in zip(P_, N, U1, U2):
        un = Vector((-n[0], n[1], n[2]))                      # Unity normal
        uv1 = (u1[0], 1 - u1[1]); uv2 = (u2[0], 1 - u2[1])   # Unity's v flip
        on = Vector((-uv1[0], 1 - uv1[1], uv2[0])).normalized(); wgt = round(1 - uv2[1], 2)
        weights[wgt] = weights.get(wgt, 0) + 1
        if wgt >= 0.5:
            d = on.dot(un)
            if len(normals_at[tuple(round(x, 4) for x in pp)]) > 1:   # a hard edge: the shell normal is the bisector
                hard += 1; hard_worst = min(hard_worst, d); continue
            tot += 1; good += d > 0.5; worst = min(worst, d)
    return {'smooth_vertices_with_shell': tot, 'dot_over_0.5': good, 'worst_dot': round(worst, 3),
            'hard_edge_vertices': hard, 'hard_edge_worst_dot': round(hard_worst, 3),
            'weights_found': {str(k): v for k, v in sorted(weights.items())},
            # the atlas set must be TEXCOORD_0, inside the atlas, and not the outline set
            'texcoord0_range': [round(min(min(u) for u in U0), 3), round(max(max(u) for u in U0), 3)],
            'texcoord0_same_as_texcoord1': sum(1 for a_, b_ in zip(U0, U1) if abs(a_[0] - b_[0]) < 1e-5 and abs(a_[1] - b_[1]) < 1e-5)}

def bake_check(o, imgs):
    """Sample the textures on the topping triangles that face the game camera: how many normal texels
    are bent past tangent z 0.3, and how many cream texels came out red or pink."""
    import numpy as np
    alb = next(i for i in imgs if 'albedo' in i.name); nrm = next(i for i in imgs if 'normal' in i.name)
    def arr(img):
        w, h = img.size; return np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4), w, h
    A, wa, ha = arr(alb); Nn, wn, hn = arr(nrm)
    me = o.data; me.calc_loop_triangles(); uv = me.uv_layers[0].data
    pitch = math.radians(42.84); view = Vector((0, -math.cos(pitch), math.sin(pitch)))   # toward the camera (Z-up)
    top = H_TOP + 0.02
    bent = cnt = red = creams = 0
    for t in me.loop_triangles:
        cz = sum((o.matrix_world @ me.vertices[v].co).z for v in t.vertices) / 3
        if cz < top: continue
        nw = (o.matrix_world.to_3x3() @ t.normal).normalized()
        if max(nw.dot(Matrix.Rotation(math.radians(a), 3, 'Z') @ view) for a in range(0, 360, 60)) < 0.15: continue
        us = [uv[li].uv for li in t.loops]
        for b0, b1 in ((1/3, 1/3), (0.6, 0.2), (0.2, 0.6), (0.2, 0.2)):
            u = us[0] * b0 + us[1] * b1 + us[2] * (1 - b0 - b1)
            x, y = min(wn - 1, max(0, int(u.x * wn))), min(hn - 1, max(0, int(u.y * hn)))
            nz = Nn[y, x, 2] * 2 - 1; cnt += 1; bent += nz < 0.3
            x, y = min(wa - 1, max(0, int(u.x * wa))), min(ha - 1, max(0, int(u.y * ha)))
            r, g, b = A[y, x, :3]
            # glaze pink on the topping is bleed (cream is light, the berry deep red, the leaves green)
            if r > 0.8 and 0.42 < g < 0.72 and b > 0.5: red += 1
    return {'topping_texels_sampled': cnt, 'bent_normals_pct': round(100 * bent / max(1, cnt), 2),
            'glaze_pink_on_topping': red if CAKE == 'strawberry' else None}

def verify_glb(path):
    """Re-import the exported file into an empty scene and check what Unity will get."""
    tmp = bpy.data.scenes.new('Verify')
    before = set(bpy.data.objects)
    win = bpy.context.window
    if win: win.scene = tmp
    try:
        bpy.ops.import_scene.gltf(filepath=path)
    finally:
        if win: win.scene = scene
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    rep = {'meshes': len(objs)}
    o = objs[0]; me = o.data; me.calc_loop_triangles()
    rep['triangles'] = len(me.loop_triangles)
    rep['origin'] = [round(x, 5) for x in o.matrix_world.translation]
    ws = [o.matrix_world @ v.co for v in me.vertices]
    rep['bounds_min'] = [round(min(w[i] for w in ws), 4) for i in range(3)]
    rep['bounds_max'] = [round(max(w[i] for w in ws), 4) for i in range(3)]
    angs = [math.degrees(math.atan2(w.y, w.x)) for w in ws if w.xy.length > 1e-4 and w.z > H_BODY]
    rep['angle_span_above_sponge_deg'] = [round(min(angs), 3), round(max(angs), 3)]
    rep['materials'] = [m.name for m in me.materials]
    rep['uv_layers'] = len(me.uv_layers); rep['color_attributes'] = [a.name for a in me.color_attributes]
    rep['double_sided'] = [not m.use_backface_culling for m in me.materials]
    # decode the outline normal from TEXCOORD_1/2 (glTF space) and compare with the shading normal in glTF space
    if len(me.uv_layers) >= 3:
        xy, zw = me.uv_layers[1].data, me.uv_layers[2].data
        good = tot = 0; worst = 1.0
        cn = me.corner_normals if hasattr(me, 'corner_normals') else None
        for poly in me.polygons:
            if not poly.use_smooth: continue
            for li in poly.loop_indices:
                w_ = 1 - zw[li].uv.y
                if w_ < 0.5: continue                         # the topping has no shell
                on = Vector((xy[li].uv.x, 1 - xy[li].uv.y, zw[li].uv.x)).normalized()
                bn = (cn[li].vector if cn else me.loops[li].normal)
                gn = Vector((bn.x, bn.z, -bn.y))
                d = on.dot(gn); tot += 1; good += d > 0.5; worst = min(worst, d)
        rep['outline_vs_normal'] = {'smooth_corners_checked': tot, 'dot_over_0.5': good, 'worst_dot': round(worst, 3)}
    imgs = [n.image for m in me.materials for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    rep['textures'] = [[i.name, list(i.size)] for i in imgs]
    rep['bake_check'] = bake_check(o, imgs)
    for ob in objs: bpy.data.objects.remove(ob)
    bpy.data.scenes.remove(tmp)
    return rep

def write_readme(st):
    g = st['glb_check']; u = st['unity_decode']
    top = TOPPING.get('readme', '')
    lines = [
        f"| Visible overlaps with neighbours (hi-res / game) | {[v['visible_pairs'] for v in st['overlap_hires'].values()]} / {[v['visible_pairs'] for v in st['overlap_lod'].values()]} |",
        f"| Rays reaching sponge cut faces from outside (whole cake) | {st['seam_rays']['rays_hitting_sponge_from_outside']} of {st['seam_rays']['rays_hitting_cake']:,} |",
        f"| First hits on back faces (game mesh: lone slice / whole cake; 12 headings, a ray every 0.006, grid kept off the seam planes) | {st['backfaces_lod']['lone slice']['first_hits_on_back_faces']} of {st['backfaces_lod']['lone slice']['rays_hitting']:,} / {st['backfaces_lod']['whole cake']['first_hits_on_back_faces']} of {st['backfaces_lod']['whole cake']['rays_hitting']:,} |",
        f"| Topping normals bent past tangent z 0.3 | {g['bake_check']['bent_normals_pct']}% of {g['bake_check']['topping_texels_sampled']} samples |",
    ]
    if CAKE == 'strawberry':
        lines += [f"| Glaze pink baked onto the topping | {g['bake_check']['glaze_pink_on_topping']} samples |",
                  f"| Green share round each berry, slots 0-5 | {st['green_share_by_slot']} |"]
    lip_note = "; 0.5: the coat's lip at the counter (where the normal points down and out)" if FULL else ''
    side = {'full': 'frosted all the way down the outside', 'naked': 'bare-sided (its layers show outside) under a glaze that drips down',
            'cap': 'bare-sided (its layers show outside) under a thick cream top'}[COAT['style']]
    txt = f"""# {TITLE} slice (Cake Sort)

The game asset for the {TITLE} cake's slice: {side}. Built by `../cake_slice.py` in Blender 4.2 and checked
by the same script; everything here is generated. Rebuild with (from `playbox/art/cake-sort/`):

    blender -b -P cake_slice.py -- --cake {CAKE} --out {CAKE} --glb --views hero,game,single,lodviews

## Files

| File | What it is |
| --- | --- |
| `{CAKE}_slice.glb` | The game mesh: one mesh, one material, {g['triangles']} triangles, 512 albedo + normal atlas (embedded) |
| `textures/{ASSET}_albedo.png`, `{ASSET}_normal.png` | The same atlas as loose files (512); `*_1024.png` are the bake masters |
| `renders/hero.png`, `game_cake.png`, `game_single.png` | The hi-res model (render only, about {st['tris_render']:,} triangles) |
| `renders/lod_game_cake.png`, `lod_game_single.png` | The GLB as the game camera sees it, with the outline drawn by an inverted hull |
| `renders/*_alpha_0001.png` | Each render again on a transparent background (for UI art) |
| `stats.json` | Every check's numbers from the last build |

The build also saves `{CAKE}_slice.blend` (both versions, lights and cameras) next to these; it is not kept in the
repository, since the script rebuilds it.

## Units and orientation

- Radius 1, pivot at the cake's centre (the slice's point). Height 0.71 (the game camera is pitched 42.84
  degrees down, so it shows as 0.52 R on screen); the topping reaches {g['bounds_max'][2]}.
- In Blender the slice spans 0..60 degrees from +X toward +Y. The GLB is +Y up: the slice lies in the
  XZ plane from +X toward -Z. glTFast and UnityGLTF negate X, so in Unity it runs from -X toward -Z.
  Slot k of a plate is the slice turned 60 k degrees about Y.
- Six slices tile a whole cake: no visible overlap with copies at +60/-60/180 degrees, and no ray from
  the game camera reaches a sponge cut face from outside (see Checks).

## Material

One material: base colour and tangent-space normal from the atlas, roughness 0.45, single-sided
(backface culling on). Sponge faces that are always covered get no texture space. The material also carries
Blender's clearcoat and specular values (KHR_materials_clearcoat, KHR_materials_specular); URP ignores them,
and the slice's look comes from the toon slice shader, not from these.{top}

## The outline (an inverted hull, in the slice shader's outline pass)

Ink colour for this cake: `{SPEC['ink']}`. Smooth normals for the shell are stored in the second and third
texture-coordinate sets, because the cut faces split the shading normals and a hull built from them would
crack at the corners.

In Unity, after glTFast or UnityGLTF (both negate X on positions and normals and flip v on every
texture-coordinate set):

    outlineNormal = normalize(float3(-uv1.x, 1 - uv1.y, uv2.x))   // object space
    weight        = 1 - uv2.y
    // shell: cull front faces, colour {SPEC['ink']}, and push each vertex out by a fixed number of screen
    // pixels, so the line keeps its weight at every plate size (in object units it would vanish: at the
    // counter a plate is about 76 px across at 2x, R about 29 px, so 0.015 R is under half a pixel):
    float4 pos = TransformObjectToHClip(positionOS);
    float3 nWS = TransformObjectToWorldDir(outlineNormal);
    float2 nCS = SafeNormalize(float3(mul((float3x3)UNITY_MATRIX_VP, nWS).xy, 0)).xy;   // no NaN facing the camera
    float  px  = _OutlinePx * weight * step(0.5, weight);        // _OutlinePx about 2.5 at 2x, 1.5 at 1x
    pos.xy    += nCS * (2.0 * px / _ScreenParams.xy) * pos.w;
    // (if it must stay in object units, use about 0.09 R at the 76 px plate.) The previews here draw
    // the shell in object units, 0.015 R, which is about 4 px at their 900 px scale.
    // weight 1: the cake{lip_note}
    // weight 0.25: piped cream: no shell, no ink
    // weight 0: the topping: no shell (it would poke through what it sits on); instead ink the
    //           surface at grazing angles: lerp(albedo, ink, smoothstep(0.62, 0.8, facing)),
    //           facing = 1 - pow(|dot(N, V)|, 0.4) (Blender's Layer Weight 'Facing', blend 0.2; N unbumped)

As written in the file (glTF space, before any importer): TEXCOORD_1 = (nx, ny), TEXCOORD_2 =
(nz, weight). A check that reads the GLB the way those importers do and applies the formula above
finds {u['dot_over_0.5']} of {u['smooth_vertices_with_shell']} smooth shell vertices with dot(outline normal,
normal) over 0.5 (worst {u['worst_dot']}); at hard edges ({u['hard_edge_vertices']} vertices) the shell normal is the
bisector of the faces that meet there (worst dot {u['hard_edge_worst_dot']}); weights found: {u['weights_found']}.
TEXCOORD_0 (the atlas) spans {u['texcoord0_range']} and never equals TEXCOORD_1.

## Checks (from the last build)

| Check | Result |
| --- | --- |
| GLB re-imported | {g['meshes']} mesh, {g['triangles']} triangles, origin {g['origin']}, materials {len(g['materials'])}, double-sided {g['double_sided']}, vertex colours {g['color_attributes'] or 'none'} |
| Top of the cake stays in the wedge | {g['angle_span_above_sponge_deg']} degrees |
""" + '\n'.join(lines) + '\n'
    with open(os.path.join(OUT, 'README.md'), 'w') as f: f.write(txt)

# ---------------------------------------------------------------- cameras and views
def camera(name, loc, target, ortho=None, lens=70):
    cd = bpy.data.cameras.new(name)
    if ortho: cd.type = 'ORTHO'; cd.ortho_scale = ortho
    else: cd.lens = lens
    o = link(bpy.data.objects.new(name, cd)); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

scene.use_nodes = True
ctree = scene.node_tree
for nd in list(ctree.nodes): ctree.nodes.remove(nd)
rl = ctree.nodes.new('CompositorNodeRLayers')
ao = ctree.nodes.new('CompositorNodeAlphaOver'); ao.inputs[1].default_value = (1.0, 0.92, 0.86, 1)   # warm paper (linear)
comp = ctree.nodes.new('CompositorNodeComposite')
RENDERS = os.path.join(OUT, 'renders'); os.makedirs(RENDERS, exist_ok=True)
fo = ctree.nodes.new('CompositorNodeOutputFile'); fo.base_path = RENDERS; fo.format.color_mode = 'RGBA'
ctree.links.new(rl.outputs['Image'], ao.inputs[2]); ctree.links.new(ao.outputs['Image'], comp.inputs['Image'])
ctree.links.new(rl.outputs['Image'], fo.inputs[0])

def render(cam, path, w, h):
    scene.camera = cam; scene.render.resolution_x = w; scene.render.resolution_y = h
    scene.render.resolution_percentage = 100
    scene.render.filepath = path
    fo.file_slots[0].path = os.path.splitext(os.path.basename(path))[0] + '_alpha_'
    bpy.ops.render.render(write_still=True)

extra = []
GREEN = {}
def show_only(objs):
    for o in scene.objects:
        if o.type in ('MESH', 'EMPTY', 'CURVE') and o.name != 'Star nozzle':
            o.hide_render = o not in objs
    for o in extra: o.hide_render = o not in objs

slice_objs = PARTS + [slice_root] + ([TOPPING['root']] if TOPPING['root'] else [])

if 'hero' in VIEWS:
    # like the reference: point to the left, a cut face toward us, the outside on the right
    show_only(slice_objs)
    tgt = (0.52, 0.3, 0.42)
    az, el, dist = math.radians(-74), math.radians(31), 4.2
    cam = camera('Hero', (tgt[0] + dist * math.cos(el) * math.cos(az), tgt[1] + dist * math.cos(el) * math.sin(az), tgt[2] + dist * math.sin(el)), tgt, lens=78)
    set_line_weight(5.2)
    render(cam, os.path.join(RENDERS, 'hero.png'), 1200, 1000)

if 'game' in VIEWS or 'single' in VIEWS:
    # the game camera: orthographic, pitched 42.84 degrees down, looking along +Y
    pitch = math.radians(42.84)
    def game_cam(name, target, scale):
        d = Vector((0, math.cos(pitch), -math.sin(pitch)))
        return camera(name, Vector(target) - d * 10, target, ortho=scale)
    if 'game' in VIEWS:
        # a whole cake of six on a plate, as it sits on the counter
        copies = []
        for k in range(1, 6):
            for o in [slice_root]:
                pass
        dup_root = []
        for k in range(1, 6):
            inst = bpy.data.objects.new(f'Slice {k}', None)
            inst.instance_type = 'COLLECTION'; inst.instance_collection = slice_coll
            inst.rotation_euler = (0, 0, SEG * k)
            link(inst); dup_root.append(inst)
        pbm = bmesh.new()
        bmesh.ops.create_cone(pbm, cap_ends=True, segments=96, radius1=1.22, radius2=1.3, depth=0.06, matrix=Matrix.Translation((0, 0, -0.03)))
        plate = mesh_obj('Plate', pbm); plate.data.materials.append(MAT['plate'])
        rbm = bmesh.new()
        bmesh.ops.create_circle(rbm, cap_ends=False, segments=96, radius=1.16, matrix=Matrix.Translation((0, 0, 0.0015)))
        rim = mesh_obj('Plate rim', rbm, smooth=False)
        sk = rim.modifiers.new('Line', 'SKIN')
        for v in rim.data.skin_vertices[0].data: v.radius = (0.022, 0.003)
        rim.data.materials.append(MAT['plate_rim'])
        extra.extend(dup_root + [plate, rim])
        show_only(slice_objs + dup_root + [plate, rim])
        set_line_weight(3.4)
        gc = game_cam('Game', (0, 0, 0.3), 3.1)
        render(gc, os.path.join(RENDERS, 'game_cake.png'), 900, 760)
        BERRY_SLOTS = [Matrix.Rotation(SEG * k, 3, 'Z') @ (TOP_SPOT + Vector((0, 0, 0.13))) for k in range(6)]
        if CAKE == 'strawberry': GREEN['hi-res game_cake'] = green_share(os.path.join(RENDERS, 'game_cake.png'), gc, BERRY_SLOTS)
    if 'single' in VIEWS:
        show_only(slice_objs)
        slice_root.rotation_euler = (0, 0, math.radians(-22))      # a slice on its own, a cut face to the camera
        set_line_weight(3.4)
        render(game_cam('Game single', (0.5, 0.05, 0.4), 1.75), os.path.join(RENDERS, 'game_single.png'), 760, 640)
        slice_root.rotation_euler = (0, 0, 0)

st = stats()
st['green_share_by_slot'] = GREEN; print('GREEN', json.dumps(GREEN))
with open(os.path.join(OUT, 'stats.json'), 'w') as f: json.dump(st, f, indent=1)
print('STATS', json.dumps(st))
st['overlap_hires'] = overlap_report(PARTS, 'hi-res')
st['backfaces_hires'] = backface_hits(TOPPING['parts'] + ([CREAM_OBJ] if CREAM_OBJ else []), step=0.01, label='hi-res topping')
if '--glb' in argv:
    lod = build_lod()
    unwrap(lod)
    st['overlap_lod'] = overlap_report([lod], 'lod')
    lod, lod_mat = bake(lod)
    outline_normals(lod)
    st['seam_rays'] = seam_rays(lod)
    print('SEAMS', json.dumps(st['seam_rays']))
    st['lod_triangles'] = tri_count(lod)
    assert st['lod_triangles'] <= 1200, f"game mesh over budget: {st['lod_triangles']} triangles (1,200)"
    bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.context.view_layer.objects.active = lod
    glb = os.path.join(OUT, CAKE + '_slice.glb')
    lod_mat.use_backface_culling = True                      # single-sided in the engine
    kw = dict(filepath=glb, use_selection=True, export_apply=True, export_yup=True, export_tangents=True, export_image_format='AUTO')
    try: bpy.ops.export_scene.gltf(export_vertex_color='NONE', **kw)
    except TypeError: bpy.ops.export_scene.gltf(export_colors=False, **kw)
    st['glb_bytes'] = os.path.getsize(glb)
    st['glb_check'] = verify_glb(glb)
    st['unity_decode'] = unity_decode_check(glb)
    print('UNITY', json.dumps(st['unity_decode']))
    st['backfaces_lod'] = backface_hits([lod], label='lod')
    print('GLB', json.dumps(st['glb_check']))
    extra.append(lod); lod.hide_render = True
    # previews of the game asset itself, from the game camera
    if 'lodviews' in VIEWS:
        pitch = math.radians(42.84)
        def gcam(name, target, sc_):
            d = Vector((0, math.cos(pitch), -math.sin(pitch)))
            return camera(name, Vector(target) - d * 10, target, ortho=sc_)
        hull_me = outline_hull(lod)
        prev_mat = preview_material(lod_mat); lod.data.materials[0] = prev_mat
        insts, hulls = [], [hull_object(hull_me, 0.0)]
        for k in range(1, 6):
            ob = bpy.data.objects.new(f'LOD {k}', lod.data); ob.rotation_euler = (0, 0, SEG * k); link(ob); insts.append(ob)
            hulls.append(hull_object(hull_me, SEG * k))
        extra.extend(insts + hulls)
        plate_objs = [o for o in scene.objects if o.name in ('Plate', 'Plate rim')]
        scene.render.use_freestyle = False                      # the outline here is the hull, as in Unity
        show_only([lod] + insts + hulls + plate_objs)
        lc = gcam('LOD cake cam', (0, 0, 0.3), 3.1)
        render(lc, os.path.join(RENDERS, 'lod_game_cake.png'), 900, 760)
        if CAKE == 'strawberry': GREEN['game asset lod_game_cake'] = green_share(os.path.join(RENDERS, 'lod_game_cake.png'), lc,
            [Matrix.Rotation(SEG * k, 3, 'Z') @ (TOP_SPOT + Vector((0, 0, 0.13))) for k in range(6)])
        st['green_share_by_slot'] = GREEN; print('GREEN', json.dumps(GREEN))
        show_only([lod, hulls[0]]); lod.rotation_euler = hulls[0].rotation_euler = (0, 0, math.radians(-22))
        render(gcam('LOD single cam', (0.5, 0.05, 0.4), 1.75), os.path.join(RENDERS, 'lod_game_single.png'), 760, 640)
        lod.rotation_euler = hulls[0].rotation_euler = (0, 0, 0)
        scene.render.use_freestyle = True
        lod.data.materials[0] = lod_mat
    with open(os.path.join(OUT, 'stats.json'), 'w') as f: json.dump(st, f, indent=1)
    write_readme(st)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, CAKE + '_slice.blend'))
print('DONE')
