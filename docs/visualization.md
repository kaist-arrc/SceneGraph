# Visualization

This page sketches the schema idea visually. The diagrams use Mermaid, which is
rendered by GitHub Markdown.

## Four-Layer Scene Graph

```mermaid
flowchart TB
    SceneGraph["SceneGraph Document"]

    SceneGraph --> Metadata["Metadata<br/>units, source, coordinate system"]
    SceneGraph --> Nodes["Shared Nodes<br/>stable entity IDs"]
    SceneGraph --> Edges["Typed Edges<br/>relationships between nodes"]
    SceneGraph --> Layers["Layer Settings<br/>defaults and validation rules"]

    Nodes --> Geometry["Geometry Graph<br/>pose, mesh, bounds, containment"]
    Nodes --> Functional["Functional Graph<br/>state, mechanisms, dependencies"]
    Nodes --> Semantic["Semantic Graph<br/>categories, labels, meaning"]
    Nodes --> Affordance["Affordance Graph<br/>actions, preconditions, effects"]

    Edges --> Geometry
    Edges --> Functional
    Edges --> Semantic
    Edges --> Affordance
```

## One Object Across Multiple Views

```mermaid
flowchart LR
    Door["door_01<br/>shared node ID"]

    Door --> DoorGeometry["Geometry<br/>transform<br/>bounds<br/>mesh"]
    Door --> DoorFunctional["Functional<br/>open: false<br/>locked: false<br/>hinge mechanism"]
    Door --> DoorSemantic["Semantic<br/>category: door<br/>attributes: hinged, entry"]
    Door --> DoorAffordance["Affordance<br/>open<br/>close<br/>lock<br/>unlock"]
```

## Cross-Layer Reasoning Example

```mermaid
flowchart LR
    Agent["Actor / Agent"] --> Goal["Goal<br/>enter room"]
    Goal --> SemanticQuery["Semantic query<br/>find object category: door"]
    SemanticQuery --> Door["door_01"]
    Door --> FunctionalCheck["Functional check<br/>locked == false"]
    FunctionalCheck --> AffordanceSelect["Affordance selection<br/>open door"]
    AffordanceSelect --> GeometryPlan["Geometry planning<br/>locate handle region"]
    GeometryPlan --> Action["Execute action<br/>grasp + turn + pull"]
```

## Example Room Graph

```mermaid
flowchart TB
    Room["room_01<br/>room"]
    Door["door_01<br/>door"]
    Handle["handle_01<br/>door handle"]
    Table["table_01<br/>table"]
    Tabletop["tabletop_01<br/>support surface"]

    Room -- "geometry: contains" --> Door
    Room -- "geometry: contains" --> Table

    Handle -- "semantic: part_of" --> Door
    Handle -- "functional: controls" --> Door
    Door -- "affordance: affords open" --> Handle

    Tabletop -- "semantic: part_of" --> Table
    Tabletop -- "affordance: supports placing" --> Table
```

## Conceptual Data Model

```mermaid
classDiagram
    class SceneGraphDocument {
      string schema
      string version
      Metadata metadata
      Node[] nodes
      Edge[] edges
      LayerSettings layers
      object extensions
    }

    class Node {
      string id
      string type
      string name
      Layer[] layers
      LayerProperties properties
      Provenance provenance
      object extensions
    }

    class Edge {
      string id
      string type
      string source
      string target
      Layer layer
      object properties
      number confidence
      Provenance provenance
      object extensions
    }

    class LayerProperties {
      object geometry
      object functional
      object semantic
      object affordance
    }

    SceneGraphDocument "1" --> "*" Node
    SceneGraphDocument "1" --> "*" Edge
    Node --> LayerProperties
    Edge --> Node : source
    Edge --> Node : target
```
