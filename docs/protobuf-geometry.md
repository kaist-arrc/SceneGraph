# Protobuf Geometry

The Protobuf runtime schema represents 6 DoF pose with typed messages instead
of free-form JSON.

## Coordinate System

The scene-level coordinate convention lives in `Metadata`.

```proto
message CoordinateSystem {
  Handedness handedness = 1;
  Axis up_axis = 2;
}
```

Example meaning:

```text
handedness: HANDEDNESS_RIGHT
up_axis: AXIS_Y
units: meter
```

This defines the convention used by the scene. It does not place an object.

## 6 DoF Pose

Object placement lives in `GeometryProperties.pose`.

```proto
message Pose {
  string frame_id = 1;
  Transform transform = 2;
}

message Transform {
  Vec3 translation = 1;
  Quaternion rotation = 2;
  Vec3 scale = 3;
}
```

A pose is relative to `frame_id`. For example, a door can be placed relative to
`world`, while a handle could later be placed relative to `door_01`.

## Rotation

Rotation uses quaternion `x, y, z, w`.

```proto
message Quaternion {
  double x = 1;
  double y = 2;
  double z = 3;
  double w = 4;
}
```

The identity rotation is:

```text
x: 0
y: 0
z: 0
w: 1
```

Quaternion rotation avoids the ambiguity and singularities of Euler angles.

## Bounds And Primitives

Geometry also includes typed bounds and primitives.

```proto
message GeometryProperties {
  Pose pose = 1;
  Bounds bounds = 2;
  Primitive primitive = 3;
  string mesh_uri = 4;
  google.protobuf.Struct extensions = 15;
}
```

`Bounds` describes spatial extent for reasoning, broad-phase queries, and
containment. `Primitive` describes simple authored geometry when no mesh is
needed.

## Flexible Layers Remain Flexible

Only geometry has been promoted to typed messages. Functional, semantic, and
affordance properties still use `google.protobuf.Struct` while their vocabularies
are evolving.

This gives C++ and Python strong types for pose math while keeping the rest of
the proposal easy to iterate.
