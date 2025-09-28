#include "evsim/plugins/Plugin.hpp"

#include "evsim/core/SimulationOrchestrator.hpp"

namespace evsim::plugins {

void PluginRegistry::register_plugin(std::unique_ptr<Plugin> plugin) {
    if (!plugin) {
        return;
    }
    plugins_.emplace_back(std::move(plugin));
}

std::vector<std::string> PluginRegistry::names() const {
    std::vector<std::string> result;
    result.reserve(plugins_.size());
    for (const auto& plugin : plugins_) {
        result.push_back(plugin->name());
    }
    return result;
}

void PluginRegistry::initialize_all(SimulationOrchestrator& orchestrator) {
    for (auto& plugin : plugins_) {
        plugin->register_components(orchestrator);
    }
}

}  // namespace evsim::plugins
