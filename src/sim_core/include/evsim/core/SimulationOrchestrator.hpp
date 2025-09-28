#pragma once

#include <memory>
#include <string>
#include <vector>

#include "evsim/events/RunEvents.hpp"
#include "evsim/io/Registry.hpp"
#include "evsim/models/SimulationModel.hpp"
#include "evsim/plugins/Plugin.hpp"
#include "evsim/solvers/Solver.hpp"
#include "evsim/storage/ResultStore.hpp"

namespace evsim {

class SimulationOrchestrator {
public:
    SimulationOrchestrator();

    void set_result_store(std::unique_ptr<storage::ResultStore> store);
    storage::ResultStore& result_store();
    const storage::ResultStore& result_store() const;

    void register_model(std::unique_ptr<models::SimulationModel> model);
    void register_solver(std::unique_ptr<solvers::Solver> solver);

    [[nodiscard]] std::vector<std::string> model_names() const;
    [[nodiscard]] std::vector<std::string> solver_names() const;

    storage::RunRecord run(const core::Scenario& scenario);

    events::EventBus& event_bus();
    io::ImporterRegistry& importer_registry();
    io::ExporterRegistry& exporter_registry();
    plugins::PluginRegistry& plugin_registry();

private:
    std::unique_ptr<storage::ResultStore> result_store_;
    std::vector<std::unique_ptr<models::SimulationModel>> models_{};
    std::vector<std::unique_ptr<solvers::Solver>> solvers_{};
    events::EventBus event_bus_{};
    io::ImporterRegistry importer_registry_{};
    io::ExporterRegistry exporter_registry_{};
    plugins::PluginRegistry plugin_registry_{};
};

}  // namespace evsim
