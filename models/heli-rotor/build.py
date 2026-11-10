# HeliRotor: geometry only. Pipeline (reset, validate, export) lives in scripts/build.py.
import bmesh
from math import cos, sin, pi, radians, sqrt, atan2
from lide3d.geometry import lathe, prism, box, loft, Rz, T, TO_X
from lide3d.scene import material

POLES, SLOTS, BLADES = 10, 12, 3
HUB_Z = 0.88
HORN = (0.11, 0.085)  # pitch-horn ball, in grip local X/Y
HORN_R = sqrt(HORN[0] ** 2 + HORN[1] ** 2)
HORN_A = atan2(HORN[1], HORN[0])


def coil_mesh():
    """Rectangular-section winding around one radial tooth."""
    bm = bmesh.new()
    hy, hz, rc, t, dx, xc, zc = 0.018, 0.097, 0.007, 0.012, 0.0145, 0.1515, 0.12
    path = []
    for cy, cz, a0 in [(hy - rc, hz - rc, 0), (-(hy - rc), hz - rc, 90), (-(hy - rc), -(hz - rc), 180),
                       (hy - rc, -(hz - rc), 270)]:
        for i in range(4):
            a = radians(a0 + 30 * i)
            n = (cos(a), sin(a))
            path.append((cy + rc * n[0], cz + rc * n[1], n))
    rings = [[bm.verts.new((xc + sx * dx, y + sn * n[0] * t / 2, zc + z + sn * n[1] * t / 2))
              for sx, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))] for y, z, n in path]
    m = len(rings)
    for i in range(m):
        a, b = rings[i], rings[(i + 1) % m]
        for j in range(4):
            bm.faces.new((a[j], a[(j + 1) % 4], b[(j + 1) % 4], b[j]))
    return bm


def bearing_mesh(z0, z1):
    bm = bmesh.new()
    d = 0.002
    lathe(bm, [(0.0285, z0), (0.034, z0), (0.036, z0 + d), (0.047, z0 + d), (0.049, z0), (0.055, z0),
               (0.055, z1), (0.049, z1), (0.047, z1 - d), (0.036, z1 - d), (0.034, z1), (0.0285, z1)], 32)
    return bm


def bolt_mesh(flip):
    bm = bmesh.new()
    s_ = -1 if flip else 1
    z = -0.02 if flip else 0.26
    lathe(bm, [(0, z + s_ * 0.008), (0.009, z + s_ * 0.008), (0.009, z), (0.005, z), (0.005, z - s_ * 0.035),
               (0, z - s_ * 0.035)], 6, T(0.205))
    return bm


def naca_loop(c, tc, theta, r, sweep):
    n = 8
    xs = [(1 - cos(pi * i / n)) / 2 for i in range(n + 1)]
    half = [5 * tc * (0.2969 * sqrt(x) - 0.126 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4) for x in xs]
    pts = [(x, h) for x, h in zip(xs, half)] + [(xs[i], -half[i]) for i in range(n - 1, 0, -1)]
    out = []
    for x, h in pts:
        y, z = (0.25 - x) * c + sweep, h * c  # leading edge on +Y: rotor turns CCW seen from above
        out.append((r, y * cos(theta) - z * sin(theta), y * sin(theta) + z * cos(theta)))
    return out


def blade_mesh():
    secs = [(0.225, 0.08, 0.40, 0.0, 0.0), (0.30, 0.08, 0.40, 0.0, 0.0), (0.38, 0.15, 0.26, 3.0, 0.0)]
    for r in (0.47, 0.8, 1.2, 1.7, 2.2, 2.7, 3.2, 3.38):
        secs.append((r, 0.22, 0.15 if r < 0.5 else 0.12, 6 - 8 * (r - 0.47) / 3.03, 0.0))
    secs += [(3.46, 0.17, 0.10, -1.9, -0.03), (3.5, 0.08, 0.06, -2.0, -0.085)]
    bm = bmesh.new()
    loft(bm, [naca_loop(c, tc, radians(th), r, sw) for r, c, tc, th, sw in secs])
    return bm


def build(m):
    STEEL = material("M_Steel", (0.62, 0.63, 0.65), 1.0, 0.35)
    ALU = material("M_Aluminium", (0.78, 0.79, 0.80), 1.0, 0.5)
    LAM = material("M_Lamination", (0.10, 0.11, 0.13), 0.9, 0.45)
    COPPER = material("M_Copper", (0.85, 0.42, 0.18), 1.0, 0.35)
    MAG_N = material("M_Magnet_N", (0.70, 0.06, 0.05), 0.2, 0.4)
    MAG_S = material("M_Magnet_S", (0.05, 0.16, 0.70), 0.2, 0.4)
    BLADE = material("M_Blade", (0.86, 0.87, 0.88), 0.0, 0.45)

    root = m.group("HeliRotor_Root")
    fixed = m.group("Stationary_Assembly", root)
    spin = m.group("Rotating_Assembly", root)

    # ---- motor: stationary
    bm = bmesh.new()
    lathe(bm, [(0.195, 0.0), (0.215, 0.0), (0.215, 0.24), (0.195, 0.24)])
    for k in range(24):
        box(bm, 0.214, 0.232, -0.0025, 0.0025, 0.02, 0.22, Rz(2 * pi * (k + 0.5) / 24))
    m.part("Motor_Housing", bm, ALU, fixed)

    bm = bmesh.new()
    lathe(bm, [(0, -0.02), (0.215, -0.02), (0.215, 0), (0.06, 0), (0.06, 0.03), (0.056, 0.03), (0.056, 0.008),
               (0, 0.008)])
    m.part("Motor_EndBell_Lower", bm, ALU, fixed)

    bm = bmesh.new()
    lathe(bm, [(0.032, 0.26), (0.215, 0.26), (0.215, 0.24), (0.06, 0.24), (0.06, 0.21), (0.056, 0.21),
               (0.056, 0.232), (0.032, 0.232)])
    m.part("Motor_EndBell_Upper", bm, ALU, fixed)

    # stator core: yoke ring plus T-shaped teeth, one shoe arc per slot
    bm = bmesh.new()
    lathe(bm, [(0.170, 0.03), (0.195, 0.03), (0.195, 0.21), (0.170, 0.21)])
    w, s, rt = 0.011, 0.030, 0.125
    arc = [(sqrt(rt * rt - y * y), y) for y in [s * t / 4 for t in range(-4, 5)]]
    tooth = [(0.175, -w), (0.133, -w), (0.131, -s)] + arc + [(0.131, s), (0.133, w), (0.175, w)]
    for k in range(SLOTS):
        prism(bm, tooth, 0.03, 0.21, Rz(2 * pi * k / SLOTS))
    m.part("Stator_Core", bm, LAM, fixed)

    for k in range(SLOTS):
        m.part(f"Stator_Coil_{k + 1:02d}", coil_mesh(), COPPER, fixed, angle=2 * pi * k / SLOTS)

    m.part("Bearing_Lower", bearing_mesh(0.01, 0.03), STEEL, fixed)
    m.part("Bearing_Upper", bearing_mesh(0.21, 0.232), STEEL, fixed)

    for k in range(8):
        a = 2 * pi * (k + 0.5) / 8
        m.part(f"Bolt_Upper_{k + 1:02d}", bolt_mesh(False), STEEL, fixed, angle=a)
        m.part(f"Bolt_Lower_{k + 1:02d}", bolt_mesh(True), STEEL, fixed, angle=a)

    bm = bmesh.new()
    lathe(bm, [(0.036, 0.465), (0.095, 0.465), (0.095, 0.49), (0.036, 0.49)])
    m.part("Swashplate_Lower", bm, ALU, fixed)

    # ---- rotating
    bm = bmesh.new()
    lathe(bm, [(0, 0.01), (0.028, 0.01), (0.028, 0.84), (0.022, 0.845), (0.022, 0.98), (0.018, 0.985), (0, 0.985)])
    m.part("Main_Shaft", bm, STEEL, spin)

    bm = bmesh.new()
    lathe(bm, [(0.028, 0.035), (0.108, 0.035), (0.108, 0.205), (0.028, 0.205)])
    m.part("Rotor_Yoke", bm, LAM, spin)

    span = radians(360 / POLES * 0.84)
    for k in range(POLES):
        bm = bmesh.new()
        angs = [-span / 2 + span * i / 5 for i in range(6)]
        pts = [(0.108 * cos(a), 0.108 * sin(a)) for a in angs] + \
              [(0.122 * cos(a), 0.122 * sin(a)) for a in reversed(angs)]
        prism(bm, pts, 0.037, 0.203)
        pole = "N" if k % 2 == 0 else "S"
        m.part(f"Magnet_{k + 1:02d}_{pole}", bm, MAG_N if pole == "N" else MAG_S, spin, angle=2 * pi * k / POLES)

    bm = bmesh.new()
    lathe(bm, [(0.036, 0.492), (0.08, 0.492), (0.08, 0.515), (0.036, 0.515)])
    for b in range(BLADES):
        box(bm, 0.07, 0.15, -0.012, 0.012, 0.497, 0.512, Rz(2 * pi * b / BLADES + HORN_A))
    m.part("Swashplate_Upper", bm, ALU, spin, pivot=(0, 0, 0.5035))  # 3 arms: bounds centre is off-axis

    bm = bmesh.new()
    lathe(bm, [(0.022, HUB_Z - 0.03), (0.06, HUB_Z - 0.03), (0.06, HUB_Z + 0.03), (0.022, HUB_Z + 0.03)])
    for b in range(BLADES):
        lathe(bm, [(0, 0.05), (0.024, 0.05), (0.024, 0.14), (0, 0.14)], 16,
              Rz(2 * pi * b / BLADES) @ T(z=HUB_Z) @ TO_X)
    m.part("Rotor_Hub", bm, STEEL, spin, pivot=(0, 0, HUB_Z))

    bm = bmesh.new()
    lathe(bm, [(0.022, HUB_Z + 0.04), (0.034, HUB_Z + 0.04), (0.034, HUB_Z + 0.065), (0.022, HUB_Z + 0.065)], 6)
    m.part("Hub_Nut", bm, STEEL, spin)

    for b in range(BLADES):
        a = 2 * pi * b / BLADES
        tag = f"{b + 1:02d}"

        bm = bmesh.new()
        lathe(bm, [(0.0245, 0.10), (0.036, 0.10), (0.036, 0.215), (0, 0.215), (0, 0.14), (0.0245, 0.14)], 24, TO_X)
        box(bm, 0.205, 0.30, -0.045, 0.045, 0.018, 0.028)
        box(bm, 0.205, 0.30, -0.045, 0.045, -0.028, -0.018)
        box(bm, HORN[0] - 0.01, HORN[0] + 0.01, 0.02, HORN[1] + 0.01, -0.008, 0.008)
        m.part(f"Blade_Grip_{tag}", bm, ALU, spin, angle=a, pivot=(0.10, 0, 0), offset=(0, 0, HUB_Z))

        m.part(f"Blade_{tag}", blade_mesh(), BLADE, spin, angle=a, pivot=(0.26, 0, 0), offset=(0, 0, HUB_Z))

        bm = bmesh.new()
        lathe(bm, [(0, -0.036), (0.012, -0.036), (0.012, -0.029), (0.006, -0.029), (0.006, 0.029), (0.012, 0.029),
                   (0.012, 0.036), (0, 0.036)], 12, T(0.26))
        m.part(f"Blade_Bolt_{tag}", bm, STEEL, spin, angle=a, offset=(0, 0, HUB_Z))

        bm = bmesh.new()
        lathe(bm, [(0, 0.508), (0.01, 0.515), (0.01, 0.53), (0.006, 0.54), (0.006, 0.845), (0.01, 0.855),
                   (0.01, 0.872), (0, 0.88)], 10, T(HORN_R))
        m.part(f"Pitch_Link_{tag}", bm, STEEL, spin, angle=a + HORN_A)
