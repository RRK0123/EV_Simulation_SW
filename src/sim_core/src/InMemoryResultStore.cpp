#include "evsim/storage/ResultStore.hpp"

#include <sstream>

namespace evsim::storage {

RunRecord InMemoryResultStore::start_run(const core::Scenario& scenario) {
    RunRecord record{};
    std::ostringstream oss;
    oss << "run_" << ++counter_;
    record.run_id = oss.str();
    record.scenario = scenario;
    storage_.emplace(record.run_id, std::vector<common::TimeseriesSample>{});
    return record;
}

void InMemoryResultStore::append_sample(const RunRecord& record, common::TimeseriesSample sample) {
    storage_.at(record.run_id).emplace_back(std::move(sample));
}

void InMemoryResultStore::complete_run(const RunRecord& record) {
    (void)record;
}

std::vector<common::TimeseriesSample> InMemoryResultStore::samples(const std::string& run_id) const {
    auto iter = storage_.find(run_id);
    if (iter == storage_.end()) {
        return {};
    }
    return iter->second;
}

}  // namespace evsim::storage
