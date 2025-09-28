#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

namespace evsim::common {

struct TimeseriesSample {
    double timestamp{0.0};
    std::unordered_map<std::string, double> signals{};
};

using Timeseries = std::vector<TimeseriesSample>;

}  // namespace evsim::common
