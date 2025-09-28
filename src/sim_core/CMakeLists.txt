add_library(evsim_core SHARED
    src/BatteryPackModel.cpp
    src/EulerSolver.cpp
    src/EventBus.cpp
    src/ImporterRegistry.cpp
    src/InMemoryResultStore.cpp
    src/SingleCellModels.cpp
    src/PluginRegistry.cpp
    src/SimulationOrchestrator.cpp
    src/WltpCsvLoader.cpp
    src/core_c_api.cpp
)

target_include_directories(evsim_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(evsim_core PUBLIC cxx_std_20)

set_target_properties(evsim_core PROPERTIES
    OUTPUT_NAME "evsim_core"
    EXPORT_NAME "evsim_core"
)
