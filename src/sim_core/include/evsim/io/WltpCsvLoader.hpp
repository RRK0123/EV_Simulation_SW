#pragma once

#include <filesystem>

#include "evsim/core/Scenario.hpp"

namespace evsim::io {

core::DriveCycle load_wltp_csv(const std::filesystem::path& path);

}  // namespace evsim::io
