cmake_minimum_required(VERSION 3.21)
project(ev_simulation_ui LANGUAGES CXX)

find_package(Qt6 6.5 COMPONENTS Core Gui Qml Quick REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

qt_standard_project_setup()

qt_add_executable(ev_simulation_ui
    src/main.cpp
    src/OrchestratorClient.cpp
    include/OrchestratorClient.hpp
)

target_include_directories(ev_simulation_ui PRIVATE include)

qt_add_qml_module(ev_simulation_ui
    URI EVSim
    VERSION 1.0
    QML_FILES
        qml/Main.qml
)

target_link_libraries(ev_simulation_ui
    PRIVATE
        Qt6::Core
        Qt6::Gui
        Qt6::Qml
        Qt6::Quick
)

install(TARGETS ev_simulation_ui RUNTIME DESTINATION bin)

