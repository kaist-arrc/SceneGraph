# Code Generation

SceneGraph can use Protobuf as a shared runtime contract for C++ and Python.
The source file is:

```text
proto/scenegraph.proto
```

Generated files should be treated as build artifacts. By default they are
written to `generated/`, which is ignored by Git.

## Generate Python And C++

Run:

```powershell
python tools/generate_protos.py
```

This generates:

```text
generated/
|-- cpp/
|   |-- scenegraph.pb.cc
|   `-- scenegraph.pb.h
`-- python/
    `-- scenegraph_pb2.py
```

## Generate One Language

Python only:

```powershell
python tools/generate_protos.py --language python
```

C++ only:

```powershell
python tools/generate_protos.py --language cpp
```

## Required Tooling

The script first tries to use `protoc` if it is installed.

If `protoc` is not installed, it falls back to Python's `grpcio-tools` package:

```powershell
python -m pip install -r requirements-dev.txt
python tools/generate_protos.py
```

## Python Usage

After generation:

```python
from generated.python import scenegraph_pb2

scene = scenegraph_pb2.SceneGraph()
scene.schema = "scenegraph"
scene.version = "0.1.0"

node = scene.nodes.add()
node.id = "door_01"
node.type = "object"
node.name = "Door"
node.layers.append(scenegraph_pb2.LAYER_GEOMETRY)
node.layers.append(scenegraph_pb2.LAYER_SEMANTIC)
```

## C++ Usage

After generation, add `generated/cpp` to your include path and compile
`generated/cpp/scenegraph.pb.cc` with the Protobuf runtime.

```cpp
#include "scenegraph.pb.h"

scenegraph::v1::SceneGraph scene;
scene.set_schema("scenegraph");
scene.set_version("0.1.0");

auto* node = scene.add_nodes();
node->set_id("door_01");
node->set_type("object");
node->set_name("Door");
node->add_layers(scenegraph::v1::LAYER_GEOMETRY);
node->add_layers(scenegraph::v1::LAYER_SEMANTIC);
```

## Recommended Workflow

1. Edit `proto/scenegraph.proto`.
2. Run `python tools/generate_protos.py`.
3. Build or test the Python/C++ code that consumes the generated files.
4. Commit the `.proto` change and docs/examples.

Generated files can be committed later if packaging needs require it, but during
schema design they are easier to keep as reproducible build artifacts.

## GitHub Actions

The repository includes `.github/workflows/protobuf.yml`.

On pushes to `main`, pull requests, and manual runs, the workflow:

1. installs Python
2. installs `requirements-dev.txt`
3. checks the generator script syntax
4. generates Python and C++ Protobuf bindings
5. verifies the expected generated files exist
6. uploads the generated bindings as a short-lived CI artifact
