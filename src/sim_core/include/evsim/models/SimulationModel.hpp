#pragma once

#include <string>

#include "evsim/common/TimeseriesSample.hpp"
#include "evsim/core/Scenario.hpp"

namespace evsim::models {

class SimulationModel {
public:
    virtual ~SimulationModel() = default;

    virtual std::string name() const = 0;
    virtual void configure(const core::Scenario& scenario) = 0;
    virtual void reset() = 0;
    virtual common::TimeseriesSample step(double time, double dt) = 0;
};

}  // namespace evsim::models
