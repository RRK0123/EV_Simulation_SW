#pragma once

#include <memory>
#include <string>
#include <vector>

namespace evsim {
class SimulationOrchestrator;
}

namespace evsim::plugins {

class Plugin {
public:
    virtual ~Plugin() = default;

    virtual std::string name() const = 0;
    virtual void register_components(SimulationOrchestrator& orchestrator) = 0;
};

class PluginRegistry {
public:
    void register_plugin(std::unique_ptr<Plugin> plugin);
    [[nodiscard]] std::vector<std::string> names() const;
    void initialize_all(SimulationOrchestrator& orchestrator);

private:
    std::vector<std::unique_ptr<Plugin>> plugins_{};
};

}  // namespace evsim::plugins
