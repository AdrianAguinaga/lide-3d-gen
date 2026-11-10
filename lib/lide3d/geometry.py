"""bmesh primitives for procedural models. Units: metres; Blender Z = up."""
from math import cos, sin, pi
from mathutils import Vector, Matrix

I4 = Matrix.Identity(4)
TO_X = Matrix.Rotation(pi / 2, 4, "Y")  # maps local +Z onto +X


def Rz(a):
    return Matrix.Rotation(a, 4, "Z")


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def lathe(bm, prof, seg=48, M=I4):
    """Revolve a closed (r, z) profile around Z. r = 0 collapses to a single pole vertex."""
    rings = []
    for r, z in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(M @ Vector((0, 0, z)))] * seg)
        else:
            rings.append([bm.verts.new(M @ Vector((r * cos(2 * pi * k / seg), r * sin(2 * pi * k / seg), z)))
                          for k in range(seg)])
    n = len(prof)
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(seg):
            u = list(dict.fromkeys([a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]]))
            if len(u) >= 3:
                bm.faces.new(u)


def prism(bm, pts, z0, z1, M=I4):
    """Extrude a closed CCW (x, y) polygon from z0 to z1."""
    lo = [bm.verts.new(M @ Vector((x, y, z0))) for x, y in pts]
    hi = [bm.verts.new(M @ Vector((x, y, z1))) for x, y in pts]
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))


def box(bm, x0, x1, y0, y1, z0, z1, M=I4):
    prism(bm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, M)


def loft(bm, rings_pts, cap=True):
    """Skin a list of equal-length closed point loops (e.g. airfoil sections)."""
    rings = [[bm.verts.new(p) for p in pts] for pts in rings_pts]
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    for a, b in zip(rings, rings[1:]):
        m = len(a)
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))


def hull2d(pts):
    """Convex hull (CCW) of 2D points; monotone chain."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def coil(bm, r, wire_r, z0, z1, turns, steps=10, sides=6, M=I4):
    """Helical spring around local Z (closed tube, capped)."""
    n = int(turns * steps) + 1
    rings = []
    for i in range(n):
        a = 2 * pi * i / steps
        z = z0 + (z1 - z0) * i / (n - 1)
        c, rad = Vector((r * cos(a), r * sin(a), z)), Vector((cos(a), sin(a), 0))
        rings.append([bm.verts.new(M @ (c + wire_r * (cos(2 * pi * k / sides) * rad + sin(2 * pi * k / sides) * Vector((0, 0, 1)))))
                      for k in range(sides)])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
