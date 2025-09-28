#include "evsim/core/SimulationOrchestrator.hpp"

#include <stdexcept>

namespace evsim {

SimulationOrchestrator::SimulationOrchestrator()
    : result_store_(std::make_unique<storage::InMemoryResultStore>()) {}

void SimulationOrchestrator::set_result_store(std::unique_ptr<storage::ResultStore> store) {
    if (store) {
        result_store_ = std::move(store);
    }
}

storage::ResultStore& SimulationOrchestrator::result_store() { return *result_store_; }

const storage::ResultStore& SimulationOrchestrator::result_store() const { return *result_store_; }

void SimulationOrchestrator::register_model(std::unique_ptr<models::SimulationModel> model) {
    if (!model) {
        throw std::invalid_argument("model cannot be null");
    }
    models_.emplace_back(std::move(model));
}

void SimulationOrchestrator::register_solver(std::unique_ptr<solvers::Solver> solver) {
    if (!solver) {
        throw std::invalid_argument("solver cannot be null");
    }
    solvers_.emplace_back(std::move(solver));
}

std::vector<std::string> SimulationOrchestrator::model_names() const {
    std::vector<std::string> names;
    names.reserve(models_.size());
    for (const auto& model : models_) {
        names.push_back(model->name());
    }
    return names;
}

std::vector<std::string> SimulationOrchestrator::solver_names() const {
    std::vector<std::string> names;
    names.reserve(solvers_.size());
    for (const auto& solver : solvers_) {
        names.push_back(solver->name());
    }
    return names;
}

storage::RunRecord SimulationOrchestrator::run(const core::Scenario& scenario) {
    if (models_.empty()) {
        throw std::runtime_error("no models registered");
    }
    if (solvers_.empty()) {
        throw std::runtime_error("no solvers registered");
    }

    auto record = result_store_->start_run(scenario);
    auto& model = *models_.front();
    auto& solver = *solvers_.front();
    solver.solve(model, scenario, record, *result_store_, event_bus_);
    result_store_->complete_run(record);
    return record;
}

events::EventBus& SimulationOrchestrator::event_bus() { return event_bus_; }

io::ImporterRegistry& SimulationOrchestrator::importer_registry() { return importer_registry_; }

io::ExporterRegistry& SimulationOrchestrator::exporter_registry() { return exporter_registry_; }

plugins::PluginRegistry& SimulationOrchestrator::plugin_registry() { return plugin_registry_; }

}  // namespace evsim
