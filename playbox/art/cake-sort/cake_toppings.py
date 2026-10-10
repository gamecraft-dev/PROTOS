# Cake Sort slices: the toppings and the patterns on top, hi-res and game (LOD) versions.
#
# build(spec, env) returns, for the topping named in the spec:
#   root    an empty the topping's pieces hang from (or None)
#   parts   its mesh objects
#   lines   hi-res: object name -> 'main' (the topping's ink outline) or 'detail' (a thinner coloured line)
#   reg     game mesh: material name -> dict(part=3|4, src=[hi-res objects it is baked from], flat_normal,
#           flat_colour, uv=its share of texels)
# env: top_z (the coat's top under the topping), coat_tree (a BVH of the coat, to sit things on it),
# piped (whether a cream rosette is under the topping), lod (build the game version).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree
from cake_common import *

_MATS = {}
def _once(name, make):
    if name not in _MATS: _MATS[name] = make()
    return _MATS[name]

def _root(name, loc, rot=None):
    r = link(bpy.data.objects.new(name, None)); r.location = loc
    if rot is not None:
        r.rotation_mode = 'QUATERNION'; r.rotation_quaternion = rot
    return r

def _hang(objs, root):
    for o in objs:
        if o: o.parent = root

def revolve(prof, n, name, close_bottom=True, close_top=True, twist=0.0, around=None):
    """A surface of revolution about z: prof is [(r, z), ...] from the bottom to the top. A ring with r == 0
    becomes a single pole. around(a, r, z) may return a radius change for shaping (ridges, flats)."""
    bm = bmesh.new(); rings = []
    for k, (r, z) in enumerate(prof):
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))]); continue
        row = []
        for i in range(n):
            a = i / n * math.tau + twist * k
            rr = r + (around(a, r, z) if around else 0.0)
            row.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z)))
        rings.append(row)
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        if len(A) == 1 and len(B) == 1: continue
        if len(A) == 1:
            for i in range(n): bm.faces.new((A[0], B[i], B[(i + 1) % n]))
        elif len(B) == 1:
            for i in range(n): bm.faces.new((A[i], A[(i + 1) % n], B[0]))
        else:
            for i in range(n): bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]))
    if close_bottom and len(rings[0]) > 1: bm.faces.new(list(reversed(rings[0])))
    if close_top and len(rings[-1]) > 1: bm.faces.new(rings[-1])
    closed_outward(bm)
    return bm

def rounded_box(sx, sy, sz, bevel, segs):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1)))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segs, profile=0.5, affect='EDGES', clamp_overlap=True)
    closed_outward(bm)
    return bm

def _sharp_all(obj):
    for e in obj.data.edges: e.use_edge_sharp = True

def _sharp_by_angle(obj, deg=50):
    """Hard edges where faces meet at more than deg (the game mesh is smooth-shaded otherwise)."""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    lim = math.radians(deg); sharp = set()
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim: sharp.add(e.index)
    bm.free()
    for e in obj.data.edges:
        if e.index in sharp: e.use_edge_sharp = True

def _lay_on(root, objs, top_z, sink, env=None):
    """Move the root down (or up) so the lowest point of its pieces sits `sink` into the surface at top_z. The game
    version takes the hi-res one's height, so the two coincide for the bake."""
    if env is not None and env.get('lod') and 'lay_z' in env:
        root.location.z = env['lay_z']; return
    bpy.context.view_layer.update()
    lo = min((o.matrix_world @ v.co).z for o in objs for v in o.data.vertices)
    root.location.z += (top_z - sink) - lo
    if env is not None and not env.get('lod'): env['lay_z'] = root.location.z

ROSETTE_REST = TOP_SPOT.z + 0.145          # where something sits in the top of the piped rosette

# ================================================================ the strawberry (the reference slice)
BERRY_TILT, BERRY_TURN = math.radians(50), math.radians(-14)

def _berry_materials():
    def berry():
        m = principled('Strawberry', '#E2213B', rough=0.24, coat=0.75, coat_rough=0.04, sss=0.25, sss_radius=(1, .2, .2), sss_scale=0.015)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc = t.node('ShaderNodeTexCoord'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Object'], sep.inputs[0])
        col = t.ramp(sep.outputs[2], [(0.0, lin('#B8152E')), (0.3, lin('#DA1F38')), (0.7, lin('#E8283F')), (1.0, lin('#F0505A'))])
        t.link(col, bsdf.inputs['Base Color'])
        return m
    def leaf():
        m = principled('Leaf', '#4FAE3A', rough=0.4, coat=0.25, sss=0.15, sss_radius=(.4, 1, .3), sss_scale=0.01)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc = t.node('ShaderNodeTexCoord'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(tc.outputs['Normal'], sep.inputs[0])
        t.link(t.ramp(sep.outputs[2], [(0.3, lin('#2E7A2A')), (0.6, lin('#4FAE3A'))]), bsdf.inputs['Base Color'])
        return m
    return (_once('Strawberry', berry), _once('Seed', lambda: principled('Seed', '#F5E39A', rough=0.35, coat=0.3)),
            _once('Leaf', leaf))

def berry_pose(S):
    psi = SEG / 2 + BERRY_TURN                    # the leaves lean out toward the rim, the point dips into the swirl
    d = Vector((math.cos(psi) * math.sin(BERRY_TILT), math.sin(psi) * math.sin(BERRY_TILT), math.cos(BERRY_TILT)))
    centre = TOP_SPOT + Vector((0, 0, 0.13))
    return centre - d * 0.5 * S, d.to_track_quat('Z', 'Y')

def berry_shape(u, v):
    """unit point on the berry: u around (0..1), v from the tip (0) to the top (1)."""
    a = u * math.tau
    # a plump cone with a soft point, widest at the shoulders, then a rounded top: 1.3x taller than wide
    if v <= 0.74:
        prof = (v / 0.74 * 0.96 + 0.04) ** 0.6
    else:
        prof = math.sqrt(max(0.0, 1 - ((v - 0.74) / 0.26) ** 2)) ** 0.85
    prof *= 1 + 0.035 * math.sin(a * 3 + v * 4)              # not a perfect solid of revolution
    return Vector((math.cos(a) * prof * 0.385, math.sin(a) * prof * 0.385, v))

def strawberry(spec, env):
    lod = env['lod']
    MB, MS, ML = _berry_materials()
    S = 0.31                                                 # berry height
    nu, nv = (10, 6) if lod else (48, 34)
    seeds = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(64):                                      # seeds on a sunflower spiral, none near the leaves
        v = 0.09 + 0.84 * (i + 0.5) / 64
        u = (i * golden / math.tau) % 1
        seeds.append((u, v))
    def dimple(u, v):
        d = 0.0
        for su, sv in seeds:
            du = min(abs(u - su), 1 - abs(u - su)) * 2.2
            dd = (du * du + (v - sv) ** 2 * 4) / 0.0028
            if dd < 9: d = max(d, math.exp(-dd))
        return d
    bm = bmesh.new()
    tip = bm.verts.new(berry_shape(0, 0) * S)
    top = bm.verts.new(berry_shape(0, 1) * S)
    rings = []
    for j in range(1, nv):
        v = j / nv; row = []
        for i in range(nu):
            u = i / nu
            p = berry_shape(u, v)
            n = Vector((p.x, p.y, 0)).normalized()
            p -= n * 0.022 * dimple(u, v)
            row.append(bm.verts.new(p * S))
        rings.append(row)
    for i in range(nu):
        k = (i + 1) % nu
        bm.faces.new((tip, rings[0][k], rings[0][i]))
        bm.faces.new((top, rings[-1][i], rings[-1][k]))
    for j in range(len(rings) - 1):
        for i in range(nu):
            k = (i + 1) % nu
            bm.faces.new((rings[j][i], rings[j][k], rings[j + 1][k], rings[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    surf = BVHTree.FromBMesh(bm) if lod else None
    sfx = ' LOD' if lod else ''
    berry = mesh_obj('Strawberry' + sfx, bm)
    berry.data.materials.append(MB)
    if not lod:
        sub = berry.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    # seeds, each sitting in its dimple and pointing along the surface
    sbm = bmesh.new()
    for su, sv in seeds:
        p = berry_shape(su, sv) * S
        n = Vector((p.x, p.y, 0.25 * (0.5 - sv))).normalized()
        q = n.to_track_quat('Z', 'Y')
        # sunk to the floor of its dimple: as big to the eye, but it barely stands proud of the outline
        m = Matrix.Translation(p - n * S * 0.03) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((S * 0.018, S * 0.018, S * 0.034, 1))
        bmesh.ops.create_uvsphere(sbm, u_segments=8, v_segments=5, radius=1.0, matrix=m)
    seeds_obj = mesh_obj('Seeds' + sfx, sbm)
    seeds_obj.data.materials.append(MS)
    if lod:                                                  # the seeds go into the baked texture
        bpy.data.objects.remove(seeds_obj); seeds_obj = None
    # the calyx: six leaf-shaped sepals (about half the berry's width long, 35% as wide as long) lying in a
    # star over the shoulders, so seen end-on the berry is a green star on red, and a short stalk
    def top_z(r):                                            # the berry's surface height at radius r (units of S)
        p = r / 0.385
        if p <= 1: return 0.74 + 0.26 * math.sqrt(max(0.0, 1 - (p ** (1 / 0.85)) ** 2))
        return 0.74 - (r - 0.385) * 1.6
    lbm = bmesh.new()
    nl = 6
    for k in range(nl):
        ang = k / nl * math.tau + 0.3
        L = 0.2 + 0.02 * math.sin(k * 2.7)                    # about a quarter of the berry's width
        Wm = L * (0.3 if lod else 0.22)                       # the game leaf tucks its edges in: start it wider
        prev = None
        segs = 3 if lod else 10
        for st in range(segs + 1):
            t = st / segs
            w = Wm * math.sin(math.pi * min(1.0, t ** 0.7)) ** 0.6 + 0.004
            r = 0.02 + L * t
            z = top_z(r) + 0.012
            c = Vector((math.cos(ang) * r, math.sin(ang) * r, z)) * S
            side = Vector((-math.sin(ang), math.cos(ang), 0)) * w * S
            lift = Vector((0, 0, 0.012 * S))                      # the edges curl up a little
            pts = [c - side + lift, c, c + side + lift]
            if lod:
                # the game berry is faceted and sits lower than the smooth one: lie on its real surface, the
                # midrib raised and the edges tucked under it, so the berry itself closes the leaf's underside
                for q in pts:
                    hit = surf.ray_cast(Vector((q.x, q.y, 2 * S)), Vector((0, 0, -1)))[0]
                    assert hit is not None
                    q.z = hit.z + (0.012 if q is pts[1] and 0 < st < segs else -0.003) * S
            row = tuple(lbm.verts.new(q) for q in pts)
            if prev:
                lbm.faces.new((prev[0], row[0], row[1], prev[1]))
                lbm.faces.new((prev[1], row[1], row[2], prev[2]))
            prev = row
    sepal_faces = list(lbm.faces)
    sbm2 = bmesh.new()                                        # the stalk, closed, normals out
    bmesh.ops.create_cone(sbm2, cap_ends=True, segments=5 if lod else 10, radius1=S * 0.03, radius2=S * 0.022, depth=S * 0.12,
                          matrix=Matrix.Translation((S * 0.012, 0, S * 1.05)) @ Matrix.Rotation(0.25, 4, 'Y'))
    bmesh.ops.recalc_face_normals(sbm2, faces=sbm2.faces)
    cen = sum((v.co for v in sbm2.verts), Vector()) / len(sbm2.verts)
    if sum(f.normal.dot(f.calc_center_median() - cen) for f in sbm2.faces) < 0: bmesh.ops.reverse_faces(sbm2, faces=sbm2.faces)
    tmp_me = bpy.data.meshes.new('stalk'); sbm2.to_mesh(tmp_me); sbm2.free(); lbm.from_mesh(tmp_me); bpy.data.meshes.remove(tmp_me)
    sep = sepal_faces
    lbm.normal_update()
    for f in sep:                                            # sepals face out, away from the berry's middle
        if f.normal.dot(f.calc_center_median() - Vector((0, 0, S * 0.5))) < 0: f.normal_flip()
    lbm.normal_update()
    leaves = mesh_obj('Leaves' + sfx, lbm)
    leaves.data.materials.append(ML)
    if not lod:
        sol = leaves.modifiers.new('Thickness', 'SOLIDIFY'); sol.thickness = S * 0.01
        sub = leaves.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    # put the berry on the cream: leaves up, leaning toward us and to the right, its lower part in the swirl
    root = link(bpy.data.objects.new('Berry', None))
    for o in (berry, seeds_obj, leaves):
        if o: o.parent = root
    root.location, q = berry_pose(S)
    root.rotation_mode = 'QUATERNION'; root.rotation_quaternion = q
    return dict(root=root, parts=[o for o in (berry, seeds_obj, leaves) if o],
                lines={'Strawberry': 'main', 'Seeds': 'main', 'Leaves': 'detail'}, detail_ink='#1E4D22',
                reg={'Strawberry': dict(part=3, src=['Strawberry', 'Seeds'], uv=2.2),
                     'Leaf': dict(part=4, src=['Leaves'], flat_normal=True, uv=2.2)})

# ================================================================ chocolate: an embossed square of chocolate
def _choc_material():
    def make():
        m = principled('Chocolate piece', '#2E1409', rough=0.26, coat=0.45, coat_rough=0.12, spec=0.5)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        # the top face catches a warmer sheen; the sides stay dark
        col = t.ramp(sep.outputs[2], [(0.0, lin('#200C04')), (0.5, lin('#2E1409')), (1.0, lin('#4E2412'))])
        noi = t.node('ShaderNodeTexNoise', in_Scale=30.0, in_Detail=2.0); t.link(tc.outputs['Object'], noi.inputs['Vector'])
        col = t.mix(t.math('MULTIPLY', noi.outputs['Fac'], 0.25), col, lin('#3A1A0C'))
        t.link(col, bsdf.inputs['Base Color'])
        return m
    return _once('Chocolate piece', make)

def chocolate(spec, env):
    lod = env['lod']; M = _choc_material()
    a, th = 0.3, 0.07
    if lod:
        bm = rounded_box(a, a, th, 0.01, 1)
    else:
        bm = rounded_box(a, a, th, 0.007, 3)
        # a raised square in the middle, its sides sloping like a mould's
        top = rounded_box(a * 0.62, a * 0.62, 0.02, 0.006, 3)
        bmesh.ops.translate(top, vec=(0, 0, th / 2 + 0.004), verts=top.verts)
        me_ = bpy.data.meshes.new('tmp'); top.to_mesh(me_); top.free(); bm.from_mesh(me_); bpy.data.meshes.remove(me_)
        closed_outward(bm)
    o = mesh_obj('Chocolate piece' + (' LOD' if lod else ''), bm, smooth=not lod)
    o.data.materials.append(M)
    if lod: _sharp_all(o)
    else:
        for p in o.data.polygons: p.use_smooth = False
    # propped up on one edge, turned off the slice's line, half of a corner sunk in the ganache
    q = Quaternion((0, 0, 1), SEG / 2 + math.radians(28)) @ Quaternion((1, 0, 0), math.radians(24))
    root = _root('Chocolate', TOP_SPOT.copy(), q); o.parent = root
    _lay_on(root, [o], env['top_z'], 0.022, env)
    return dict(root=root, parts=[o], lines={'Chocolate piece': 'main'},
                reg={'Chocolate piece': dict(part=3, src=['Chocolate piece'], uv=2.2)},
                readme='')

# ================================================================ caramel: a hazelnut on a caramel dollop
def _nut_materials():
    def nut():
        m = principled('Hazelnut', '#9A5A28', rough=0.32, coat=0.35, coat_rough=0.15)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        z = sep.outputs[2]
        # fine stripes running tip to base, a darker tip, and the pale rough scar at the base
        mp = t.node('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (55.0, 55.0, 5.0)
        t.link(tc.outputs['Object'], mp.inputs['Vector'])
        st = t.node('ShaderNodeTexNoise', in_Scale=1.0, in_Detail=3.0); t.link(mp.outputs['Vector'], st.inputs['Vector'])
        shell = t.mix(t.math('MULTIPLY', st.outputs['Fac'], 0.9), lin('#8A4C1E'), lin('#B87338'))
        shell = t.mix(t.ramp(z, [(0.0, (0, 0, 0)), (0.13, (0, 0, 0)), (0.17, (1, 1, 1)), (1.0, (1, 1, 1))]), shell, lin('#5E3012'))
        scar = t.mix(t.math('MULTIPLY', st.outputs['Fac'], 0.5), lin('#C7965E'), lin('#A97A44'))
        sm = t.ramp(z, [(0.0, (1, 1, 1)), (0.035, (1, 1, 1)), (0.05, (0, 0, 0)), (1.0, (0, 0, 0))])
        col = t.mix(sm, shell, scar)
        t.link(col, bsdf.inputs['Base Color'])
        bump = t.node('ShaderNodeBump', in_Strength=0.35, in_Distance=0.004)
        t.link(st.outputs['Fac'], bump.inputs['Height']); t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    def dollop():
        return principled('Caramel dollop', '#B86A1C', rough=0.14, coat=0.7, coat_rough=0.05, sss=0.3, sss_radius=(1, .6, .25), sss_scale=0.02)
    return _once('Hazelnut', nut), _once('Caramel dollop', dollop)

def caramel(spec, env):
    lod = env['lod']; MN, MD = _nut_materials()
    h, rm = 0.225, 0.115
    prof = []
    steps = 7 if lod else 26
    for i in range(steps + 1):
        th = i / steps * math.pi                                   # from the base (0) to the tip (pi)
        r = math.sin(th) * rm * (1 - 0.22 * (th / math.pi) ** 2.5)
        z = (1 - math.cos(th)) / 2 * h
        if th < 0.9: z = z * 0.7 + 0.006 * (th / 0.9)               # a broad flattish base
        z += 0.022 * smoothstep(0.75, 1.0, th / math.pi)           # and a little point at the top
        prof.append((r, z))
    n = 10 if lod else 48
    bm = revolve(prof, n, 'nut', around=None if lod else (lambda a, r, z: r * 0.025 * math.sin(a * 9 + z * 20)))
    o = mesh_obj('Hazelnut' + (' LOD' if lod else ''), bm); o.data.materials.append(MN)
    if not lod:
        sub = o.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    dp = [(0.135, 0.0), (0.13, 0.014), (0.105, 0.028), (0.06, 0.037), (0.0, 0.04)] if not lod else [(0.135, 0.0), (0.11, 0.026), (0.0, 0.039)]
    dbm = revolve(dp, 12 if lod else 40, 'dollop', around=None if lod else (lambda a, r, z: 0.007 * math.sin(a * 5) * (r / 0.135)))
    d = mesh_obj('Caramel dollop' + (' LOD' if lod else ''), dbm); d.data.materials.append(MD)
    if not lod:
        sub = d.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    root = _root('Hazelnut on caramel', TOP_SPOT.copy())
    d.parent = root; d.location = (0, 0, -0.012)
    o.parent = root; o.location = (0.005, 0, 0.012)
    o.rotation_euler = (math.radians(14), math.radians(-18), 0.4)
    _lay_on(root, [d], env['top_z'], 0.012, env)
    return dict(root=root, parts=[o, d], lines={o.name: 'main', d.name: 'detail'}, detail_ink='#5A2A08',
                reg={'Hazelnut': dict(part=3, src=['Hazelnut'], uv=2.2),
                     'Caramel dollop': dict(part=4, src=['Caramel dollop'], flat_normal=True, uv=1.2)})

# ================================================================ matcha: a tea leaf on the cream
def _tea_leaf_material():
    def make():
        m = principled('Tea leaf', '#3F8A2E', rough=0.33, coat=0.35, coat_rough=0.1, sss=0.12, sss_radius=(.4, 1, .3), sss_scale=0.01)
        t = NT(m); bsdf = t.n['Principled BSDF']
        uvn = t.node('ShaderNodeUVMap'); sep = t.node('ShaderNodeSeparateXYZ'); t.link(uvn.outputs['UV'], sep.inputs[0])
        u, v = sep.outputs[0], sep.outputs[1]                      # u along the leaf 0..1, v across -1..1
        av = t.math('ABSOLUTE', v)
        mid = t.math('SUBTRACT', 1.0, t.math('DIVIDE', av, 0.07), clamp=True)
        veins = t.math('SUBTRACT', 1.0, t.math('DIVIDE', t.math('ABSOLUTE', t.math('SUBTRACT',
                    t.math('FRACT', t.math('SUBTRACT', t.math('MULTIPLY', u, 7.0), t.math('MULTIPLY', av, 1.6))), 0.5)), 0.06), clamp=True)
        veins = t.math('MULTIPLY', veins, t.math('SUBTRACT', 1.0, t.math('DIVIDE', av, 0.85), clamp=True))
        col = t.ramp(av, [(0.0, lin('#4E9C38')), (0.7, lin('#3F8A2E')), (1.0, lin('#2C6A20'))])
        col = t.mix(t.math('MULTIPLY', veins, 0.45), col, lin('#7DBE5A'))
        col = t.mix(mid, col, lin('#9FD27C'))
        t.link(col, bsdf.inputs['Base Color'])
        bump = t.node('ShaderNodeBump', in_Strength=0.3, in_Distance=0.004)
        t.link(t.math('MAXIMUM', mid, t.math('MULTIPLY', veins, 0.6)), bump.inputs['Height'])
        t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    return _once('Tea leaf', make)

def _leaf_point(t, s, L, W):
    """A point on the leaf: t along (0 stem .. 1 tip), s across (-1 .. 1)."""
    w = W / 2 * math.sin(math.pi * min(1.0, t)) ** 0.7 * (1 - 0.3 * t)
    saw = 1 + 0.07 * (1 - abs(((t * 13) % 1) * 2 - 1))              # a fine serrated edge
    if abs(s) > 0.95: w *= saw
    x = t * L
    y = s * w
    z = abs(s) * w * 0.38 + 0.035 * math.sin(math.pi * t) - 0.012 * t   # folded along the midrib, arched
    return Vector((x, y, z))

def matcha(spec, env):
    lod = env['lod']; M = _tea_leaf_material()
    L, W = 0.27, 0.12
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    if not lod:
        nt_, ns = 26, 10
        grid = [[bm.verts.new(_leaf_point(i / nt_, -1 + 2 * j / ns, L, W)) for j in range(ns + 1)] for i in range(nt_ + 1)]
        for i in range(nt_):
            for j in range(ns):
                f = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
                for lp, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                    lp[uvl].uv = (ii / nt_, -1 + 2 * jj / ns)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.normal_update()
        if sum(f.normal.z for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
        o = mesh_obj('Tea leaf', bm); o.data.materials.append(M)
        sol = o.modifiers.new('Thickness', 'SOLIDIFY'); sol.thickness = 0.007; sol.offset = -1
        sub = o.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
        # a short stem
        sbm = bmesh.new()
        bmesh.ops.create_cone(sbm, cap_ends=True, segments=8, radius1=0.0045, radius2=0.003, depth=0.04,
                              matrix=Matrix.Translation((-0.016, 0, 0.004)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
        closed_outward(sbm)
        tmp = bpy.data.meshes.new('stem'); sbm.to_mesh(tmp); sbm.free()
        st = link(bpy.data.objects.new('Tea leaf stem', tmp)); st.data.materials.append(M); st.parent = o
        parts = [o, st]
    else:
        # a thin closed lens: top sheet and a bottom sheet that shares its rim, so no edge is open
        nt_ = 5; top, bot = [], []
        for i in range(nt_ + 1):
            t = i / nt_
            row = [bm.verts.new(_leaf_point(t, s, L, W)) for s in (-1, 0, 1)]
            top.append(row)
        for i in range(1, nt_):
            p = _leaf_point(i / nt_, 0, L, W); bot.append(bm.verts.new(p - Vector((0, 0, 0.012))))
        def uvf(f, coords):
            for lp, c in zip(f.loops, coords): lp[uvl].uv = c
        for i in range(nt_):
            for j in range(2):
                f = bm.faces.new((top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]))
                uvf(f, [(i / nt_, -1 + j), (i / nt_, j), ((i + 1) / nt_, j), ((i + 1) / nt_, -1 + j)])
        # underside: rim -> midrib below
        mids = [top[0][1]] + bot + [top[nt_][1]]
        for i in range(nt_):
            for side in (0, 2):
                f = bm.faces.new((top[i][side], mids[i], mids[i + 1], top[i + 1][side]))
                uvf(f, [(i / nt_, side - 1), (i / nt_, 0), ((i + 1) / nt_, 0), ((i + 1) / nt_, side - 1)])
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        closed_outward(bm)
        o = mesh_obj('Tea leaf LOD', bm); o.data.materials.append(M)
        parts = [o]
    # lying across the top of the rosette, its middle over the peak, rolled a little toward us
    q = (Quaternion((0, 0, 1), SEG / 2 - math.radians(60)) @ Quaternion((0, 1, 0), math.radians(-10))
         @ Quaternion((1, 0, 0), math.radians(-16)))
    root = _root('Tea leaf on cream', TOP_SPOT + Vector((0, 0, ROSETTE_REST - TOP_SPOT.z + 0.06)), q)
    o.parent = root; o.location = (-L * 0.42, 0, 0)
    return dict(root=root, parts=parts, lines={'Tea leaf': 'main', 'Tea leaf stem': 'main'},
                reg={'Tea leaf': dict(part=3, src=['Tea leaf', 'Tea leaf stem'], flat_normal=True, uv=2.2)})

# ================================================================ blueberry: three berries with their crowns
def _blueberry_material():
    def make():
        m = principled('Blueberry', '#33358F', rough=0.42, coat=0.2, coat_rough=0.2, sss=0.05, sss_radius=(.3, .3, 1), sss_scale=0.01)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        # the dusty bloom: paler toward the edges and in soft patches; the crown dark
        lw = t.node('ShaderNodeLayerWeight', in_Blend=0.5)
        vd = t.node('ShaderNodeValue', name='ViewDep'); vd.outputs[0].default_value = 1.0
        noi = t.node('ShaderNodeTexNoise', in_Scale=14.0, in_Detail=3.0); t.link(tc.outputs['Object'], noi.inputs['Vector'])
        col = t.mix(t.math('MULTIPLY', noi.outputs['Fac'], 0.55), lin('#2E3088'), lin('#5A5FC2'))
        col = t.mix(t.math('MULTIPLY', t.math('POWER', lw.outputs['Facing'], 1.5), t.math('MULTIPLY', vd.outputs[0], 0.6)), col, lin('#7C82D6'))
        crown = t.ramp(sep.outputs[2], [(0.0, (0, 0, 0)), (0.82, (0, 0, 0)), (0.9, (1, 1, 1)), (1.0, (1, 1, 1))])
        col = t.mix(crown, col, lin('#1E1C4E'))
        t.link(col, bsdf.inputs['Base Color'])
        return m
    return _once('Blueberry', make)

def _blueberry(name, r, lod, M):
    if lod:                                                         # round enough at game size: 8 x 5, 64 triangles
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=r)
        for v in bm.verts: v.co.z *= 0.88
        closed_outward(bm)
    else:
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=r)
        for v in bm.verts:
            v.co.z *= 0.88
            # the crown at the top: a five-pointed star sunk in a dimple, its points a little raised
            p = v.co; rho = Vector((p.x, p.y)).length / r; a = math.atan2(p.y, p.x)
            if p.z > 0 and rho < 0.42:
                star = 0.5 + 0.5 * math.cos(5 * a)
                v.co.z -= r * 0.16 * (1 - rho / 0.42) ** 1.5
                v.co.z += r * 0.07 * star * smoothstep(0.12, 0.3, rho) * (1 - smoothstep(0.3, 0.42, rho))
        closed_outward(bm)
    o = mesh_obj(name, bm); o.data.materials.append(M)
    if not lod:
        sub = o.modifiers.new('Smooth', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    return o

def blueberry(spec, env):
    lod = env['lod']; M = _blueberry_material()
    sfx = ' LOD' if lod else ''
    spots = [(-0.068, -0.012, 0.0, 0.07), (0.07, -0.01, 0.006, 0.066), (0.0, 0.05, 0.07, 0.068)]
    q = Quaternion((0, 0, 1), SEG / 2 - math.pi / 2)
    root = _root('Blueberries', TOP_SPOT + Vector((0, 0, ROSETTE_REST - TOP_SPOT.z + 0.035)), q)
    parts = []
    for k, (x, y, z, r) in enumerate(spots):
        o = _blueberry(f'Blueberry {k + 1}{sfx}', r, lod, M)
        o.parent = root; o.location = (x, y, z)
        o.rotation_euler = (math.radians(25 - 18 * k), math.radians(12 * (k - 1)), 0.6 * k)
        parts.append(o)
    return dict(root=root, parts=parts, lines={o.name: 'main' for o in parts},
                reg={'Blueberry': dict(part=3, src=[f'Blueberry {k + 1}' for k in range(3)], uv=2.2)})

# ================================================================ birthday: a striped candle, lit
def _candle_materials():
    def wax():
        m = principled('Candle', '#FFF8F0', rough=0.3, coat=0.3, sss=0.35, sss_radius=(1, .8, .6), sss_scale=0.02)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        ang = t.math('DIVIDE', t.math('ARCTAN2', sep.outputs[1], sep.outputs[0]), math.tau)
        stripe = t.math('FRACT', t.math('ADD', t.math('MULTIPLY', sep.outputs[2], 9.0), ang))
        mask = t.ramp(stripe, [(0.0, (1, 1, 1)), (0.36, (1, 1, 1)), (0.42, (0, 0, 0)), (1.0, (0, 0, 0))])
        t.link(t.mix(mask, lin('#FFF8F0'), lin('#FF5E98')), bsdf.inputs['Base Color'])
        return m
    def wick():
        return principled('Wick', '#3B2A20', rough=0.8)
    def flame():
        m = principled('Candle flame', '#FFC94A', rough=0.5)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        # a warm core at the wick, orange toward the tip: glowing, but not blown out to white
        col = t.ramp(sep.outputs[2], [(0.0, lin('#FFE680')), (0.035, lin('#FFC23A')), (0.1, lin('#FF8A1F'))])
        bsdf.inputs['Emission Strength'].default_value = 1.4
        t.link(col, bsdf.inputs['Emission Color']); t.link(col, bsdf.inputs['Base Color'])
        return m
    return _once('Candle', wax), _once('Wick', wick), _once('Candle flame', flame)

def birthday(spec, env):
    lod = env['lod']; MW, MK, MF = _candle_materials()
    sfx = ' LOD' if lod else ''
    r, h = 0.034, 0.27
    n = 8 if lod else 40
    prof = [(r, 0.0), (r, h - 0.006), (r * 0.82, h)] if not lod else [(r, 0.0), (r, h)]
    c = mesh_obj('Candle' + sfx, revolve(prof, n, 'candle')); c.data.materials.append(MW)
    if lod: _sharp_by_angle(c)
    kb = revolve([(0.005, 0.0), (0.0045, 0.03), (0.0, 0.034)], 3 if lod else 10, 'wick')
    k = mesh_obj('Wick' + sfx, kb); k.data.materials.append(MK)
    fp = [(0.0, 0.0), (0.02, 0.012), (0.029, 0.034), (0.022, 0.062), (0.0, 0.1)] if not lod else [(0.0, 0.0), (0.026, 0.02), (0.022, 0.058), (0.0, 0.1)]
    f = mesh_obj('Candle flame' + sfx, revolve(fp, 6 if lod else 24, 'flame')); f.data.materials.append(MF)
    root = _root('Candle', TOP_SPOT + Vector((0, 0, ROSETTE_REST - TOP_SPOT.z - 0.035)))
    c.parent = root
    k.parent = root; k.location = (0, 0, h - 0.004)
    f.parent = root; f.location = (0, 0, h + 0.018)
    return dict(root=root, parts=[c, k, f], lines={c.name: 'main', k.name: 'main', f.name: 'detail'}, detail_ink='#C0560C',
                reg={'Candle': dict(part=3, src=['Candle'], flat_normal=True, uv=2.2),
                     'Wick': dict(part=4, src=['Wick'], flat_colour=True, flat_normal=True, uv=0.4),
                     'Candle flame': dict(part=4, src=['Candle flame'], flat_colour=True, flat_normal=True, uv=0.6)},
                readme="""

The candle's flame is part of the mesh, baked as a flat warm yellow (#FFC94A). The game's 2D candle flickers;
in Unity give the flame's triangles (y 1.108 to 1.208; everything above y 1.10, over the wick and the candle's
top at 1.09) an unlit or emissive look in the slice shader, or hide them and draw a flame sprite or particle
at the wick (about y 1.10 at the slice's middle).""")

# ================================================================ mango: three juicy cubes
def _mango_material():
    def make():
        m = principled('Mango', '#FFA21C', rough=0.22, coat=0.5, coat_rough=0.08, sss=0.35, sss_radius=(1, .5, .2), sss_scale=0.02)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        col = t.ramp(sep.outputs[2], [(-0.05, lin('#E68400')), (0.0, lin('#FFA21C')), (0.045, lin('#FFD06A'))])
        mp = t.node('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (8.0, 8.0, 60.0)
        t.link(tc.outputs['Object'], mp.inputs['Vector'])
        fib = t.node('ShaderNodeTexNoise', in_Scale=1.0, in_Detail=2.0); t.link(mp.outputs['Vector'], fib.inputs['Vector'])
        col = t.mix(t.math('MULTIPLY', fib.outputs['Fac'], 0.25), col, lin('#FFB940'))
        t.link(col, bsdf.inputs['Base Color'])
        bump = t.node('ShaderNodeBump', in_Strength=0.12, in_Distance=0.003)
        t.link(fib.outputs['Fac'], bump.inputs['Height']); t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    return _once('Mango', make)

def mango(spec, env):
    lod = env['lod']; M = _mango_material()
    sfx = ' LOD' if lod else ''
    cubes = [((-0.074, -0.024, 0.0), 0.12, (0, 0, 0.25)), ((0.079, 0.014, 0.0), 0.113, (0, 0, -0.35)),
             ((0.005, -0.005, 0.103), 0.106, (0.18, -0.12, 0.7))]
    root = _root('Mango cubes', TOP_SPOT.copy(), Quaternion((0, 0, 1), SEG / 2 - math.pi / 2))
    parts = []
    for k, (p, a, rot) in enumerate(cubes):
        bm = rounded_box(a, a, a, 0.012 if lod else 0.018, 1 if lod else 4)
        o = mesh_obj(f'Mango cube {k + 1}{sfx}', bm, smooth=not lod); o.data.materials.append(M)
        if lod: _sharp_all(o)
        o.parent = root; o.location = Vector(p) + Vector((0, 0, a / 2)); o.rotation_euler = rot
        parts.append(o)
    _lay_on(root, parts[:2], env['top_z'], 0.012, env)
    return dict(root=root, parts=parts, lines={o.name: 'main' for o in parts},
                reg={'Mango': dict(part=3, src=[f'Mango cube {k + 1}' for k in range(3)], flat_normal=True, uv=2.0)})

# ================================================================ cookies & cream: a sandwich cookie
def _cookie_materials():
    def wafer():
        m = principled('Cookie', '#262120', rough=0.75, coat=0.0)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        x, y = sep.outputs[0], sep.outputs[1]
        r = t.math('SQRT', t.math('ADD', t.math('MULTIPLY', x, x), t.math('MULTIPLY', y, y)))
        a = t.math('ARCTAN2', y, x)
        # the embossed face: a ring, a flower of twelve petals inside it, a beaded rim
        ring = t.math('SUBTRACT', 1.0, t.math('DIVIDE', t.math('ABSOLUTE', t.math('SUBTRACT', r, 0.082)), 0.006), clamp=True)
        pet = t.math('MULTIPLY', t.math('ADD', t.math('MULTIPLY', t.math('COSINE', t.math('MULTIPLY', a, 12.0)), 0.5), 0.5),
                     t.math('MULTIPLY', t.math('GREATER_THAN', r, 0.03), t.math('LESS_THAN', r, 0.07)))
        beads = t.math('MULTIPLY', t.math('ADD', t.math('MULTIPLY', t.math('COSINE', t.math('MULTIPLY', a, 36.0)), 0.5), 0.5),
                       t.math('GREATER_THAN', r, 0.095))
        h = t.math('MAXIMUM', t.math('MAXIMUM', ring, t.math('MULTIPLY', pet, 0.8)), t.math('MULTIPLY', beads, 0.6))
        noi = t.node('ShaderNodeTexNoise', in_Scale=90.0, in_Detail=2.0); t.link(tc.outputs['Object'], noi.inputs['Vector'])
        col = t.mix(t.math('MULTIPLY', h, 0.55), lin('#221D1B'), lin('#3E3633'))
        col = t.mix(t.math('MULTIPLY', noi.outputs['Fac'], 0.3), col, lin('#14110F'))
        t.link(col, bsdf.inputs['Base Color'])
        bump = t.node('ShaderNodeBump', in_Strength=0.3, in_Distance=0.002)
        t.link(t.math('ADD', h, t.math('MULTIPLY', noi.outputs['Fac'], 0.2)), bump.inputs['Height'])
        t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    def cream():
        return principled('Cookie cream', '#FBF8F2', rough=0.5, sss=0.25, sss_radius=(1, .9, .8), sss_scale=0.01)
    return _once('Cookie', wafer), _once('Cookie cream', cream)

def cookies(spec, env):
    lod = env['lod']; MW, MC = _cookie_materials()
    sfx = ' LOD' if lod else ''
    R0, T, TC = 0.118, 0.022, 0.018
    if not lod:
        def wafer(name, z0):
            prof = [(0.0, 0.0), (R0 * 0.97, 0.0), (R0, T * 0.25), (R0, T * 0.75), (R0 * 0.97, T), (0.0, T)]
            bm = revolve(prof, 72, name, around=lambda a, r, z: r * 0.02 * math.cos(a * 36) if r > R0 * 0.9 else 0.0)
            bmesh.ops.translate(bm, vec=(0, 0, z0), verts=bm.verts)
            o = mesh_obj(name, bm, smooth=False); o.data.materials.append(MW)
            for p in o.data.polygons: p.use_smooth = abs(p.normal.z) < 0.5
            return o
        w1 = wafer('Cookie wafer 1', 0.0)
        cr = mesh_obj('Cookie filling', revolve([(0.0, 0.0), (R0 * 0.88, 0.0), (R0 * 0.9, TC * 0.5), (R0 * 0.88, TC), (0.0, TC)], 48, 'filling'))
        cr.data.materials.append(MC)
        for v in cr.data.vertices: v.co.z += T
        w2 = wafer('Cookie wafer 2', T + TC)
        parts = [w1, cr, w2]
        lines = {w1.name: 'main', w2.name: 'main', cr.name: 'detail'}
    else:
        # one closed piece: two wafers and the cream between them as a groove, so no face is buried inside
        # another (a bake would read a buried face from the wrong side)
        prof = [(0.0, 0.0), (R0, 0.0), (R0, T), (R0 * 0.88, T), (R0 * 0.88, T + TC), (R0, T + TC), (R0, 2 * T + TC), (0.0, 2 * T + TC)]
        bm = revolve(prof, 12, 'cookie')
        o = mesh_obj('Cookie LOD', bm, smooth=False)
        o.data.materials.append(MW); o.data.materials.append(MC)
        for p in o.data.polygons:                                       # the groove's wall is the cream
            if abs(p.normal.z) < 0.5 and T + 0.002 < p.center.z < T + TC - 0.002: p.material_index = 1
        _sharp_by_angle(o)
        parts = [o]; lines = {}
    # stood on its edge in the cream, leaning back and turned so its face shows
    q = Quaternion((0, 0, 1), SEG / 2 + math.radians(30)) @ Quaternion((0, 1, 0), math.radians(90 - 24))
    root = _root('Cookie', TOP_SPOT.copy(), q)
    for o in parts:
        o.parent = root; o.location.z -= (2 * T + TC) / 2
    _lay_on(root, [parts[0], parts[-1]], env['top_z'], 0.04, env)
    return dict(root=root, parts=parts, lines=lines, detail_ink='#6E6660',
                reg={'Cookie': dict(part=3, src=['Cookie wafer 1', 'Cookie wafer 2'], uv=2.2, cage=0.008, ray=0.03),
                     'Cookie cream': dict(part=4, src=['Cookie filling'], flat_colour=True, flat_normal=True, uv=0.6)})

# ================================================================ red velvet: a raspberry
def _raspberry_materials():
    def drupe():
        m = principled('Raspberry', '#C8144A', rough=0.2, coat=0.55, coat_rough=0.05, sss=0.4, sss_radius=(1, .2, .3), sss_scale=0.01)
        t = NT(m); bsdf = t.n['Principled BSDF']
        lw = t.node('ShaderNodeLayerWeight', in_Blend=0.4)
        vd = t.node('ShaderNodeValue', name='ViewDep'); vd.outputs[0].default_value = 1.0
        col = t.mix(t.math('MULTIPLY', t.math('POWER', lw.outputs['Facing'], 1.2), vd.outputs[0]), lin('#D41A55'), lin('#8E0C33'))
        t.link(col, bsdf.inputs['Base Color'])
        return m
    def core():
        return principled('Raspberry core', '#7A0A2A', rough=0.4, sss=0.2, sss_radius=(1, .2, .3), sss_scale=0.01)
    return _once('Raspberry', drupe), _once('Raspberry core', core)

def redvelvet(spec, env):
    lod = env['lod']; MD, MC = _raspberry_materials()
    sfx = ' LOD' if lod else ''
    H, RB = 0.16, 0.078
    def core_r(z):                                                     # the berry's envelope: a plump rounded cone
        u = z / H
        return RB * (math.sin(math.pi * min(1.0, 0.18 + 0.82 * u)) ** 0.55) * (1 - 0.25 * u)
    if lod:
        prof = [(RB * 0.7, 0.0)] + [(core_r(H * k / 5) + 0.014, H * k / 5) for k in range(1, 5)] + [(0.0, H + 0.012)]
        o = mesh_obj('Raspberry' + sfx, revolve(prof, 10, 'rasp')); o.data.materials.append(MD)
        parts = [o]; reg = {'Raspberry': dict(part=3, src=['Raspberry', 'Raspberry core'], uv=2.2)}
    else:
        c = mesh_obj('Raspberry core', revolve([(RB * 0.6, 0.0)] + [(core_r(H * k / 12) * 0.92, H * k / 12) for k in range(1, 12)] + [(0.0, H)], 24, 'core'))
        c.data.materials.append(MC)
        bm = bmesh.new(); rnd = random.Random(7)
        rows = 7
        for j in range(rows):
            z = H * (0.06 + 0.88 * j / (rows - 1))
            rr = core_r(z) * 0.92
            cnt = max(4, int(round(math.tau * rr / 0.034)))
            for i in range(cnt):
                a = (i + 0.5 * (j % 2)) / cnt * math.tau + rnd.uniform(-0.08, 0.08)
                rad = 0.019 + rnd.uniform(-0.002, 0.002)
                p = Vector((math.cos(a) * (rr + rad * 0.55), math.sin(a) * (rr + rad * 0.55), z + rnd.uniform(-0.003, 0.003)))
                bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=rad, matrix=Matrix.Translation(p))
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.018, matrix=Matrix.Translation((0, 0, H + 0.004)))
        closed = bm
        bm.normal_update()
        o = mesh_obj('Raspberry', closed); o.data.materials.append(MD)
        parts = [o, c]; reg = {}
    root = _root('Raspberry on top', TOP_SPOT.copy(), Quaternion((0, 1, 0), math.radians(8)))
    for p_ in parts: p_.parent = root
    _lay_on(root, parts[:1], env['top_z'], 0.012, env)
    return dict(root=root, parts=parts, lines={'Raspberry': 'main'}, reg=reg)

# ================================================================ lemon: a candied half-wheel in the cream
def _lemon_material():
    def make():
        m = principled('Lemon', '#FFE765', rough=0.16, coat=0.65, coat_rough=0.05, sss=0.35, sss_radius=(1, .9, .3), sss_scale=0.015)
        t = NT(m); bsdf = t.n['Principled BSDF']
        tc, sep = t.obj_xyz()
        x, z = sep.outputs[0], sep.outputs[2]
        r = t.math('DIVIDE', t.math('SQRT', t.math('ADD', t.math('MULTIPLY', x, x), t.math('MULTIPLY', z, z))), 0.15)
        a = t.math('ARCTAN2', z, x)                                   # 0 .. pi over the half wheel
        # rind, pith, flesh in five segments with pale membranes, a pale core, juicy cells
        seg = t.math('ABSOLUTE', t.math('SUBTRACT', t.math('FRACT', t.math('DIVIDE', a, math.pi / 5)), 0.5))
        memb = t.math('SUBTRACT', 1.0, t.math('DIVIDE', t.math('SUBTRACT', 0.5, seg), 0.05), clamp=True)
        vor = t.node('ShaderNodeTexVoronoi', in_Scale=55.0); t.link(tc.outputs['Object'], vor.inputs['Vector'])
        flesh = t.mix(t.math('MULTIPLY', vor.outputs['Distance'], 0.8), lin('#FFE24A'), lin('#FFF09A'))
        col = t.mix(memb, flesh, lin('#FFF8D8'))
        col = t.mix(t.ramp(r, [(0.0, (1, 1, 1)), (0.1, (1, 1, 1)), (0.14, (0, 0, 0)), (1.0, (0, 0, 0))]), col, lin('#FFF8D8'))
        col = t.mix(t.ramp(r, [(0.0, (0, 0, 0)), (0.8, (0, 0, 0)), (0.83, (1, 1, 1)), (1.0, (1, 1, 1))]), col, lin('#FFF6D6'))
        col = t.mix(t.ramp(r, [(0.0, (0, 0, 0)), (0.9, (0, 0, 0)), (0.93, (1, 1, 1)), (1.0, (1, 1, 1))]), col, lin('#F2BE00'))
        t.link(col, bsdf.inputs['Base Color'])
        bump = t.node('ShaderNodeBump', in_Strength=0.15, in_Distance=0.003)
        t.link(t.math('ADD', memb, t.math('MULTIPLY', vor.outputs['Distance'], 0.5)), bump.inputs['Height'])
        t.link(bump.outputs['Normal'], bsdf.inputs['Normal'])
        return m
    return _once('Lemon', make)

def lemon(spec, env):
    lod = env['lod']; M = _lemon_material()
    rr, th = 0.15, 0.038
    n = 8 if lod else 48
    bm = bmesh.new()
    # the half wheel in the XZ plane (flat side down), extruded along Y
    pts = [(math.cos(math.pi * i / n) * rr, math.sin(math.pi * i / n) * rr) for i in range(n + 1)]
    front = [bm.verts.new((x, -th / 2, z)) for x, z in pts]; back = [bm.verts.new((x, th / 2, z)) for x, z in pts]
    bm.faces.new(front); bm.faces.new(list(reversed(back)))
    for i in range(n):
        bm.faces.new((front[i], front[i + 1], back[i + 1], back[i]))
    bm.faces.new((front[n], front[0], back[0], back[n]))
    if not lod:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    closed_outward(bm)
    o = mesh_obj('Lemon wheel' + (' LOD' if lod else ''), bm, smooth=False); o.data.materials.append(M)
    if lod: _sharp_all(o)
    else:
        for p in o.data.polygons: p.use_smooth = abs(p.normal.y) < 0.9
    # standing in the top of the rosette, leaning back so its face shows from every side
    q = Quaternion((0, 0, 1), SEG / 2 + math.radians(18)) @ Quaternion((1, 0, 0), math.radians(-38))
    root = _root('Lemon wheel on cream', TOP_SPOT + Vector((0, 0, ROSETTE_REST - TOP_SPOT.z - 0.008)), q)
    o.parent = root
    return dict(root=root, parts=[o], lines={o.name: 'main'},
                reg={'Lemon': dict(part=3, src=['Lemon wheel'], flat_normal=True, uv=2.2)})

BUILDERS = {'strawberry': strawberry, 'choc': chocolate, 'nut': caramel, 'leaf': matcha, 'berries': blueberry,
            'candle': birthday, 'cubes': mango, 'cookie': cookies, 'raspberry': redvelvet, 'lemon': lemon}

def build(spec, env):
    out = dict(readme='', detail_ink='#1E4D22', reg={})
    out.update(BUILDERS[spec['topping']](spec, env))
    out['env'] = env
    return out

# ================================================================ patterns on top (hi-res; baked into the game coat)
def _on_top(env, x, y, lift=0.0):
    hit = env['coat_tree'].ray_cast(Vector((x, y, 2.0)), Vector((0, 0, -1)))[0]
    return Vector((x, y, (hit.z if hit else env['top_z']) + lift))

def _inside(x, y, margin=0.05, rim=0.06):
    r = math.hypot(x, y); a = math.atan2(y, x)
    if r > R - rim or r < 0.12: return False
    return r * math.sin(a) > margin and r * math.sin(SEG - a) > margin

def _tube(name, pts, radius, mat, res=4):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (c.x, c.y, c.z, 1)
    tmp = link(bpy.data.objects.new(name + ' tmp', cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); bpy.data.objects.remove(tmp)
    bm = bmesh.new(); bm.from_mesh(me); closed_outward(bm); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat)
    return o

def build_pattern(spec, env):
    pat = spec['pattern']; kind = pat['kind']; rnd = random.Random(11)
    out = []
    if kind == 'swirl':
        # piped ganache rings round the cake, a little lighter than the coat
        m = principled('Swirl', pat['colour'], rough=0.2, coat=0.55, coat_rough=0.08)
        for k, rr in enumerate((0.36, 0.72)):
            a0, a1 = 0.035 / rr, SEG - 0.035 / rr
            pts = [_on_top(env, math.cos(a0 + (a1 - a0) * i / 40) * rr, math.sin(a0 + (a1 - a0) * i / 40) * rr, -0.002) for i in range(41)]
            o = _tube(f'Swirl {k + 1}', pts, 0.02, m)
            for v in o.data.vertices:                                # a low soft ridge in the ganache, not a wire
                zs = _on_top(env, v.co.x, v.co.y).z
                v.co.z = zs + (v.co.z - zs) * 0.5
            out.append(o)
    elif kind == 'drizzle':
        m = principled('Drizzle', pat['colour'], rough=0.12, coat=0.7, coat_rough=0.05, sss=0.2, sss_radius=(1, .5, .2), sss_scale=0.01)
        ctrl = [(k / 8, 0.95 if k % 2 else 0.42) for k in range(9)]
        pts = []
        for k in range(len(ctrl) - 1):                              # a smooth zigzag through the control points
            for s in range(12):
                f = s / 12; u = ctrl[k][0] + (ctrl[k + 1][0] - ctrl[k][0]) * f
                v = ctrl[k][1] + (ctrl[k + 1][1] - ctrl[k][1]) * (0.5 - 0.5 * math.cos(math.pi * f))
                a = 0.06 + (SEG - 0.12) * u
                pts.append(_on_top(env, math.cos(a) * v * 0.97, math.sin(a) * v * 0.97, 0.003))
        out.append(_tube('Drizzle', pts, 0.013, m))
        # flakes of salt
        sm = principled('Salt', '#FFFFFF', rough=0.15, coat=0.2, sss=0.3, sss_radius=(1, 1, 1), sss_scale=0.005)
        bm = bmesh.new(); placed = 0
        while placed < 11:
            x, y = rnd.uniform(0.2, 0.95), rnd.uniform(0.02, 0.85)
            if not _inside(x, y, 0.06, 0.08) or (Vector((x, y)) - TOP_SPOT.xy).length < 0.15: continue
            p = _on_top(env, x, y, 0.004); s = rnd.uniform(0.012, 0.02)
            mtx = Matrix.Translation(p) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, 'Z') @ Matrix.Rotation(rnd.uniform(-0.4, 0.4), 4, 'X') @ Matrix.Diagonal((s, s * rnd.uniform(0.6, 1.0), s * 0.35, 1))
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mtx); placed += 1
        o = mesh_obj('Salt flakes', bm, smooth=False); o.data.materials.append(sm); out.append(o)
    elif kind == 'sprinkles':
        mats = [principled(f'Sprinkle {i}', c, rough=0.3, coat=0.5, coat_rough=0.1) for i, c in enumerate(pat['colours'])]
        bm = bmesh.new(); placed = 0; tries = 0
        while placed < 30 and tries < 2000:
            tries += 1
            x, y = rnd.uniform(0.12, 0.98), rnd.uniform(0.0, 0.88)
            if not _inside(x, y, 0.045, 0.06) or (Vector((x, y)) - TOP_SPOT.xy).length < 0.24: continue
            p = _on_top(env, x, y, 0.006)
            mtx = Matrix.Translation(p) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'Y')
            g = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.0105, radius2=0.0105, depth=0.056, matrix=mtx)
            mi = placed % len(mats)
            for f in {f for v in g['verts'] for f in v.link_faces}: f.material_index = mi
            placed += 1
        closed_outward(bm)
        o = mesh_obj('Sprinkles', bm)
        for mm in mats: o.data.materials.append(mm)
        bev = o.modifiers.new('Round', 'BEVEL'); bev.width = 0.006; bev.segments = 3
        out.append(o)
    elif kind == 'crumbs':
        m = principled('Crumb', pat['colour'], rough=0.85)
        t = NT(m); bsdf = t.n['Principled BSDF']; tc, sep = t.obj_xyz()
        vor = t.node('ShaderNodeTexVoronoi', in_Scale=160.0); t.link(tc.outputs['Object'], vor.inputs['Vector'])
        t.link(t.mix(t.ramp(vor.outputs['Distance'], [(0.0, (1, 1, 1)), (0.2, (0, 0, 0))]), lin(pat['colour']), lin(pat['light'])), bsdf.inputs['Base Color'])
        bm = bmesh.new(); placed = 0; tries = 0
        while placed < 16 and tries < 3000:
            tries += 1
            a = rnd.uniform(0.0, SEG); v = rnd.uniform(0.62, 0.95)
            x, y = math.cos(a) * v, math.sin(a) * v
            if not _inside(x, y, 0.05, 0.06) or (Vector((x, y)) - TOP_SPOT.xy).length < 0.16: continue
            s = rnd.uniform(0.016, 0.03)
            p = _on_top(env, x, y, s * 0.35)
            mtx = Matrix.Translation(p) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, 'Z') @ Matrix.Diagonal((s, s * rnd.uniform(0.7, 1.0), s * rnd.uniform(0.6, 0.85), 1))
            g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mtx)
            for vv in g['verts']: vv.co += (vv.co - p).normalized() * s * rnd.uniform(-0.25, 0.2)
            placed += 1
        closed_outward(bm)
        o = mesh_obj('Crumbs', bm, smooth=False); o.data.materials.append(m); out.append(o)
    return out
