# InlineFour: educational cutaway inline-4 (DOHC, 16 valves). Geometry only; see model.toml for the rig.
# Frame: crank axis = X (front +X), cylinders up (+Z), crank centre at the root origin; root sits so the
# oil pan rests on the ground. Cutaway: block and pan sectioned at y = 0, head and valve cover at the intake
# valve line, so pistons, crank, valves and cams are visible. Moving parts are whole objects.
import bmesh
from math import cos, sin, pi, radians, sqrt
from mathutils import Matrix
from lide3d.geometry import lathe, prism, box, coil, hull2d, T, TO_X
TO_Y = Matrix.Rotation(-pi / 2, 4, "X")  # maps local +Z onto +Y
from lide3d.scene import material

BORE_R, STROKE, ROD, PITCH = 0.0395, 0.0815, 0.130, 0.088
CR = STROKE / 2
CX = [(-1.5 + i) * PITCH for i in range(4)]
THROW = [0.0, pi, pi, 0.0]               # crank angle per cylinder at this pose (cyl 1 at TDC)
CYCLE = [0, 180, 540, 360]               # degrees into the 4-stroke cycle (0 = compression TDC); firing 1-3-4-2
PIN_UP, SKIRT = 0.030, 0.025             # piston crown above / skirt below the pin
DECK = CR + ROD + PIN_UP + 0.0005        # block deck height above the crank axis
PAN_Z = -0.165                           # oil pan bottom (ground)
HEAD_H, COVER_H = 0.125, 0.06
SEAT_Y, SEAT_Z = 0.017, DECK + 0.005    # valve heads in the chamber roof
TILT = radians(15)                       # pent-roof: valve axes lean outwards
CAM_S = 0.113                            # cam axis distance from the seat, along the valve axis
VALVE_DX = 0.0165
VALVES = {"Intake": (1, 0.0145, 470), "Exhaust": (-1, 0.0125, 250)}  # side (+y/-y), head radius, peak-lift cycle deg
BASE_R, LIFT = 0.016, 0.008


def valve_frame(side, x=0.0):
    """Local frame of a valve: origin at the seat, +Z along the valve axis (tilted outwards)."""
    return T(x, side * SEAT_Y, SEAT_Z) @ Matrix.Rotation(-side * TILT, 4, "X")


def cam_axis(side):
    return side * (SEAT_Y + CAM_S * sin(TILT)), SEAT_Z + CAM_S * cos(TILT)


def pin_z(t):
    return CR * cos(t) + sqrt(ROD ** 2 - (CR * sin(t)) ** 2)


def along_x(bm, prof, x0, y=0.0, z=0.0, seg=32):
    """Lathe a (radius, x-offset) profile around an axis parallel to X through (x0, y, z)."""
    lathe(bm, prof, seg, T(x0, y, z) @ TO_X)


def disc_x(bm, r, xa, xb, y=0.0, z=0.0, seg=32, ri=0.0):
    along_x(bm, [(ri, xa), (r, xa), (r, xb), (ri, xb)], 0.0, y, z, seg)


def prism_x(bm, yz, xa, xb):
    """Extrude a (y, z) outline along X."""
    prism(bm, [(-z, y) for y, z in yz], xa, xb, TO_X)


def cyl_z(bm, r, za, zb, x=0.0, y=0.0, seg=32):
    lathe(bm, [(0, za), (r, za), (r, zb), (0, zb)], seg, T(x, y))


def solid_box(*a):
    bm = bmesh.new()
    box(bm, *a)
    return bm


def solid_cyl_z(*a, **k):
    bm = bmesh.new()
    cyl_z(bm, *a, **k)
    return bm


def solid_cyl_x(r, xa, xb, y, z, seg=32):
    bm = bmesh.new()
    disc_x(bm, r, xa, xb, y, z, seg)
    return bm


def lobe_r(d):
    """Cam radius at angle d (rad) from the nose."""
    d = (d + pi) % (2 * pi) - pi
    return BASE_R + (LIFT * cos(d * 1.5) ** 2 if abs(d) < radians(60) else 0.0)


def tappet_lift(d):
    """Lift of a flat tappet when the valve lies at angle d from the nose: the lobe's support function
    (furthest extent towards the valve), not its radius at that angle."""
    return max(lobe_r(a) * cos(a - d) for a in [2 * pi * j / 360 for j in range(360)]) - BASE_R


def nose_angle(cyl, side, peak):
    """Cam nose direction in the (y, z) plane (0 = +z, pi/2 = +y) for this pose; pi + side*TILT points at the valve."""
    return pi + side * TILT - radians(CYCLE[cyl] - peak) / 2


def build(m):
    IRON = material("M_CastIron", (0.32, 0.33, 0.35), 0.6, 0.6)
    ALU = material("M_Aluminium", (0.78, 0.79, 0.80), 1.0, 0.45)
    STEEL = material("M_Steel", (0.62, 0.63, 0.65), 1.0, 0.3)
    CUT = material("M_Cutaway", (0.85, 0.12, 0.08), 0.0, 0.5)
    COVER = material("M_ValveCover", (0.08, 0.08, 0.09), 0.2, 0.6)
    PAN = material("M_OilPan", (0.12, 0.12, 0.13), 0.5, 0.5)
    PLUG = material("M_Ceramic", (0.92, 0.92, 0.90), 0.0, 0.3)
    RUBBER = material("M_Rubber", (0.05, 0.05, 0.05), 0.0, 0.8)

    root = m.group("InlineFour_Root")
    root.location.z = -PAN_Z
    fixed = m.group("Stationary_Assembly", root)
    crank = m.group("Crank_Assembly", root)
    valvetrain = m.group("Valvetrain", root)

    # ---------------- stationary, sectioned
    cutaway_front = lambda y: solid_box(-0.4, 0.4, -0.4, y, -0.4, 0.6)

    def head_section():
        """Section plane through the (tilted) intake valve axes."""
        bm = bmesh.new()
        box(bm, -0.4, 0.4, -0.4, 0.0, -0.3, 0.4, valve_frame(1))
        return bm

    bm = bmesh.new()
    box(bm, -0.215, 0.215, -0.085, 0.085, -0.045, DECK)
    cuts = [cutaway_front(0.0), solid_cyl_x(0.0255, -0.25, 0.25, 0, 0)]
    for x in CX:
        cuts.append(solid_cyl_z(BORE_R, 0.055, DECK + 0.01, x))
        cuts.append(solid_box(x - 0.034, x + 0.034, -0.07, 0.07, -0.06, 0.075))
    m.part("Engine_Block", bm, IRON, fixed, cut=cuts, cut_mat=CUT)

    bm = bmesh.new()
    box(bm, -0.215, 0.215, -0.085, 0.085, DECK, DECK + HEAD_H)
    cuts = [head_section(), solid_box(-0.195, 0.195, -0.072, 0.072, DECK + 0.085, DECK + HEAD_H + 0.01)]
    for s in (1, -1):
        cuts.append(solid_cyl_x(0.0136, -0.25, 0.25, *cam_axis(s)))
    for x in CX:
        cuts.append(solid_cyl_z(BORE_R, DECK - 0.01, DECK + 0.008, x))                  # combustion chamber
        cuts.append(solid_cyl_z(0.0095, DECK + 0.006, DECK + 0.095, x, 0.0, 24))        # spark plug well
        for side in (1, -1):
            cuts.append(solid_box(x - 0.028, x + 0.028, side * 0.012, side * 0.1, DECK + 0.016, DECK + 0.040)
                        if side > 0 else solid_box(x - 0.028, x + 0.028, -0.1, -0.012, DECK + 0.016, DECK + 0.040))
        for s, vr, _ in VALVES.values():
            for dx in (-VALVE_DX, VALVE_DX):
                M = valve_frame(s, x + dx)
                for r, za, zb, seg in ((vr - 0.001, -0.001, 0.025, 24), (0.0045, 0.015, 0.045, 12), (0.016, 0.04, 0.14, 24)):
                    c = bmesh.new()                                   # throat, guide, spring/bucket bore
                    lathe(c, [(0, za), (r, za), (r, zb), (0, zb)], seg, M)
                    cuts.append(c)
    m.part("Cylinder_Head", bm, ALU, fixed, cut=cuts, cut_mat=CUT)

    bm = bmesh.new()
    box(bm, -0.21, 0.21, -0.08, 0.08, DECK + HEAD_H, DECK + HEAD_H + COVER_H)
    m.part("Valve_Cover", bm, COVER, fixed, cut=[
        solid_box(-0.205, 0.205, -0.075, 0.075, DECK + HEAD_H - 0.01, DECK + HEAD_H + COVER_H - 0.005),
        head_section()], cut_mat=CUT)

    bm = bmesh.new()
    box(bm, -0.205, 0.205, -0.085, 0.085, PAN_Z, -0.045)
    m.part("Oil_Pan", bm, PAN, fixed, cut=[
        solid_box(-0.201, 0.201, -0.081, 0.081, PAN_Z + 0.004, -0.04), cutaway_front(0.0)], cut_mat=CUT)

    for i, x in enumerate(CX):
        bm = bmesh.new()
        D = DECK
        lathe(bm, [(0, D + 0.004), (0.0035, D + 0.004), (0.0035, D + 0.008), (0.007, D + 0.008), (0.007, D + 0.027),
                   (0.0105, D + 0.027), (0.0105, D + 0.04), (0.0065, D + 0.04), (0.0065, D + 0.085), (0, D + 0.085)],
              12, T(x))
        m.part(f"Spark_Plug_{i + 1:02d}", bm, PLUG, fixed)

    # ---------------- crank train (pivots on the crank axis)
    bm = bmesh.new()
    disc_x(bm, 0.045, -0.215, -0.205)                                   # rear flange
    edges = [-0.205] + [e for x in CX for e in (x - 0.027, x + 0.027)] + [0.215]
    for xa, xb in zip(edges[0::2], edges[1::2]):
        disc_x(bm, 0.025, xa, xb)                                       # main journals
    disc_x(bm, 0.018, 0.215, 0.27)                                      # snout
    for x, t in zip(CX, THROW):
        py, pz = CR * sin(t), CR * cos(t)
        disc_x(bm, 0.0215, x - 0.012, x + 0.012, py, pz)                # crank pin
        web = [(py + 0.03 * cos(a), pz + 0.03 * sin(a)) for a in [2 * pi * k / 16 for k in range(16)]]
        web += [(0.03 * cos(a), 0.03 * sin(a)) for a in [2 * pi * k / 16 for k in range(16)]]
        web += [(0.062 * sin(t + pi + d), 0.062 * cos(t + pi + d)) for d in [radians(-65 + 13 * k) for k in range(11)]]
        web = hull2d(web)
        prism_x(bm, web, x - 0.027, x - 0.011)
        prism_x(bm, web, x + 0.011, x + 0.027)
    m.part("Crankshaft", bm, STEEL, crank, pivot=(0, 0, 0))

    bm = bmesh.new()
    along_x(bm, [(0.018, -0.245), (0.14, -0.245), (0.14, -0.225), (0.05, -0.225), (0.05, -0.215), (0.018, -0.215)], 0.0, seg=64)
    m.part("Flywheel", bm, STEEL, crank, pivot=(0, 0, 0))

    bm = bmesh.new()
    disc_x(bm, 0.0225, 0.222, 0.236, ri=0.018)
    m.part("Crank_Sprocket", bm, STEEL, crank, pivot=(0, 0, 0))

    bm = bmesh.new()
    along_x(bm, [(0.018, 0.24), (0.065, 0.24), (0.065, 0.247), (0.058, 0.251), (0.065, 0.255), (0.065, 0.262),
                 (0.018, 0.262)], 0.0, seg=48)
    m.part("Crank_Pulley", bm, STEEL, crank, pivot=(0, 0, 0))

    # ---------------- cylinders: piston (slides) > pin, conrod (swings about the pin)
    for i, (x, t) in enumerate(zip(CX, THROW)):
        tag = f"{i + 1:02d}"
        cyl = m.group(f"Cylinder_{tag}", root)
        cyl.location.x = x

        bm = bmesh.new()
        prof = [(0.034, -SKIRT), (0.0393, -SKIRT)]
        for g in (0.012, 0.018, 0.024):                                 # three ring grooves
            prof += [(0.0393, g), (0.0378, g), (0.0378, g + 0.002), (0.0393, g + 0.002)]
        prof += [(0.0393, PIN_UP), (0, PIN_UP), (0, 0.022), (0.034, 0.022)]
        lathe(bm, prof, 32)
        for s in (-1, 1):
            box(bm, s * 0.022, s * 0.0345, -0.012, 0.012, -0.012, 0.012) if s > 0 else \
                box(bm, -0.0345, -0.022, -0.012, 0.012, -0.012, 0.012)  # pin bosses
        piston = m.part(f"Piston_{tag}", bm, ALU, cyl, pivot=(0, 0, 0), offset=(0, 0, pin_z(t)))

        bm = bmesh.new()
        disc_x(bm, 0.0095, -0.032, 0.032, ri=0.006, seg=16)
        m.part(f"Piston_Pin_{tag}", bm, STEEL, piston, pivot=(0, 0, 0))

        bm = bmesh.new()
        disc_x(bm, 0.0145, -0.01, 0.01, ri=0.0095, seg=24)              # small end
        disc_x(bm, 0.033, -0.0105, 0.0105, z=-ROD, ri=0.0215, seg=32)   # big end
        box(bm, -0.007, 0.007, -0.009, 0.009, -ROD + 0.03, -0.012)      # beam
        m.part(f"Conrod_{tag}", bm, STEEL, piston, pivot=(0, 0, 0))

    # ---------------- valvetrain
    for side, (s, vr, peak) in VALVES.items():
        cy, cz = cam_axis(s)
        bm = bmesh.new()
        disc_x(bm, 0.012, -0.2, 0.215, cy, cz, 16)                      # shaft
        disc_x(bm, 0.045, 0.222, 0.236, cy, cz, 48)                     # sprocket (2:1 to the crank)
        for k, x in enumerate(CX):
            n = nose_angle(k, s, peak)
            out = [(cy + lobe_r(a - n) * sin(a), cz + lobe_r(a - n) * cos(a)) for a in [2 * pi * j / 36 for j in range(36)]]
            for dx in (-VALVE_DX, VALVE_DX):
                prism_x(bm, out, x + dx - 0.007, x + dx + 0.007)
            disc_x(bm, 0.0135, x + PITCH / 2 - 0.007, x + PITCH / 2 + 0.007, cy, cz, 16)  # journal
        m.part(f"Camshaft_{side}", bm, STEEL, valvetrain, pivot=(0, cy, cz))

        for k, x in enumerate(CX):
            lift = tappet_lift(pi + s * TILT - nose_angle(k, s, peak))      # along the valve axis
            for ab, dx in (("A", -VALVE_DX), ("B", VALVE_DX)):
                tag, M, z0 = f"{side}_{k + 1:02d}{ab}", valve_frame(s, x + dx), -lift
                top = CAM_S - BASE_R - lift                               # bucket top touches the cam base circle
                bm = bmesh.new()
                lathe(bm, [(0, z0), (vr, z0), (vr, z0 + 0.0015), (vr - 0.002, z0 + 0.003), (0.0045, z0 + 0.010),
                           (0.0028, z0 + 0.016), (0.0028, top - 0.004), (0, top - 0.004)], 16, M)
                m.part(f"Valve_{tag}", bm, STEEL, valvetrain)
                bm = bmesh.new()
                coil(bm, 0.011, 0.0018, 0.045, top - 0.014, 4, 10, 6, M)
                m.part(f"Valve_Spring_{tag}", bm, STEEL, valvetrain)
                bm = bmesh.new()
                lathe(bm, [(0.003, top - 0.014), (0.015, top - 0.014), (0.015, top), (0, top), (0, top - 0.003),
                           (0.003, top - 0.003)], 24, M)
                m.part(f"Tappet_{tag}", bm, STEEL, valvetrain)

    # ---------------- timing belt (static loop around the three sprockets) and intake manifold
    circles = [(0.0, 0.0, 0.0225)] + [(*cam_axis(s), 0.045) for s in (1, -1)]
    loop = lambda grow: hull2d([(cy + (r + grow) * cos(a), cz + (r + grow) * sin(a))
                                for cy, cz, r in circles for a in [2 * pi * k / 48 for k in range(48)]])
    bm = bmesh.new()
    prism_x(bm, loop(0.004), 0.2235, 0.2345)
    inner = bmesh.new()
    prism_x(inner, loop(0.0005), 0.22, 0.24)
    m.part("Timing_Belt", bm, RUBBER, fixed, cut=[inner], cut_mat=RUBBER)

    PZ, PY = DECK + 0.028, 0.19                                         # intake port centre height, plenum y
    bm = bmesh.new()
    cuts = [solid_cyl_x(0.031, -0.186, 0.186, PY, PZ), solid_cyl_x(0.021, 0.15, 0.26, PY, PZ)]
    for x in CX:
        lathe(bm, [(0, 0.085), (0.019, 0.085), (0.019, PY), (0, PY)], 24, T(x, 0, PZ) @ TO_Y)   # runner
        c = bmesh.new()
        lathe(c, [(0, 0.07), (0.015, 0.07), (0.015, PY), (0, PY)], 24, T(x, 0, PZ) @ TO_Y)
        cuts.append(c)
    disc_x(bm, 0.035, -0.19, 0.19, PY, PZ, 32)                         # plenum
    disc_x(bm, 0.025, 0.19, 0.25, PY, PZ, 32)                          # throttle body
    m.part("Intake_Manifold", bm, ALU, fixed, cut=cuts, cut_mat=ALU)
