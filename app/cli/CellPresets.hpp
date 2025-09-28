#pragma once

#include <map>
#include <string>

#include "evsim/core/Scenario.hpp"

namespace wltp::cli {

struct CellPresetParameters {
    std::string cell_id;
    std::string chemistry;
    evsim::core::CellModelKind model_kind{evsim::core::CellModelKind::Ohmic};
    double nominal_voltage{3.7};
    double capacity_ah{5.0};
    double internal_resistance{0.015};
    double base_current_a{2.0};
    double speed_current_gain{0.4};
    double accel_current_gain{2.5};
    double ocv_min{3.0};
    double ocv_max{4.2};
    double rc_time_constant_s{0.0};
    double rc_resistance{0.0};
    double mass_kg{0.0};
    double surface_area_m2{0.0};
    double heat_capacity_j_per_kg_k{0.0};
    double thermal_resistance_k_per_w{0.0};
};

inline const std::map<std::string, CellPresetParameters>& default_cell_presets() {
    static const std::map<std::string, CellPresetParameters> presets = [] {
        std::map<std::string, CellPresetParameters> definitions{};

        CellPresetParameters nmc{};
        nmc.cell_id = "NMC811";
        nmc.chemistry = "NMC811";
        nmc.model_kind = evsim::core::CellModelKind::Ohmic;
        nmc.nominal_voltage = 3.65;
        nmc.capacity_ah = 5.0;
        nmc.internal_resistance = 0.012;
        nmc.base_current_a = 2.0;
        nmc.speed_current_gain = 0.55;
        nmc.accel_current_gain = 3.0;
        nmc.ocv_min = 3.0;
        nmc.ocv_max = 4.25;
        definitions.emplace(nmc.cell_id, nmc);

        CellPresetParameters lfp{};
        lfp.cell_id = "LFP";
        lfp.chemistry = "LFP";
        lfp.model_kind = evsim::core::CellModelKind::Rc;
        lfp.nominal_voltage = 3.2;
        lfp.capacity_ah = 4.8;
        lfp.internal_resistance = 0.015;
        lfp.base_current_a = 2.5;
        lfp.speed_current_gain = 0.6;
        lfp.accel_current_gain = 3.5;
        lfp.ocv_min = 2.9;
        lfp.ocv_max = 3.7;
        lfp.rc_time_constant_s = 8.0;
        lfp.rc_resistance = 0.0045;
        definitions.emplace(lfp.cell_id, lfp);

        CellPresetParameters nca{};
        nca.cell_id = "NCA";
        nca.chemistry = "NCA";
        nca.model_kind = evsim::core::CellModelKind::Thermal;
        nca.nominal_voltage = 3.6;
        nca.capacity_ah = 4.5;
        nca.internal_resistance = 0.011;
        nca.base_current_a = 3.0;
        nca.speed_current_gain = 0.65;
        nca.accel_current_gain = 4.0;
        nca.ocv_min = 3.1;
        nca.ocv_max = 4.15;
        nca.mass_kg = 0.047;
        nca.surface_area_m2 = 0.013;
        nca.heat_capacity_j_per_kg_k = 910.0;
        nca.thermal_resistance_k_per_w = 1.2;
        definitions.emplace(nca.cell_id, nca);

        return definitions;
    }();
    return presets;
}

}  // namespace wltp::cli
