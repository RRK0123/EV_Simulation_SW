#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace evsim::core {

enum class CellModelKind { Ohmic, Rc, Thermal };

struct DriveCycleSample {
    double timestamp{0.0};
    double speed_kph{0.0};
    double distance_m{0.0};
    double grade_percent{0.0};
    std::string phase;
};

struct DriveCycle {
    std::string id;
    std::string description;
    std::string source;
    double sample_interval{1.0};
    std::vector<DriveCycleSample> samples{};
};

struct EnvironmentConditions {
    double ambient_temperature_c{25.0};
    double initial_cell_temperature_c{25.0};
};

struct CellDefinition {
    std::string cell_id;
    std::string chemistry;
    CellModelKind model_kind{CellModelKind::Ohmic};
    double nominal_voltage{3.7};
    double capacity_ah{5.0};
    double internal_resistance{0.015};
    double rc_time_constant_s{10.0};
    double rc_resistance{0.005};
    double mass_kg{0.045};
    double heat_capacity_j_per_kg_k{900.0};
    double thermal_resistance_k_per_w{1.5};
    double surface_area_m2{0.01};
    double base_current_a{2.0};
    double speed_current_gain{0.4};
    double accel_current_gain{2.5};
    double ocv_min{3.0};
    double ocv_max{4.2};
};

struct ScenarioParameter {
    std::string name;
    double value{0.0};
};

struct Scenario {
    std::string id;
    std::string description;
    double time_step{0.1};
    std::size_t step_count{0};
    std::vector<ScenarioParameter> parameters{};
    std::vector<CellDefinition> cells{};
    std::string active_cell_id;
    DriveCycle drive_cycle{};
    EnvironmentConditions environment{};

    [[nodiscard]] double duration() const noexcept { return time_step * static_cast<double>(step_count); }
};

}  // namespace evsim::core
