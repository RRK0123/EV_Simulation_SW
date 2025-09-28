cmake_minimum_required(VERSION 3.21)
project(EV_Simulation_SW LANGUAGES CXX)

option(EV_SIM_ENABLE_TESTS "Build C++ tests" OFF)

add_subdirectory(src/sim_core)
add_subdirectory(app/cli)

if(EV_SIM_ENABLE_TESTS)
    enable_testing()
    add_subdirectory(tests/cpp)
endif()
