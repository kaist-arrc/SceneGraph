# Design Principles

The scene graph schema should support both human discussion and machine
reasoning. These principles guide the shape of the model.

## 1. One Entity, Many Views

A real object may participate in several graph views at once.

For example, a chair can be:

- a geometry node with transform, mesh, and bounding volume
- a semantic node with category `chair`
- a functional node that supports sitting
- an affordance target for actions such as `sit`, `move`, or `grasp`

The schema should avoid duplicating the chair as unrelated objects. Instead, it
should use stable node IDs and attach layer-specific properties where needed.

## 2. Relationships Are First-Class

Edges are not just implementation details. They carry meaning.

Examples:

- `contains`: a room contains a table
- `supports`: a table supports a cup
- `part_of`: a handle is part of a door
- `enables`: a handle enables opening the door
- `requires`: opening the door requires the door to be unlocked

Typed edges let geometry, semantics, function, and affordance reasoning share a
common graph substrate.

## 3. Separate Observation From Interpretation

The schema should make room for both measured facts and inferred meaning.

Examples:

- measured: mesh path, pose, bounding box, detected plane
- inferred: object category, likely function, possible action
- authored: manually assigned label, gameplay behavior, simulation property

Fields should be able to record confidence, source, and provenance when those
distinctions matter.

## 4. Keep The Core Small

The core schema should define durable concepts:

- node identity
- edge identity
- graph layer
- typed properties
- coordinate system
- provenance
- extensions

Specialized domains can add fields through `extensions` rather than forcing
every use case into the base model.

## 5. Support Incremental Detail

A scene may start as a sparse graph and become richer over time.

The schema should allow:

- geometry-only scenes
- semantic labels without full geometry
- affordances inferred later
- partial functional descriptions
- multiple alternative hypotheses for the same object

This is important for pipelines that combine perception, manual authoring,
simulation, and planning.

## 6. Be Useful Across Domains

The model should be understandable in multiple settings:

- robotics and embodied AI
- digital twins and BIM-like environments
- simulation and synthetic data
- games and interactive worlds
- CAD and product structure
- AR, VR, and spatial computing

The schema should avoid unnecessary assumptions about one engine, renderer, or
runtime.
