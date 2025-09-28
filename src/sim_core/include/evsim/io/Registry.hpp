#pragma once

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "evsim/io/DataImporter.hpp"

namespace evsim::io {

class ImporterRegistry {
public:
    void register_importer(std::unique_ptr<DataImporter> importer);
    [[nodiscard]] std::vector<std::string> formats() const;
    DataImporter* find_by_format(const std::string& format) const;

private:
    std::unordered_map<std::string, std::unique_ptr<DataImporter>> importers_{};
};

class ExporterRegistry {
public:
    void register_exporter(std::unique_ptr<DataExporter> exporter);
    [[nodiscard]] std::vector<std::string> formats() const;
    DataExporter* find_by_format(const std::string& format) const;

private:
    std::unordered_map<std::string, std::unique_ptr<DataExporter>> exporters_{};
};

}  // namespace evsim::io
