using Google.Protobuf;
using Google.Protobuf.WellKnownTypes;
using Sg = SceneGraph.V1;

static Sg.Vec3 Vec3(double x, double y, double z) => new()
{
    X = x,
    Y = y,
    Z = z
};

static Sg.Pose Pose(string frameId, double x, double y, double z) => new()
{
    FrameId = frameId,
    Transform = new Sg.Transform
    {
        Translation = Vec3(x, y, z),
        Rotation = new Sg.Quaternion { X = 0.0, Y = 0.0, Z = 0.0, W = 1.0 },
        Scale = Vec3(1.0, 1.0, 1.0)
    }
};

static Sg.Bounds BoxBounds(double x, double y, double z) => new()
{
    Box = new Sg.BoxBounds { Size = Vec3(x, y, z) }
};

static Sg.Primitive CylinderPrimitive(double radius, double length, Sg.Axis axis = Sg.Axis.X) => new()
{
    Cylinder = new Sg.CylinderPrimitive
    {
        Radius = radius,
        Length = length,
        Axis = axis
    }
};

static Struct StructFromJson(string json) => JsonParser.Default.Parse<Struct>(json);

static Sg.Node AddNode(
    Sg.SceneGraph scene,
    string id,
    string type,
    string name,
    Sg.GeometryProperties? geometry = null,
    Struct? semantic = null,
    Struct? functional = null,
    Struct? affordance = null)
{
    var node = new Sg.Node
    {
        Id = id,
        Type = type,
        Name = name,
        Properties = new Sg.LayerProperties()
    };

    if (geometry is not null)
    {
        node.Layers.Add(Sg.Layer.Geometry);
        node.Properties.Geometry = geometry;
    }

    if (functional is not null)
    {
        node.Layers.Add(Sg.Layer.Functional);
        node.Properties.Functional = functional;
    }

    if (semantic is not null)
    {
        node.Layers.Add(Sg.Layer.Semantic);
        node.Properties.Semantic = semantic;
    }

    if (affordance is not null)
    {
        node.Layers.Add(Sg.Layer.Affordance);
        node.Properties.Affordance = affordance;
    }

    scene.Nodes.Add(node);
    return node;
}

static Sg.Edge AddEdge(
    Sg.SceneGraph scene,
    string id,
    string type,
    string source,
    string target,
    Sg.Layer layer,
    Struct? properties = null)
{
    var edge = new Sg.Edge
    {
        Id = id,
        Type = type,
        Source = source,
        Target = target,
        Layer = layer
    };

    if (properties is not null)
    {
        edge.Properties = properties;
    }

    scene.Edges.Add(edge);
    return edge;
}

static Sg.SceneGraph BuildScene()
{
    var scene = new Sg.SceneGraph
    {
        Schema = "scenegraph",
        Version = "0.1.0",
        Metadata = new Sg.Metadata
        {
            Name = "C# room example",
            Description = "A small scene built through C# helper functions.",
            Author = "SceneGraph contributors",
            Units = "meter",
            CoordinateSystem = new Sg.CoordinateSystem
            {
                Handedness = Sg.Handedness.Right,
                UpAxis = Sg.Axis.Y
            }
        }
    };

    AddNode(
        scene,
        "room_01",
        "scene",
        "Room",
        geometry: new Sg.GeometryProperties
        {
            Bounds = BoxBounds(4.0, 2.8, 3.5)
        },
        semantic: StructFromJson("""
        {
          "category": "room",
          "attributes": ["indoor"]
        }
        """));

    AddNode(
        scene,
        "door_01",
        "object",
        "Door",
        geometry: new Sg.GeometryProperties
        {
            Pose = Pose("world", 0.0, 1.0, -1.75),
            Bounds = BoxBounds(0.9, 2.0, 0.08)
        },
        semantic: StructFromJson("""
        {
          "category": "door",
          "attributes": ["hinged", "entry"]
        }
        """),
        functional: StructFromJson("""
        {
          "state": { "open": false, "locked": false },
          "mechanism": "hinge"
        }
        """),
        affordance: StructFromJson("""
        {
          "affordances": [
            {
              "action": "open",
              "actor": "human",
              "preconditions": ["door_01.functional.state.locked == false"],
              "effects": ["door_01.functional.state.open = true"]
            }
          ]
        }
        """));

    AddNode(
        scene,
        "handle_01",
        "part",
        "Door handle",
        geometry: new Sg.GeometryProperties
        {
            Pose = Pose("world", 0.35, 1.05, -1.7),
            Primitive = CylinderPrimitive(0.03, 0.16)
        },
        semantic: StructFromJson("""
        {
          "category": "handle"
        }
        """),
        functional: StructFromJson("""
        {
          "function": "latch_control"
        }
        """),
        affordance: StructFromJson("""
        {
          "affordances": [{ "action": "grasp", "actor": "human" }]
        }
        """));

    AddEdge(scene, "edge_room_contains_door", "contains", "room_01", "door_01", Sg.Layer.Geometry);
    AddEdge(scene, "edge_handle_part_of_door", "part_of", "handle_01", "door_01", Sg.Layer.Semantic);
    AddEdge(scene, "edge_handle_controls_door", "controls", "handle_01", "door_01", Sg.Layer.Functional);
    AddEdge(
        scene,
        "edge_door_affords_open",
        "affords",
        "door_01",
        "handle_01",
        Sg.Layer.Affordance,
        StructFromJson("""
        {
          "action": "open"
        }
        """));

    scene.Layers["geometry"] = StructFromJson("""
    {
      "default_coordinate_space": "world"
    }
    """);
    scene.Layers["affordance"] = StructFromJson("""
    {
      "actor_model": "human_adult"
    }
    """);

    return scene;
}

var outputDir = args.Length > 0 ? args[0] : "generated/examples";
Directory.CreateDirectory(outputDir);

var scene = BuildScene();
var binaryPath = Path.Combine(outputDir, "room_from_csharp.scenegraph.pb");
var jsonPath = Path.Combine(outputDir, "room_from_csharp.scenegraph.pb.json");

await File.WriteAllBytesAsync(binaryPath, scene.ToByteArray());
await File.WriteAllTextAsync(jsonPath, JsonFormatter.Default.Format(scene));

Console.WriteLine($"Wrote {binaryPath}");
Console.WriteLine($"Wrote {jsonPath}");
