# Usage Examples

The generated Protobuf classes are the cross-language contract, but raw generated
code should not be the main authoring experience. In real code, put a small
facade around them so scene construction reads like scene construction rather
than generated API plumbing.

## Generate Bindings First

```powershell
python tools/generate_protos.py
```

This creates `generated/python` and `generated/cpp`.

## Python

Run:

```powershell
python examples/python/build_room.py
```

The example builds a room scene and writes:

```text
generated/examples/room_from_python.scenegraph.pb
generated/examples/room_from_python.scenegraph.pb.json
```

The important pattern is to use typed geometry helpers and hide
`google.protobuf.Struct` handling for the flexible layers:

```python
def add_node(scene, *, node_id, node_type, name, geometry_properties=None, semantic=None):
    node = scene.nodes.add()
    node.id = node_id
    node.type = node_type
    node.name = name
    if geometry_properties is not None:
        node.properties.geometry.CopyFrom(geometry_properties)
    set_struct(node.properties.semantic, semantic)
    return node
```

Application code can then stay readable:

```python
add_node(
    scene,
    node_id="door_01",
    node_type="object",
    name="Door",
    geometry_properties=geometry(
        node_pose=pose(frame_id="world", translation=(0.0, 1.0, -1.75)),
        bounds=box_bounds((0.9, 2.0, 0.08)),
    ),
    semantic={"category": "door"},
)
```

## C++

Build:

```bash
cmake -S examples/cpp -B build/examples-cpp -DGENERATED_CPP_DIR="$PWD/generated/cpp"
cmake --build build/examples-cpp
```

Run:

```bash
./build/examples-cpp/build_room generated/examples
```

The example writes:

```text
generated/examples/room_from_cpp.scenegraph.pb
generated/examples/room_from_cpp.scenegraph.pb.json
```

The C++ example uses helper functions for the generated API:

```cpp
auto* door = AddNode(
    &scene,
    "door_01",
    "object",
    "Door",
    {sg::LAYER_GEOMETRY, sg::LAYER_SEMANTIC});
```

For flexible layer properties, it also uses JSON snippets to populate
`google.protobuf.Struct`. Geometry itself is typed:

```cpp
auto* door_geometry = door->mutable_properties()->mutable_geometry();
SetPose(door_geometry, "world", 0.0, 1.0, -1.75);
SetBoxBounds(door_geometry, 0.9, 2.0, 0.08);
```

Semantic, functional, and affordance data can stay flexible while the vocabulary
is still evolving:

```cpp
door->mutable_properties()->mutable_semantic()->CopyFrom(StructFromJson(R"json({
  "category": "door",
  "attributes": ["hinged", "entry"]
})json"));
```

## Recommendation

Use generated Protobuf classes at system boundaries:

- file loading and saving
- network messages
- C++/Python interchange
- validation of the shared contract

Use small domain helpers or wrappers inside application code. If the helpers
start becoming stable, they can graduate into a real `scenegraph` runtime
library for Python and C++.
