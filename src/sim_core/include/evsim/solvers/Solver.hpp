#pragma once

#include <string>

#include "evsim/events/RunEvents.hpp"
#include "evsim/models/SimulationModel.hpp"
#include "evsim/storage/ResultStore.hpp"

namespace evsim::solvers {

class Solver {
public:
    virtual ~Solver() = default;

    virtual std::string name() const = 0;
    virtual void solve(models::SimulationModel& model, const core::Scenario& scenario,
                       storage::RunRecord& run_record, storage::ResultStore& store,
                       events::EventBus& bus) = 0;
};

}  // namespace evsim::solvers
