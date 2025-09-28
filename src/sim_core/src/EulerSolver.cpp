#include "evsim/solvers/EulerSolver.hpp"

namespace evsim::solvers {

std::string EulerSolver::name() const { return "euler_solver"; }

void EulerSolver::solve(models::SimulationModel& model, const core::Scenario& scenario,
                        storage::RunRecord& run_record, storage::ResultStore& store, events::EventBus& bus) {
    model.configure(scenario);
    model.reset();

    events::RunEvent start_event{events::RunEventType::Started, run_record.run_id, 0.0, 0.0, "run-started"};
    bus.publish(start_event);

    double time = 0.0;
    for (std::size_t step = 0; step < scenario.step_count; ++step) {
        auto sample = model.step(time, scenario.time_step);
        store.append_sample(run_record, std::move(sample));
        time += scenario.time_step;
        const double pct = static_cast<double>(step + 1) / static_cast<double>(scenario.step_count);
        events::RunEvent progress{events::RunEventType::Progress, run_record.run_id, time, pct, "run-progress"};
        bus.publish(progress);
    }

    events::RunEvent complete{events::RunEventType::Completed, run_record.run_id, time, 1.0, "run-complete"};
    bus.publish(complete);
}

}  // namespace evsim::solvers
