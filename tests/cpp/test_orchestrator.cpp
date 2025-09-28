#include <cassert>
#include <iostream>

#include "evsim/core/Scenario.hpp"
#include "evsim/core/SimulationOrchestrator.hpp"
#include "evsim/models/BatteryPackModel.hpp"
#include "evsim/solvers/EulerSolver.hpp"

int main() {
    evsim::SimulationOrchestrator orchestrator;
    orchestrator.register_model(std::make_unique<evsim::models::BatteryPackModel>());
    orchestrator.register_solver(std::make_unique<evsim::solvers::EulerSolver>());

    evsim::core::Scenario scenario{};
    scenario.id = "smoke";
    scenario.time_step = 1.0;
    scenario.step_count = 10;

    const auto record = orchestrator.run(scenario);
    const auto samples = orchestrator.result_store().samples(record.run_id);

    assert(samples.size() == scenario.step_count);
    assert(samples.front().signals.at("pack.soc") <= 1.0);
    assert(samples.back().signals.at("pack.soc") <= 1.0);

    std::cout << "Simulation produced " << samples.size() << " samples\n";
    return 0;
}
