#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace evsim::core {

struct ScenarioParameter {
    std::string name;
    double value{0.0};
};

struct Scenario {
    std::string id;
    std::string description;
    double time_step{0.1};
    std::size_t step_count{0};
    std::vector<ScenarioParameter> parameters{};

    [[nodiscard]] double duration() const noexcept { return time_step * static_cast<double>(step_count); }
};

}  // namespace evsim::core
