#pragma once

#include <memory>
#include <string>
#include <string_view>

#include "evsim/core/Scenario.hpp"
#include "evsim/models/SimulationModel.hpp"

namespace evsim::models {

class SingleCellBaseModel : public SimulationModel {
public:
    explicit SingleCellBaseModel(std::string model_name);

    std::string name() const override;
    void configure(const core::Scenario& scenario) override;
    void reset() override;
    common::TimeseriesSample step(double time, double dt) override;

protected:
    virtual double compute_terminal_voltage(double current_a, double ocv_v, double dt) = 0;
    virtual void on_reset();
    virtual void populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                        double terminal_voltage_v, double ocv_v, double heat_w) const;
    virtual double compute_heat_generation(double current_a, double terminal_voltage_v,
                                           double ocv_v) const;
    virtual void update_temperature(double heat_w, double dt);

    [[nodiscard]] double capacity_coulombs() const;
    [[nodiscard]] double compute_ocv() const;
    [[nodiscard]] double compute_current(double speed_mps, double accel_mps2) const;
    void integrate_soc(double current_a, double dt);

    const core::DriveCycleSample& drive_sample(std::size_t index) const;
    std::size_t sample_index_for_time(double time) const;
    std::string signal_name(std::string_view suffix) const;

protected:
    std::string model_name_;
    core::CellDefinition cell_;
    core::DriveCycle drive_cycle_;
    core::EnvironmentConditions environment_{};
    double scenario_time_step_{1.0};
    double soc_{1.0};
    double temperature_c_{25.0};
    double previous_speed_mps_{0.0};
};

class SingleCellOhmicModel final : public SingleCellBaseModel {
public:
    SingleCellOhmicModel();

protected:
    double compute_terminal_voltage(double current_a, double ocv_v, double dt) override;
};

class SingleCellRcModel final : public SingleCellBaseModel {
public:
    SingleCellRcModel();

protected:
    double compute_terminal_voltage(double current_a, double ocv_v, double dt) override;
    void on_reset() override;
    void populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                double terminal_voltage_v, double ocv_v, double heat_w) const override;

private:
    double rc_voltage_v_{0.0};
};

class SingleCellThermalModel final : public SingleCellBaseModel {
public:
    SingleCellThermalModel();

protected:
    double compute_terminal_voltage(double current_a, double ocv_v, double dt) override;
    void update_temperature(double heat_w, double dt) override;
    void populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                double terminal_voltage_v, double ocv_v, double heat_w) const override;
};

}  // namespace evsim::models
