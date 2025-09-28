#include "evsim/io/Registry.hpp"

namespace evsim::io {

void ImporterRegistry::register_importer(std::unique_ptr<DataImporter> importer) {
    if (!importer) {
        return;
    }
    importers_[importer->format()] = std::move(importer);
}

std::vector<std::string> ImporterRegistry::formats() const {
    std::vector<std::string> keys;
    keys.reserve(importers_.size());
    for (const auto& [key, _] : importers_) {
        keys.push_back(key);
    }
    return keys;
}

DataImporter* ImporterRegistry::find_by_format(const std::string& format) const {
    auto iter = importers_.find(format);
    if (iter == importers_.end()) {
        return nullptr;
    }
    return iter->second.get();
}

void ExporterRegistry::register_exporter(std::unique_ptr<DataExporter> exporter) {
    if (!exporter) {
        return;
    }
    exporters_[exporter->format()] = std::move(exporter);
}

std::vector<std::string> ExporterRegistry::formats() const {
    std::vector<std::string> keys;
    keys.reserve(exporters_.size());
    for (const auto& [key, _] : exporters_) {
        keys.push_back(key);
    }
    return keys;
}

DataExporter* ExporterRegistry::find_by_format(const std::string& format) const {
    auto iter = exporters_.find(format);
    if (iter == exporters_.end()) {
        return nullptr;
    }
    return iter->second.get();
}

}  // namespace evsim::io
