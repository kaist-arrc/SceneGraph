# Open Questions

This page tracks design questions that should be discussed before the schema is
treated as stable.

## Identity

- Should IDs be local strings, URIs, UUIDs, or support all three?
- How should the schema represent two systems disagreeing about whether two
  detections are the same object?
- Should object identity survive scene updates over time?

## Geometry

- Which transform convention should be recommended by default?
- Should geometry primitives be standardized in the core schema?
- How should the schema reference external assets such as meshes, materials,
  point clouds, and textures?

## Functional Graph

- Should functional state be represented as free-form properties or typed state
  machines?
- How should continuous processes, flows, and constraints be modeled?
- Should functional dependencies be executable, declarative, or descriptive?

## Semantic Graph

- Should the core schema define a small vocabulary of categories?
- How should external ontologies be referenced?
- How should uncertainty, confidence, and alternative labels be represented?

## Affordance Graph

- Should affordances be object-centric, actor-centric, or action-centric?
- How should preconditions and effects be written so they are both readable and
  executable?
- How should the schema represent failed or risky affordances?

## Time And Change

- Is the base document a static scene, a snapshot, or an evolving world model?
- Should temporal changes be represented as patches, events, or versioned graph
  states?
- How should the graph store provenance for updates from sensors or inference?

## Validation

- Which constraints should be enforced by JSON Schema?
- Which constraints require a graph validator outside JSON Schema?
- Should example validators be provided in this repository?
