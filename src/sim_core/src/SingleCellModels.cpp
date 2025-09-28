#include "evsim/models/SingleCellModels.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>
#include <string_view>

#include "evsim/core/Scenario.hpp"

namespace {
constexpr double kSecondsPerHour = 3600.0;
constexpr double kKelvinClampMin = -40.0;
constexpr double kKelvinClampMax = 120.0;
}  // namespace

namespace evsim::models {

SingleCellBaseModel::SingleCellBaseModel(std::string model_name) : model_name_(std::move(model_name)) {}

std::string SingleCellBaseModel::name() const { return model_name_; }

void SingleCellBaseModel::configure(const core::Scenario& scenario) {
    if (scenario.active_cell_id.empty()) {
        throw std::invalid_argument("scenario active_cell_id is empty");
    }
    const auto cell_iter = std::find_if(scenario.cells.begin(), scenario.cells.end(), [&](const auto& cell) {
        return cell.cell_id == scenario.active_cell_id;
    });
    if (cell_iter == scenario.cells.end()) {
        throw std::invalid_argument("scenario does not contain active cell definition");
    }
    if (scenario.drive_cycle.samples.empty()) {
        throw std::invalid_argument("scenario drive cycle is empty");
    }
    cell_ = *cell_iter;
    drive_cycle_ = scenario.drive_cycle;
    environment_ = scenario.environment;
    scenario_time_step_ = scenario.time_step;

    if (drive_cycle_.samples.size() < scenario.step_count) {
        throw std::invalid_argument("drive cycle shorter than requested steps");
    }

}

void SingleCellBaseModel::reset() {
    soc_ = 1.0;
    temperature_c_ = environment_.initial_cell_temperature_c;
    previous_speed_mps_ = drive_cycle_.samples.front().speed_kph / 3.6;
    on_reset();
}

void SingleCellBaseModel::on_reset() {}

common::TimeseriesSample SingleCellBaseModel::step(double time, double dt) {
    const auto index = sample_index_for_time(time);
    const auto& sample = drive_sample(index);
    const double speed_mps = sample.speed_kph / 3.6;
    const double accel_mps2 = (speed_mps - previous_speed_mps_) / scenario_time_step_;
    previous_speed_mps_ = speed_mps;

    const double current_a = compute_current(speed_mps, accel_mps2);
    const double ocv_v = compute_ocv();
    const double terminal_v = compute_terminal_voltage(current_a, ocv_v, dt);
    const double heat_w = compute_heat_generation(current_a, terminal_v, ocv_v);

    integrate_soc(current_a, dt);
    update_temperature(heat_w, dt);

    common::TimeseriesSample output{};
    output.timestamp = time;
    output.signals["drive.speed_kph"] = sample.speed_kph;
    output.signals["drive.distance_m"] = sample.distance_m;
    output.signals["drive.accel_mps2"] = accel_mps2;
    double phase_id = 0.0;
    if (sample.phase == "low") {
        phase_id = 1.0;
    } else if (sample.phase == "medium") {
        phase_id = 2.0;
    } else if (sample.phase == "high") {
        phase_id = 3.0;
    } else if (sample.phase == "extra_high") {
        phase_id = 4.0;
    }
    output.signals["drive.phase_id"] = phase_id;
    output.signals[signal_name("current_a")] = current_a;
    output.signals[signal_name("voltage_v")] = terminal_v;
    output.signals[signal_name("ocv_v")] = ocv_v;
    output.signals[signal_name("soc")] = soc_;
    output.signals[signal_name("temperature_c")] = temperature_c_;
    output.signals[signal_name("power_kw")] = terminal_v * current_a / 1000.0;
    output.signals[signal_name("heat_w")] = heat_w;
    populate_extra_signals(output, current_a, terminal_v, ocv_v, heat_w);
    return output;
}

double SingleCellBaseModel::compute_heat_generation(double current_a, double terminal_voltage_v,
                                                    double ocv_v) const {
    (void)terminal_voltage_v;
    (void)ocv_v;
    return current_a * current_a * cell_.internal_resistance;
}

void SingleCellBaseModel::update_temperature(double heat_w, double dt) {
    (void)heat_w;
    (void)dt;
    temperature_c_ = environment_.ambient_temperature_c;
}

void SingleCellBaseModel::populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                                 double terminal_voltage_v, double ocv_v,
                                                 double heat_w) const {
    (void)sample;
    (void)current_a;
    (void)terminal_voltage_v;
    (void)ocv_v;
    (void)heat_w;
}

double SingleCellBaseModel::capacity_coulombs() const {
    return cell_.capacity_ah * kSecondsPerHour;
}

double SingleCellBaseModel::compute_ocv() const {
    const double clamped_soc = std::clamp(soc_, 0.0, 1.0);
    const double ocv_span = std::max(cell_.ocv_max - cell_.ocv_min, 0.0);
    return cell_.ocv_min + ocv_span * clamped_soc;
}

double SingleCellBaseModel::compute_current(double speed_mps, double accel_mps2) const {
    const double raw_current = cell_.base_current_a + cell_.speed_current_gain * speed_mps +
                               cell_.accel_current_gain * accel_mps2;
    return std::max(raw_current, 0.0);
}

void SingleCellBaseModel::integrate_soc(double current_a, double dt) {
    if (capacity_coulombs() <= 0.0) {
        return;
    }
    const double delta_soc = (current_a * dt) / capacity_coulombs();
    soc_ = std::clamp(soc_ - delta_soc, 0.0, 1.0);
}

const core::DriveCycleSample& SingleCellBaseModel::drive_sample(std::size_t index) const {
    if (index >= drive_cycle_.samples.size()) {
        return drive_cycle_.samples.back();
    }
    return drive_cycle_.samples[index];
}

std::size_t SingleCellBaseModel::sample_index_for_time(double time) const {
    if (scenario_time_step_ <= 0.0) {
        return 0;
    }
    const auto idx = static_cast<std::size_t>(std::floor(time / scenario_time_step_));
    if (idx >= drive_cycle_.samples.size()) {
        return drive_cycle_.samples.size() - 1;
    }
    return idx;
}

std::string SingleCellBaseModel::signal_name(std::string_view suffix) const {
    std::string result = cell_.cell_id;
    result.append(".");
    result.append(suffix);
    return result;
}

SingleCellOhmicModel::SingleCellOhmicModel() : SingleCellBaseModel("single_cell_ohmic") {}

double SingleCellOhmicModel::compute_terminal_voltage(double current_a, double ocv_v, double dt) {
    (void)dt;
    const double voltage = ocv_v - current_a * cell_.internal_resistance;
    return std::max(voltage, 0.0);
}

SingleCellRcModel::SingleCellRcModel() : SingleCellBaseModel("single_cell_rc") {}

void SingleCellRcModel::on_reset() {
    rc_voltage_v_ = 0.0;
    SingleCellBaseModel::on_reset();
}

double SingleCellRcModel::compute_terminal_voltage(double current_a, double ocv_v, double dt) {
    const double r0 = cell_.internal_resistance;
    const double r1 = std::max(cell_.rc_resistance, 0.0);
    const double tau = std::max(cell_.rc_time_constant_s, 1e-3);
    const double cap = tau / std::max(r1, 1e-6);

    if (cap > 0.0) {
        const double rc_derivative = ((current_a * r1) - rc_voltage_v_) / tau;
        rc_voltage_v_ += rc_derivative * dt;
    } else {
        rc_voltage_v_ = 0.0;
    }

    const double voltage = ocv_v - current_a * (r0 + r1) + rc_voltage_v_;
    return std::max(voltage, 0.0);
}

void SingleCellRcModel::populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                               double terminal_voltage_v, double ocv_v,
                                               double heat_w) const {
    (void)current_a;
    (void)terminal_voltage_v;
    (void)ocv_v;
    (void)heat_w;
    sample.signals[signal_name("rc_surface_voltage_v")] = rc_voltage_v_;
}

SingleCellThermalModel::SingleCellThermalModel() : SingleCellBaseModel("single_cell_thermal") {}

double SingleCellThermalModel::compute_terminal_voltage(double current_a, double ocv_v, double dt) {
    (void)dt;
    const double voltage = ocv_v - current_a * cell_.internal_resistance;
    return std::max(voltage, 0.0);
}

void SingleCellThermalModel::update_temperature(double heat_w, double dt) {
    const double mass = std::max(cell_.mass_kg, 1e-6);
    const double heat_capacity = std::max(cell_.heat_capacity_j_per_kg_k, 1e-3);
    const double thermal_resistance = std::max(cell_.thermal_resistance_k_per_w, 1e-3);

    const double cooling_w = (temperature_c_ - environment_.ambient_temperature_c) / thermal_resistance;
    const double net_heat_w = heat_w - cooling_w;
    const double delta_temp = (net_heat_w / (mass * heat_capacity)) * dt;
    temperature_c_ = std::clamp(temperature_c_ + delta_temp, kKelvinClampMin, kKelvinClampMax);
}

void SingleCellThermalModel::populate_extra_signals(common::TimeseriesSample& sample, double current_a,
                                                    double terminal_voltage_v, double ocv_v,
                                                    double heat_w) const {
    (void)current_a;
    (void)terminal_voltage_v;
    (void)ocv_v;
    sample.signals[signal_name("heat_rejection_w")] =
        (temperature_c_ - environment_.ambient_temperature_c) / std::max(cell_.thermal_resistance_k_per_w, 1e-3);
    sample.signals[signal_name("heat_w")] = heat_w;
}

}  // namespace evsim::models
