#include "evsim/core/c_api.h"

#include <memory>
#include "evsim/core/Scenario.hpp"

#include "evsim/core/SimulationOrchestrator.hpp"
#include "evsim/models/BatteryPackModel.hpp"
#include "evsim/solvers/EulerSolver.hpp"

namespace {

struct OrchestratorHolder {
    evsim::SimulationOrchestrator orchestrator;

    OrchestratorHolder() {
        orchestrator.register_model(std::make_unique<evsim::models::BatteryPackModel>());
        orchestrator.register_solver(std::make_unique<evsim::solvers::EulerSolver>());
    }
};

}  // namespace

extern "C" {

evsim_orchestrator_handle evsim_create_orchestrator() {
    try {
        return new OrchestratorHolder();
    } catch (...) {
        return nullptr;
    }
}

void evsim_destroy_orchestrator(evsim_orchestrator_handle handle) {
    auto* holder = static_cast<OrchestratorHolder*>(handle);
    delete holder;
}

int evsim_run_default_scenario(evsim_orchestrator_handle handle, double time_step, std::uint32_t steps) {
    if (handle == nullptr) {
        return -1;
    }

    auto* holder = static_cast<OrchestratorHolder*>(handle);
    evsim::core::Scenario scenario{};
    scenario.id = "default";
    scenario.description = "Default battery pack discharge";
    scenario.time_step = time_step;
    scenario.step_count = steps;

    try {
        holder->orchestrator.run(scenario);
    } catch (...) {
        return -2;
    }
    return 0;
}

}  // extern "C"
