// Generic exploded view for any LIDE 3D Gen model. Add to the model root; drive `amount` (0..1) from a
// slider, an animation or code. Top-level parts (a mesh whose parent has no mesh) move away from the model
// centre, so children follow their parent (e.g. a piston takes its pin and conrod with it).
using System.Collections.Generic;
using UnityEngine;

public class LideExplode : MonoBehaviour
{
    [Range(0f, 1f)] public float amount;
    [Tooltip("Metres a part travels at amount = 1.")] public float distance = 0.25f;
    [Tooltip("Extra weight on the vertical direction, so stacked parts (head, cover, pan) separate cleanly.")]
    public float verticalBias = 1.5f;

    readonly List<(Transform t, Vector3 local0, Vector3 dir)> parts = new List<(Transform, Vector3, Vector3)>();
    float applied = -1f;

    void Start()
    {
        var rs = GetComponentsInChildren<Renderer>();
        if (rs.Length == 0) return;
        var b = rs[0].bounds;
        foreach (var r in rs) b.Encapsulate(r.bounds);
        foreach (var r in rs)
        {
            var t = r.transform;
            if (t.parent != null && t.parent.GetComponent<Renderer>() != null) continue;  // moves with its parent
            var d = r.bounds.center - b.center;
            d.y *= verticalBias;
            if (d.sqrMagnitude < 1e-6f) d = Vector3.up;
            parts.Add((t, t.localPosition, d.normalized));
        }
    }

    void LateUpdate()
    {
        if (Mathf.Approximately(amount, applied)) return;
        applied = amount;
        foreach (var (t, local0, dir) in parts)
        {
            var worldOffset = dir * (distance * amount);
            t.localPosition = local0 + (t.parent ? t.parent.InverseTransformVector(worldOffset) : worldOffset);
        }
    }
}
