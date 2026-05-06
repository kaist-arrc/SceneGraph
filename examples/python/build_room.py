from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct


ROOT = Path(__file__).resolve().parents[2]
GENERATED_PYTHON = ROOT / "generated" / "python"

if not GENERATED_PYTHON.exists():
    raise SystemExit(
        "Generated Python bindings were not found. Run "
        "`python tools/generate_protos.py --language python` first."
    )

sys.path.insert(0, str(GENERATED_PYTHON))
import scenegraph_pb2  # noqa: E402


LAYER = {
    "geometry": scenegraph_pb2.LAYER_GEOMETRY,
    "functional": scenegraph_pb2.LAYER_FUNCTIONAL,
    "semantic": scenegraph_pb2.LAYER_SEMANTIC,
    "affordance": scenegraph_pb2.LAYER_AFFORDANCE,
}


def to_struct(value: dict[str, Any]) -> Struct:
    result = Struct()
    result.update(value)
    return result


def set_struct(target: Struct, value: dict[str, Any] | None) -> None:
    if value is not None:
        target.CopyFrom(to_struct(value))


def vec3(x: float, y: float, z: float) -> scenegraph_pb2.Vec3:
    return scenegraph_pb2.Vec3(x=x, y=y, z=z)


def quaternion(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    w: float = 1.0,
) -> scenegraph_pb2.Quaternion:
    return scenegraph_pb2.Quaternion(x=x, y=y, z=z, w=w)


def pose(
    *,
    frame_id: str,
    translation: tuple[float, float, float],
    rotation_xyzw: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> scenegraph_pb2.Pose:
    result = scenegraph_pb2.Pose(frame_id=frame_id)
    result.transform.translation.CopyFrom(vec3(*translation))
    result.transform.rotation.CopyFrom(quaternion(*rotation_xyzw))
    result.transform.scale.CopyFrom(vec3(*scale))
    return result


def box_bounds(size: tuple[float, float, float]) -> scenegraph_pb2.Bounds:
    result = scenegraph_pb2.Bounds()
    result.box.size.CopyFrom(vec3(*size))
    return result


def cylinder_primitive(
    *,
    radius: float,
    length: float,
    axis: int = scenegraph_pb2.AXIS_X,
) -> scenegraph_pb2.Primitive:
    result = scenegraph_pb2.Primitive()
    result.cylinder.radius = radius
    result.cylinder.length = length
    result.cylinder.axis = axis
    return result


def geometry(
    *,
    node_pose: scenegraph_pb2.Pose | None = None,
    bounds: scenegraph_pb2.Bounds | None = None,
    primitive: scenegraph_pb2.Primitive | None = None,
    mesh_uri: str | None = None,
) -> scenegraph_pb2.GeometryProperties:
    result = scenegraph_pb2.GeometryProperties()
    if node_pose is not None:
        result.pose.CopyFrom(node_pose)
    if bounds is not None:
        result.bounds.CopyFrom(bounds)
    if primitive is not None:
        result.primitive.CopyFrom(primitive)
    if mesh_uri is not None:
        result.mesh_uri = mesh_uri
    return result


def add_node(
    scene: scenegraph_pb2.SceneGraph,
    *,
    node_id: str,
    node_type: str,
    name: str,
    geometry_properties: scenegraph_pb2.GeometryProperties | None = None,
    functional: dict[str, Any] | None = None,
    semantic: dict[str, Any] | None = None,
    affordance: dict[str, Any] | None = None,
) -> scenegraph_pb2.Node:
    node = scene.nodes.add()
    node.id = node_id
    node.type = node_type
    node.name = name

    layer_values = {
        "geometry": geometry_properties,
        "functional": functional,
        "semantic": semantic,
        "affordance": affordance,
    }
    node.layers.extend(
        LAYER[layer] for layer, value in layer_values.items() if value is not None
    )

    if geometry_properties is not None:
        node.properties.geometry.CopyFrom(geometry_properties)
    set_struct(node.properties.functional, functional)
    set_struct(node.properties.semantic, semantic)
    set_struct(node.properties.affordance, affordance)
    return node


def add_edge(
    scene: scenegraph_pb2.SceneGraph,
    *,
    edge_id: str,
    edge_type: str,
    source: str,
    target: str,
    layer: str,
    properties: dict[str, Any] | None = None,
) -> scenegraph_pb2.Edge:
    edge = scene.edges.add()
    edge.id = edge_id
    edge.type = edge_type
    edge.source = source
    edge.target = target
    edge.layer = LAYER[layer]
    set_struct(edge.properties, properties)
    return edge


def build_scene() -> scenegraph_pb2.SceneGraph:
    scene = scenegraph_pb2.SceneGraph(schema="scenegraph", version="0.1.0")
    scene.metadata.name = "Python room example"
    scene.metadata.description = "A small scene built through a friendly Python facade."
    scene.metadata.author = "SceneGraph contributors"
    scene.metadata.units = "meter"
    scene.metadata.coordinate_system.handedness = scenegraph_pb2.HANDEDNESS_RIGHT
    scene.metadata.coordinate_system.up_axis = scenegraph_pb2.AXIS_Y

    add_node(
        scene,
        node_id="room_01",
        node_type="scene",
        name="Room",
        geometry_properties=geometry(bounds=box_bounds((4.0, 2.8, 3.5))),
        semantic={"category": "room", "attributes": ["indoor"]},
    )

    add_node(
        scene,
        node_id="door_01",
        node_type="object",
        name="Door",
        geometry_properties=geometry(
            node_pose=pose(frame_id="world", translation=(0.0, 1.0, -1.75)),
            bounds=box_bounds((0.9, 2.0, 0.08)),
        ),
        semantic={"category": "door", "attributes": ["hinged", "entry"]},
        functional={"state": {"open": False, "locked": False}, "mechanism": "hinge"},
        affordance={
            "affordances": [
                {
                    "action": "open",
                    "actor": "human",
                    "preconditions": ["door_01.functional.state.locked == false"],
                    "effects": ["door_01.functional.state.open = true"],
                }
            ]
        },
    )

    add_node(
        scene,
        node_id="handle_01",
        node_type="part",
        name="Door handle",
        geometry_properties=geometry(
            node_pose=pose(frame_id="world", translation=(0.35, 1.05, -1.7)),
            primitive=cylinder_primitive(radius=0.03, length=0.16),
        ),
        semantic={"category": "handle"},
        functional={"function": "latch_control"},
        affordance={"affordances": [{"action": "grasp", "actor": "human"}]},
    )

    add_edge(
        scene,
        edge_id="edge_room_contains_door",
        edge_type="contains",
        source="room_01",
        target="door_01",
        layer="geometry",
    )
    add_edge(
        scene,
        edge_id="edge_handle_part_of_door",
        edge_type="part_of",
        source="handle_01",
        target="door_01",
        layer="semantic",
    )
    add_edge(
        scene,
        edge_id="edge_handle_controls_door",
        edge_type="controls",
        source="handle_01",
        target="door_01",
        layer="functional",
    )
    add_edge(
        scene,
        edge_id="edge_door_affords_open",
        edge_type="affords",
        source="door_01",
        target="handle_01",
        layer="affordance",
        properties={"action": "open"},
    )

    scene.layers["geometry"].CopyFrom(to_struct({"default_coordinate_space": "world"}))
    scene.layers["affordance"].CopyFrom(to_struct({"actor_model": "human_adult"}))
    return scene


def main() -> int:
    scene = build_scene()
    out_dir = ROOT / "generated" / "examples"
    out_dir.mkdir(parents=True, exist_ok=True)

    binary_path = out_dir / "room_from_python.scenegraph.pb"
    json_path = out_dir / "room_from_python.scenegraph.pb.json"

    binary_path.write_bytes(scene.SerializeToString())
    json_path.write_text(
        json_format.MessageToJson(scene, preserving_proto_field_name=True, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {binary_path.relative_to(ROOT)}")
    print(f"Wrote {json_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
