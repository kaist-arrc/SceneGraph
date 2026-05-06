# Schema Overview

This document describes the proposed top-level shape of a SceneGraph document.

This page describes the human-readable JSON proposal. For the C++ and Python
runtime contract, see the typed Protobuf schema in
[`proto/scenegraph.proto`](../proto/scenegraph.proto), especially the geometry
messages described in [Protobuf Geometry](protobuf-geometry.md).

## Top-Level Object

```json
{
  "schema": "scenegraph",
  "version": "0.1.0",
  "metadata": {},
  "nodes": [],
  "edges": [],
  "layers": {},
  "extensions": {}
}
```

## Metadata

`metadata` records scene-level context.

Recommended fields:

- `name`
- `description`
- `author`
- `created_at`
- `units`
- `coordinate_system`
- `source`

Example:

```json
{
  "name": "Example room",
  "units": "meter",
  "coordinate_system": {
    "handedness": "right",
    "up_axis": "Y"
  }
}
```

## Nodes

Nodes represent entities in the scene.

Required fields:

- `id`: stable unique identifier
- `type`: broad entity type

Optional fields:

- `name`
- `layers`
- `properties`
- `provenance`
- `extensions`

Example:

```json
{
  "id": "door_01",
  "type": "object",
  "name": "Main door",
  "layers": ["geometry", "semantic", "functional", "affordance"],
  "properties": {
    "semantic": {
      "category": "door"
    },
    "functional": {
      "state": {
        "open": false,
        "locked": false
      }
    }
  }
}
```

## Edges

Edges represent typed relationships between nodes.

Required fields:

- `id`
- `type`
- `source`
- `target`
- `layer`

Optional fields:

- `properties`
- `confidence`
- `provenance`
- `extensions`

Example:

```json
{
  "id": "edge_handle_part_of_door",
  "type": "part_of",
  "source": "handle_01",
  "target": "door_01",
  "layer": "semantic"
}
```

## Layers

`layers` stores layer-level settings, indexes, or constraints.

Example:

```json
{
  "geometry": {
    "default_coordinate_space": "world"
  },
  "affordance": {
    "actor_model": "human_adult"
  }
}
```

## Extensions

`extensions` is reserved for domain-specific data. Extension keys should use a
namespace-like prefix.

Examples:

- `robotics.grasp_quality`
- `gameplay.interaction_prompt`
- `bim.ifc_guid`
- `simulation.physics_material`

The core schema should accept extensions while keeping them separate from
portable concepts.
