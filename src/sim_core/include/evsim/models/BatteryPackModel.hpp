#pragma once

#include <vector>

#include "evsim/models/SimulationModel.hpp"

namespace evsim::models {

class BatteryPackModel final : public SimulationModel {
public:
    BatteryPackModel() = default;
    ~BatteryPackModel() override = default;

    std::string name() const override;
    void configure(const core::Scenario& scenario) override;
    void reset() override;
    common::TimeseriesSample step(double time, double dt) override;

private:
    double nominal_voltage_{400.0};
    double pack_capacity_{85.0};  // kWh
    double internal_resistance_{0.05};
    double soc_{1.0};
    double current_draw_profile_{60.0};
};

}  // namespace evsim::models
