#include "evsim/io/WltpCsvLoader.hpp"

#include <fstream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace evsim::io {

namespace {
constexpr std::string_view kHeaderTime = "time_s";
constexpr std::string_view kHeaderPhase = "phase";
constexpr std::string_view kHeaderSpeed = "speed_kph";
constexpr std::string_view kHeaderDistance = "distance_m";

double parse_double(const std::string& value) {
    try {
        size_t index = 0;
        const double result = std::stod(value, &index);
        if (index != value.size()) {
            throw std::invalid_argument("Trailing characters in numeric value");
        }
        return result;
    } catch (const std::exception& ex) {
        throw std::invalid_argument("Failed to parse numeric value '" + value + "': " + ex.what());
    }
}

}  // namespace

core::DriveCycle load_wltp_csv(const std::filesystem::path& path) {
    std::ifstream stream(path);
    if (!stream.is_open()) {
        throw std::runtime_error("Unable to open WLTP CSV at " + path.string());
    }

    core::DriveCycle cycle{};
    cycle.id = "WLTP_Class3";
    cycle.description = "WLTP Class 3 representative cycle";
    cycle.source = path.string();

    std::string header_line;
    if (!std::getline(stream, header_line)) {
        throw std::runtime_error("WLTP CSV is empty: " + path.string());
    }

    std::vector<std::string> headers;
    {
        std::stringstream header_stream(header_line);
        std::string token;
        while (std::getline(header_stream, token, ',')) {
            headers.push_back(token);
        }
    }

    if (headers.size() < 3) {
        throw std::runtime_error("WLTP CSV header must contain at least three columns");
    }

    std::size_t time_index = std::numeric_limits<std::size_t>::max();
    std::size_t phase_index = std::numeric_limits<std::size_t>::max();
    std::size_t speed_index = std::numeric_limits<std::size_t>::max();
    std::size_t distance_index = std::numeric_limits<std::size_t>::max();

    for (std::size_t i = 0; i < headers.size(); ++i) {
        if (headers[i] == kHeaderTime) {
            time_index = i;
        } else if (headers[i] == kHeaderPhase) {
            phase_index = i;
        } else if (headers[i] == kHeaderSpeed) {
            speed_index = i;
        } else if (headers[i] == kHeaderDistance) {
            distance_index = i;
        }
    }

    if (time_index == std::numeric_limits<std::size_t>::max() ||
        speed_index == std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("WLTP CSV must contain time_s and speed_kph columns");
    }

    std::string line;
    double last_timestamp = 0.0;
    bool first_sample = true;
    while (std::getline(stream, line)) {
        if (line.empty()) {
            continue;
        }
        std::stringstream line_stream(line);
        std::string cell;
        std::vector<std::string> columns;
        while (std::getline(line_stream, cell, ',')) {
            columns.push_back(cell);
        }
        if (columns.size() < headers.size()) {
            columns.resize(headers.size());
        }

        core::DriveCycleSample sample{};
        sample.timestamp = parse_double(columns.at(time_index));
        sample.speed_kph = parse_double(columns.at(speed_index));
        if (distance_index != std::numeric_limits<std::size_t>::max()) {
            sample.distance_m = parse_double(columns.at(distance_index));
        }
        if (phase_index != std::numeric_limits<std::size_t>::max()) {
            sample.phase = columns.at(phase_index);
        }
        if (first_sample) {
            first_sample = false;
        } else {
            cycle.sample_interval = sample.timestamp - last_timestamp;
        }
        last_timestamp = sample.timestamp;
        cycle.samples.emplace_back(std::move(sample));
    }

    if (cycle.samples.empty()) {
        throw std::runtime_error("WLTP CSV did not contain samples");
    }

    if (cycle.sample_interval <= 0.0) {
        cycle.sample_interval = 1.0;
    }

    return cycle;
}

}  // namespace evsim::io
