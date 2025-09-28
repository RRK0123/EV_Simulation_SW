#include "evsim/events/RunEvents.hpp"

namespace evsim::events {

void EventBus::subscribe(Callback callback) {
    std::scoped_lock lock(mutex_);
    subscribers_.emplace_back(std::move(callback));
}

void EventBus::publish(const RunEvent& event) {
    std::vector<Callback> copy;
    {
        std::scoped_lock lock(mutex_);
        copy = subscribers_;
    }
    for (const auto& subscriber : copy) {
        if (subscriber) {
            subscriber(event);
        }
    }
}

}  // namespace evsim::events
