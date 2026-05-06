# Graph Layers

The scene graph is a shared entity graph with four major views. Each view
answers a different kind of question about the same scene.

## Geometry Graph

The geometry graph describes physical and spatial structure.

Typical questions:

- Where is this object?
- What is its parent transform?
- What mesh, primitive, or volume represents it?
- What contains, supports, touches, or intersects what?

Common node properties:

- `transform`
- `mesh`
- `primitive`
- `bounds`
- `material`
- `coordinate_space`

Common edge types:

- `child_of`
- `contains`
- `attached_to`
- `supports`
- `touches`
- `intersects`

## Functional Graph

The functional graph describes mechanisms, behaviors, dependencies, and state.

Typical questions:

- What role does this object play?
- Which component controls another component?
- What state can change?
- What flows through or between objects?

Common node properties:

- `function`
- `state`
- `inputs`
- `outputs`
- `parameters`
- `constraints`

Common edge types:

- `part_of`
- `controls`
- `depends_on`
- `transfers`
- `constrains`
- `activates`

## Semantic Graph

The semantic graph describes meaning.

Typical questions:

- What is this thing?
- What class or category does it belong to?
- Which object is a part, instance, or member of another?
- What labels, attributes, and context describe it?

Common node properties:

- `label`
- `category`
- `attributes`
- `ontology_refs`
- `confidence`
- `source`

Common edge types:

- `is_a`
- `instance_of`
- `part_of`
- `same_as`
- `near`
- `used_for`

## Affordance Graph

The affordance graph describes possible actions.

Typical questions:

- What can an actor do with this object?
- What preconditions must be true?
- What effects should be expected?
- Which parts are action handles or interaction targets?

Common node properties:

- `affordances`
- `actor_requirements`
- `preconditions`
- `effects`
- `interaction_regions`
- `success_likelihood`

Common edge types:

- `affords`
- `requires`
- `causes`
- `targets`
- `blocks`
- `enables`

## Cross-Layer Links

The four graph views should not become four disconnected datasets. They are
linked through shared node IDs and typed edges.

Example:

```text
door_01
|-- geometry: has transform, mesh, bounds
|-- semantic: category door, attribute hinged
|-- functional: state open/closed/locked
`-- affordance: open, close, lock, unlock
```

Cross-layer reasoning is where the schema becomes powerful. A planner can use
the semantic graph to identify a door, the geometry graph to locate the handle,
the functional graph to understand lock state, and the affordance graph to plan
an `open` action.
