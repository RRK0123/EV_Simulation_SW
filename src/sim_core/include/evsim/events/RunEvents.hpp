#pragma once

#include <functional>
#include <mutex>
#include <string>
#include <vector>

namespace evsim::events {

enum class RunEventType { Started, Progress, Completed, Failed };

struct RunEvent {
    RunEventType type{RunEventType::Started};
    std::string run_id;
    double timestamp{0.0};
    double progress{0.0};
    std::string message;
};

class EventBus {
public:
    using Callback = std::function<void(const RunEvent&)>;

    void subscribe(Callback callback);
    void publish(const RunEvent& event);

private:
    std::mutex mutex_{};
    std::vector<Callback> subscribers_{};
};

}  // namespace evsim::events
