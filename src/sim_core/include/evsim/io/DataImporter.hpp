#pragma once

#include <filesystem>
#include <memory>
#include <string>

#include "evsim/common/TimeseriesSample.hpp"

namespace evsim::io {

struct ImportedDataset {
    std::string name;
    common::Timeseries samples;
};

class DataImporter {
public:
    virtual ~DataImporter() = default;

    virtual std::string format() const = 0;
    virtual bool supports(const std::filesystem::path& path) const = 0;
    virtual ImportedDataset import_from(const std::filesystem::path& path) = 0;
};

class DataExporter {
public:
    virtual ~DataExporter() = default;

    virtual std::string format() const = 0;
    virtual void export_to(const std::filesystem::path& path, const common::Timeseries& samples) = 0;
};

}  // namespace evsim::io
