// Batchmode check: how Unity actually imports each exported model.
// Invoked by scripts/unity_check.py with -executeMethod LideImportCheck.Run -lideOut <json path>
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class LideImportCheck
{
    [System.Serializable] class Item
    {
        public string file; public int renderers; public int triangles; public int materials; public int textures;
        public float[] size; public float[] rootEuler; public string[] upOfEmpties;
    }
    [System.Serializable] class Report { public string unity; public Item[] items; }

    public static void Run()
    {
        var args = System.Environment.GetCommandLineArgs();
        var outPath = args[System.Array.IndexOf(args, "-lideOut") + 1];
        AssetDatabase.Refresh();
        var items = AssetDatabase.FindAssets("t:Model", new[] { "Assets/Lide" }).Select(guid =>
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));
            var rs = go.GetComponentsInChildren<MeshRenderer>();
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            var mats = rs.SelectMany(r => r.sharedMaterials).Where(m => m).Distinct().ToArray();
            var tex = mats.SelectMany(m => m.GetTexturePropertyNames().Select(m.GetTexture)).Where(t => t).Distinct().Count();
            var it = new Item
            {
                file = Path.GetFileName(path),
                renderers = rs.Length,
                triangles = rs.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3),
                materials = mats.Length,
                textures = tex,
                size = new[] { b.size.x, b.size.y, b.size.z },
                rootEuler = new[] { go.transform.eulerAngles.x, go.transform.eulerAngles.y, go.transform.eulerAngles.z },
                upOfEmpties = go.GetComponentsInChildren<Transform>()
                    .Where(t => t.GetComponent<MeshRenderer>() == null && t != go.transform)
                    .Select(t => t.name + ":" + t.up.ToString("F3")).ToArray(),
            };
            Object.DestroyImmediate(go);
            return it;
        }).ToArray();
        File.WriteAllText(outPath, JsonUtility.ToJson(new Report { unity = Application.unityVersion, items = items }, true));
    }
}
