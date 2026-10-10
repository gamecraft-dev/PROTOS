# Cake Sort slices: helpers shared by the build (cake_slice.py) and its parts (cake_toppings.py).
import bpy, bmesh, math
from mathutils import Vector, Matrix

R = 1.0
SEG = math.radians(60)
H_TOP = 0.71                       # top of the coat
H_BODY = 0.672                     # where the coat's band starts on a cut face
SPONGE_TOP = H_BODY - 0.016        # the sponge stops a little lower, so at a seam between slices the coat covers it
GLAZE_E = 0.024                    # how far the coat stands off the sponge
RC = 0.6366                        # centroid of the sector, as a share of R
CENTROID = Vector((RC * math.cos(SEG / 2), RC * math.sin(SEG / 2)))
TOP_SPOT = Vector((0.56 * math.cos(SEG / 2), 0.56 * math.sin(SEG / 2), H_TOP))   # where the topping stands

def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)

def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj

def mesh_obj(name, bm, coll=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return link(bpy.data.objects.new(name, me), coll)

def principled(name, base, rough=0.5, coat=0.0, coat_rough=0.05, sss=0.0, sss_radius=(1, .5, .3), sss_scale=0.02, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(base) if isinstance(base, str) else base
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_rough
    b.inputs['Subsurface Weight'].default_value = sss
    b.inputs['Subsurface Radius'].default_value = sss_radius
    b.inputs['Subsurface Scale'].default_value = sss_scale
    b.inputs['Specular IOR Level'].default_value = spec
    return m

class NT:
    """Small helper for building node trees."""
    def __init__(self, mat):
        self.nt = mat.node_tree; self.n = self.nt.nodes; self.l = self.nt.links
    def node(self, kind, **kw):
        nd = self.n.new(kind)
        for k, v in kw.items():
            if k.startswith('in_'):
                key = k[3:].replace('_', ' ')
                nd.inputs[key].default_value = v
            else:
                setattr(nd, k, v)
        return nd
    def math(self, op, a, b=None, clamp=False):
        nd = self.n.new('ShaderNodeMath'); nd.operation = op; nd.use_clamp = clamp
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): nd.inputs[i].default_value = x
            else: self.l.new(x, nd.inputs[i])
        return nd.outputs[0]
    def link(self, out, inp): self.l.new(out, inp)
    def ramp(self, fac, stops, interp='LINEAR'):
        r = self.n.new('ShaderNodeValToRGB'); r.color_ramp.interpolation = interp
        els = r.color_ramp.elements
        while len(els) > len(stops): els.remove(els[-1])
        while len(els) < len(stops): els.new(0.5)
        for e, (pos, col) in zip(els, stops):
            e.position = pos; e.color = col if len(col) == 4 else (*col, 1)
        self.l.new(fac, r.inputs['Fac'])
        return r.outputs['Color']
    def mix(self, fac, a, b):
        m = self.n.new('ShaderNodeMix'); m.data_type = 'RGBA'; m.blend_type = 'MIX'
        if isinstance(fac, (int, float)): m.inputs['Factor'].default_value = fac
        else: self.l.new(fac, m.inputs['Factor'])
        for slot, x in (('A', a), ('B', b)):
            if isinstance(x, tuple): m.inputs[slot].default_value = x
            else: self.l.new(x, m.inputs[slot])
        return m.outputs['Result']
    def obj_xyz(self, kind='Object'):
        tc = self.node('ShaderNodeTexCoord'); sep = self.node('ShaderNodeSeparateXYZ'); self.link(tc.outputs[kind], sep.inputs[0])
        return tc, sep

def closed_outward(bm):
    """Recalculate normals and make sure a closed piece faces out (engines cull back faces)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    cen = sum((v.co for v in bm.verts), Vector()) / max(1, len(bm.verts))
    if sum(f.calc_area() * f.normal.dot(f.calc_center_median() - cen) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.normal_update()
