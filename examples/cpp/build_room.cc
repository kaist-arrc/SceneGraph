#include "scenegraph.pb.h"

#include <google/protobuf/struct.pb.h>
#include <google/protobuf/util/json_util.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;
namespace sg = scenegraph::v1;

google::protobuf::Struct StructFromJson(const std::string& json) {
  google::protobuf::Struct value;
  const auto status = google::protobuf::util::JsonStringToMessage(json, &value);
  if (!status.ok()) {
    throw std::runtime_error("Could not parse Struct JSON: " + status.ToString());
  }
  return value;
}

void SetVec3(sg::Vec3* value, double x, double y, double z) {
  value->set_x(x);
  value->set_y(y);
  value->set_z(z);
}

void SetQuaternion(sg::Quaternion* value, double x, double y, double z, double w) {
  value->set_x(x);
  value->set_y(y);
  value->set_z(z);
  value->set_w(w);
}

void SetPose(
    sg::GeometryProperties* geometry,
    const std::string& frame_id,
    double tx,
    double ty,
    double tz) {
  auto* pose = geometry->mutable_pose();
  pose->set_frame_id(frame_id);
  auto* transform = pose->mutable_transform();
  SetVec3(transform->mutable_translation(), tx, ty, tz);
  SetQuaternion(transform->mutable_rotation(), 0.0, 0.0, 0.0, 1.0);
  SetVec3(transform->mutable_scale(), 1.0, 1.0, 1.0);
}

void SetBoxBounds(sg::GeometryProperties* geometry, double x, double y, double z) {
  SetVec3(geometry->mutable_bounds()->mutable_box()->mutable_size(), x, y, z);
}

void SetCylinderPrimitive(
    sg::GeometryProperties* geometry,
    double radius,
    double length,
    sg::Axis axis = sg::AXIS_X) {
  auto* cylinder = geometry->mutable_primitive()->mutable_cylinder();
  cylinder->set_radius(radius);
  cylinder->set_length(length);
  cylinder->set_axis(axis);
}

sg::Node* AddNode(
    sg::SceneGraph* scene,
    const std::string& id,
    const std::string& type,
    const std::string& name,
    const std::vector<sg::Layer>& layers) {
  auto* node = scene->add_nodes();
  node->set_id(id);
  node->set_type(type);
  node->set_name(name);
  for (const auto layer : layers) {
    node->add_layers(layer);
  }
  return node;
}

sg::Edge* AddEdge(
    sg::SceneGraph* scene,
    const std::string& id,
    const std::string& type,
    const std::string& source,
    const std::string& target,
    sg::Layer layer) {
  auto* edge = scene->add_edges();
  edge->set_id(id);
  edge->set_type(type);
  edge->set_source(source);
  edge->set_target(target);
  edge->set_layer(layer);
  return edge;
}

sg::SceneGraph BuildScene() {
  sg::SceneGraph scene;
  scene.set_schema("scenegraph");
  scene.set_version("0.1.0");

  auto* metadata = scene.mutable_metadata();
  metadata->set_name("C++ room example");
  metadata->set_description("A small scene built through C++ helper functions.");
  metadata->set_author("SceneGraph contributors");
  metadata->set_units("meter");
  metadata->mutable_coordinate_system()->set_handedness(sg::HANDEDNESS_RIGHT);
  metadata->mutable_coordinate_system()->set_up_axis(sg::AXIS_Y);

  auto* room = AddNode(
      &scene,
      "room_01",
      "scene",
      "Room",
      {sg::LAYER_GEOMETRY, sg::LAYER_SEMANTIC});
  SetBoxBounds(room->mutable_properties()->mutable_geometry(), 4.0, 2.8, 3.5);
  room->mutable_properties()->mutable_semantic()->CopyFrom(StructFromJson(R"json({
    "category": "room",
    "attributes": ["indoor"]
  })json"));

  auto* door = AddNode(
      &scene,
      "door_01",
      "object",
      "Door",
      {sg::LAYER_GEOMETRY, sg::LAYER_FUNCTIONAL, sg::LAYER_SEMANTIC, sg::LAYER_AFFORDANCE});
  auto* door_geometry = door->mutable_properties()->mutable_geometry();
  SetPose(door_geometry, "world", 0.0, 1.0, -1.75);
  SetBoxBounds(door_geometry, 0.9, 2.0, 0.08);
  door->mutable_properties()->mutable_semantic()->CopyFrom(StructFromJson(R"json({
    "category": "door",
    "attributes": ["hinged", "entry"]
  })json"));
  door->mutable_properties()->mutable_functional()->CopyFrom(StructFromJson(R"json({
    "state": { "open": false, "locked": false },
    "mechanism": "hinge"
  })json"));
  door->mutable_properties()->mutable_affordance()->CopyFrom(StructFromJson(R"json({
    "affordances": [
      {
        "action": "open",
        "actor": "human",
        "preconditions": ["door_01.functional.state.locked == false"],
        "effects": ["door_01.functional.state.open = true"]
      }
    ]
  })json"));

  auto* handle = AddNode(
      &scene,
      "handle_01",
      "part",
      "Door handle",
      {sg::LAYER_GEOMETRY, sg::LAYER_FUNCTIONAL, sg::LAYER_SEMANTIC, sg::LAYER_AFFORDANCE});
  auto* handle_geometry = handle->mutable_properties()->mutable_geometry();
  SetPose(handle_geometry, "world", 0.35, 1.05, -1.7);
  SetCylinderPrimitive(handle_geometry, 0.03, 0.16);
  handle->mutable_properties()->mutable_semantic()->CopyFrom(StructFromJson(R"json({
    "category": "handle"
  })json"));
  handle->mutable_properties()->mutable_functional()->CopyFrom(StructFromJson(R"json({
    "function": "latch_control"
  })json"));
  handle->mutable_properties()->mutable_affordance()->CopyFrom(StructFromJson(R"json({
    "affordances": [{ "action": "grasp", "actor": "human" }]
  })json"));

  AddEdge(&scene, "edge_room_contains_door", "contains", "room_01", "door_01", sg::LAYER_GEOMETRY);
  AddEdge(&scene, "edge_handle_part_of_door", "part_of", "handle_01", "door_01", sg::LAYER_SEMANTIC);
  AddEdge(&scene, "edge_handle_controls_door", "controls", "handle_01", "door_01", sg::LAYER_FUNCTIONAL);

  auto* affordance_edge = AddEdge(
      &scene,
      "edge_door_affords_open",
      "affords",
      "door_01",
      "handle_01",
      sg::LAYER_AFFORDANCE);
  affordance_edge->mutable_properties()->CopyFrom(StructFromJson(R"json({
    "action": "open"
  })json"));

  (*scene.mutable_layers())["geometry"].CopyFrom(StructFromJson(R"json({
    "default_coordinate_space": "world"
  })json"));
  (*scene.mutable_layers())["affordance"].CopyFrom(StructFromJson(R"json({
    "actor_model": "human_adult"
  })json"));

  return scene;
}

int main(int argc, char** argv) {
  const fs::path out_dir = argc > 1 ? fs::path(argv[1]) : fs::path("generated/examples");
  fs::create_directories(out_dir);

  const auto scene = BuildScene();
  const auto binary_path = out_dir / "room_from_cpp.scenegraph.pb";
  const auto json_path = out_dir / "room_from_cpp.scenegraph.pb.json";

  std::ofstream binary(binary_path, std::ios::binary);
  if (!scene.SerializeToOstream(&binary)) {
    throw std::runtime_error("Could not write " + binary_path.string());
  }

  google::protobuf::util::JsonPrintOptions options;
  options.preserve_proto_field_names = true;
  std::string json;
  const auto status = google::protobuf::util::MessageToJsonString(scene, &json, options);
  if (!status.ok()) {
    throw std::runtime_error("Could not convert scene to JSON: " + status.ToString());
  }

  std::ofstream json_file(json_path);
  json_file << json << '\n';

  std::cout << "Wrote " << binary_path.string() << '\n';
  std::cout << "Wrote " << json_path.string() << '\n';
  return 0;
}
