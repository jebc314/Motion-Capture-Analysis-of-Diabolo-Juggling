cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

if(POLICY CMP0100)
  cmake_policy(SET CMP0100 NEW)
endif()

set (CMAKE_AUTOMOC ON)

find_package (Qt5Widgets REQUIRED)
find_package (Qt5Core REQUIRED)
find_package(Protobuf REQUIRED)
find_package(gazebo REQUIRED)

include_directories(SYSTEM ${GAZEBO_INCLUDE_DIRS} ${Qt5Core_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${GAZEBO_CXX_FLAGS}")

add_library(gui_example_spawn_widget SHARED ${headers_MOC}
  GUIExampleSpawnWidget.cc)
target_link_libraries(gui_example_spawn_widget ${GAZEBO_LIBRARIES}
    ${Qt5Core_LIBRARIES}
    ${Qt5Widgets_LIBRARIES}
    ${PROTOBUF_LIBRARIES})
    
# Find the Ignition_Transport library
find_package(ignition-transport8 QUIET)
if (NOT ignition-transport8_FOUND)
  find_package(ignition-transport4 REQUIRED)
endif()
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${IGNITION-TRANSPORT_CXX_FLAGS}")
include_directories(${IGNITION-TRANSPORT_INCLUDE_DIRS})
link_directories(${IGNITION-TRANSPORT_LIBRARY_DIRS})
    
# add_executable(watcher watcher.cc)
# target_link_libraries(watcher ${GAZEBO_LIBRARIES} ${IGNITION-TRANSPORT_LIBRARIES})

add_library(model_push SHARED model_push.cc)
target_link_libraries(model_push ${GAZEBO_LIBRARIES})

add_library(model_revolve_y SHARED model_revolve_y.cc)
target_link_libraries(model_revolve_y ${GAZEBO_LIBRARIES})

add_library(model_revolve_z SHARED model_revolve_z.cc)
target_link_libraries(model_revolve_z ${GAZEBO_LIBRARIES})

add_library(model_revolve_z_opp SHARED model_revolve_z_opp.cc)
target_link_libraries(model_revolve_z_opp ${GAZEBO_LIBRARIES})