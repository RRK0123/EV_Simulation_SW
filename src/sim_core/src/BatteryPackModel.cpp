#include "evsim/models/BatteryPackModel.hpp"

#include <algorithm>

namespace evsim::models {

std::string BatteryPackModel::name() const { return "battery_pack"; }

void BatteryPackModel::configure(const core::Scenario& scenario) {
    for (const auto& parameter : scenario.parameters) {
        if (parameter.name == "nominal_voltage") {
            nominal_voltage_ = parameter.value;
        } else if (parameter.name == "capacity_kwh") {
            pack_capacity_ = parameter.value;
        } else if (parameter.name == "internal_resistance") {
            internal_resistance_ = parameter.value;
        } else if (parameter.name == "current_draw") {
            current_draw_profile_ = parameter.value;
        }
    }
}

void BatteryPackModel::reset() { soc_ = 1.0; }

common::TimeseriesSample BatteryPackModel::step(double time, double dt) {
    const double discharge_kw = nominal_voltage_ * current_draw_profile_ / 1000.0;
    const double energy_removed = discharge_kw * dt / 3600.0;
    const double capacity_wh = pack_capacity_ * 1000.0;
    const double delta_soc = energy_removed / capacity_wh;
    soc_ = std::clamp(soc_ - delta_soc, 0.0, 1.0);

    common::TimeseriesSample sample{};
    sample.timestamp = time;
    sample.signals["pack.voltage"] = nominal_voltage_ - current_draw_profile_ * internal_resistance_;
    sample.signals["pack.current"] = current_draw_profile_;
    sample.signals["pack.soc"] = soc_;
    sample.signals["pack.power_kw"] = discharge_kw;
    return sample;
}

}  // namespace evsim::models
