#pragma once

#include "evsim/solvers/Solver.hpp"

namespace evsim::solvers {

class EulerSolver final : public Solver {
public:
    std::string name() const override;
    void solve(models::SimulationModel& model, const core::Scenario& scenario,
               storage::RunRecord& run_record, storage::ResultStore& store,
               events::EventBus& bus) override;
};

}  // namespace evsim::solvers
