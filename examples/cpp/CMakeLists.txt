cmake_minimum_required(VERSION 3.16)

project(scenegraph_examples LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(GENERATED_CPP_DIR "" CACHE PATH "Directory containing generated scenegraph.pb.cc and scenegraph.pb.h")
if(NOT GENERATED_CPP_DIR)
  message(FATAL_ERROR "Set GENERATED_CPP_DIR to the generated/cpp directory.")
endif()

find_package(Protobuf REQUIRED)

add_library(scenegraph_proto
  "${GENERATED_CPP_DIR}/scenegraph.pb.cc"
)
target_include_directories(scenegraph_proto PUBLIC
  "${GENERATED_CPP_DIR}"
)
target_link_libraries(scenegraph_proto PUBLIC
  protobuf::libprotobuf
)

add_executable(build_room build_room.cc)
target_link_libraries(build_room PRIVATE scenegraph_proto)
