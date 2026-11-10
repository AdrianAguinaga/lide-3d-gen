// Animates the InlineFour model (models/inline-four-engine): crank, pistons, conrods, camshafts, valves.
// Add to the imported InlineFour_Root. Axes are discovered from the hierarchy (flywheel -> pulley = crank axis,
// world up at Start = cylinder axis), so it does not depend on the FBX/GLB axis conversion.
// The engine must be upright when the scene starts; it can be moved/grabbed afterwards.
using UnityEngine;

public class LideEngineKinematics : MonoBehaviour
{
    [Tooltip("Crank speed. Low values are better for teaching.")] public float rpm = 30f;
    public bool run = true;
    [Tooltip("Flip if the cam lobes rotate away from the tappets they should push.")] public bool reverse;
    [Range(0f, 720f)] public float crankAngle;     // degrees from the exported pose (cyl 1 at compression TDC)

    // model.toml [rig]
    const float R = 0.08150f / 2f, L = 0.130f, LIFT = 0.008f;
    static readonly float[] Cycle = { 0f, 180f, 540f, 360f };       // cycle position of each cylinder at the pose
    const float PeakIntake = 470f, PeakExhaust = 250f;

    Transform crank, cams0, cams1;
    readonly Transform[] pistons = new Transform[4], rods = new Transform[4];
    Quaternion crankRot0, cam0Rot0, cam1Rot0;
    readonly Quaternion[] rodRot0 = new Quaternion[4];
    readonly Vector3[] cylCentre = new Vector3[4];
    readonly float[] throwSign = new float[4];
    Vector3 axis, up;                                                 // root space

    struct Valve { public Transform valve, tappet; public Vector3 pos0, tap0, dir; public int cyl; public float peak, lift0; }
    Valve[] valves;
    LideExplode explode;

    Transform Find(string n)
    {
        foreach (var t in GetComponentsInChildren<Transform>(true)) if (t.name == n) return t;
        Debug.LogError($"LideEngineKinematics: '{n}' not found under {name}", this);
        return null;
    }

    Vector3 P(Transform t) => transform.InverseTransformPoint(t.position);
    Quaternion Rlocal(Transform t) => Quaternion.Inverse(transform.rotation) * t.rotation;

    const float BASE = 0.016f;
    static readonly float[] lobeR = BuildLobe();                      // cam radius every 1 deg from the nose

    static float[] BuildLobe()
    {
        var r = new float[360];
        for (int a = 0; a < 360; a++)
        {
            float d = a > 180 ? a - 360 : a;
            float c = Mathf.Cos(1.5f * d * Mathf.Deg2Rad);
            r[a] = BASE + (Mathf.Abs(d) < 60f ? LIFT * c * c : 0f);
        }
        return r;
    }

    // Flat-tappet lift = support function of the lobe towards the valve (same as build.py tappet_lift).
    static float TappetLift(float deltaDeg)
    {
        float best = 0f;
        for (int a = 0; a < 360; a++) best = Mathf.Max(best, lobeR[a] * Mathf.Cos((a - deltaDeg) * Mathf.Deg2Rad));
        return best - BASE;
    }

    float Lift(int cyl, float peak, float theta) => TappetLift((Cycle[cyl] + theta - peak) / 2f);

    void Start()
    {
        explode = GetComponent<LideExplode>();
        crank = Find("Crank_Assembly");
        var c0 = P(crank);
        axis = (P(Find("Crank_Pulley")) - P(Find("Flywheel"))).normalized;
        up = Vector3.ProjectOnPlane(transform.InverseTransformDirection(Vector3.up), axis).normalized;
        crankRot0 = Rlocal(crank);
        for (int i = 0; i < 4; i++)
        {
            pistons[i] = Find($"Piston_{i + 1:00}");
            rods[i] = Find($"Conrod_{i + 1:00}");
            var pin = P(pistons[i]);
            cylCentre[i] = c0 + axis * Vector3.Dot(pin - c0, axis);
            throwSign[i] = Vector3.Dot(pin - cylCentre[i], up) > L ? 1f : -1f;   // TDC above L, BDC below
            rodRot0[i] = Rlocal(rods[i]);
        }
        cams0 = Find("Camshaft_Intake"); cams1 = Find("Camshaft_Exhaust");
        cam0Rot0 = Rlocal(cams0); cam1Rot0 = Rlocal(cams1);

        var list = new System.Collections.Generic.List<Valve>();
        foreach (var t in GetComponentsInChildren<Transform>(true))
        {
            if (!t.name.StartsWith("Valve_Intake_") && !t.name.StartsWith("Valve_Exhaust_")) continue;
            bool intake = t.name.StartsWith("Valve_Intake_");
            var suffix = t.name.Substring(intake ? 13 : 14);              // e.g. "01A"
            var cam = intake ? cams0 : cams1;
            var p = P(t);
            var onAxis = P(cam) + axis * Vector3.Dot(p - P(cam), axis);
            int cyl = int.Parse(suffix.Substring(0, 2)) - 1;
            float peak = intake ? PeakIntake : PeakExhaust;
            var tap = Find((intake ? "Tappet_Intake_" : "Tappet_Exhaust_") + suffix);
            list.Add(new Valve { valve = t, tappet = tap, pos0 = p, tap0 = P(tap), dir = (onAxis - p).normalized,
                                 cyl = cyl, peak = peak, lift0 = Lift(cyl, peak, 0f) });
        }
        valves = list.ToArray();
    }

    void Update()
    {
        if (explode != null && explode.amount > 0f) return;            // exploded view owns the transforms
        if (run) crankAngle = Mathf.Repeat(crankAngle + rpm * 6f * Time.deltaTime, 720f);
        Apply(crankAngle);
    }

    public void Apply(float theta)
    {
        var sign = reverse ? 1f : -1f;                                // Blender (right-handed) +X spin = Unity -angle
        var q = Quaternion.AngleAxis(sign * theta, axis);
        crank.rotation = transform.rotation * q * crankRot0;
        var qc = Quaternion.AngleAxis(sign * theta / 2f, axis);
        cams0.rotation = transform.rotation * qc * cam0Rot0;
        cams1.rotation = transform.rotation * qc * cam1Rot0;

        for (int i = 0; i < 4; i++)
        {
            var crankPin = cylCentre[i] + q * (up * (throwSign[i] * R));
            var rel = crankPin - cylCentre[i];
            float h = Vector3.Dot(rel, up);
            float lat = Vector3.ProjectOnPlane(rel, up).magnitude;
            var pin = cylCentre[i] + up * (h + Mathf.Sqrt(L * L - lat * lat));
            pistons[i].position = transform.TransformPoint(pin);
            var rod = Quaternion.FromToRotation(-up, (crankPin - pin).normalized) * rodRot0[i];
            rods[i].rotation = transform.rotation * rod;
        }

        foreach (var v in valves)
        {
            var delta = -(Lift(v.cyl, v.peak, theta) - v.lift0) * v.dir; // opening = away from the cam
            v.valve.position = transform.TransformPoint(v.pos0 + delta);
            if (v.tappet) v.tappet.position = transform.TransformPoint(v.tap0 + delta);
        }
    }
}
