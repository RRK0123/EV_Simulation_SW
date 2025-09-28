add_executable(wltp_single_cell_cli
    wltp_single_cell_cli.cpp
)

target_link_libraries(wltp_single_cell_cli PRIVATE evsim_core)

target_compile_features(wltp_single_cell_cli PRIVATE cxx_std_20)
