#pragma once

#include <cstddef>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include "evsim/common/TimeseriesSample.hpp"
#include "evsim/core/Scenario.hpp"

namespace evsim::storage {

struct RunRecord {
    std::string run_id;
    core::Scenario scenario;
};

class ResultStore {
public:
    virtual ~ResultStore() = default;

    virtual RunRecord start_run(const core::Scenario& scenario) = 0;
    virtual void append_sample(const RunRecord& record, common::TimeseriesSample sample) = 0;
    virtual void complete_run(const RunRecord& record) = 0;
    virtual std::vector<common::TimeseriesSample> samples(const std::string& run_id) const = 0;
};

class InMemoryResultStore final : public ResultStore {
public:
    RunRecord start_run(const core::Scenario& scenario) override;
    void append_sample(const RunRecord& record, common::TimeseriesSample sample) override;
    void complete_run(const RunRecord& record) override;
    std::vector<common::TimeseriesSample> samples(const std::string& run_id) const override;

private:
    std::unordered_map<std::string, std::vector<common::TimeseriesSample>> storage_{};
    std::size_t counter_{0};
};

}  // namespace evsim::storage
