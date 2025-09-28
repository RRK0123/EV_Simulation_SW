#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <string_view>
#include <stdexcept>
#include <vector>

#include "evsim/common/TimeseriesSample.hpp"
#include "evsim/core/Scenario.hpp"
#include "evsim/core/SimulationOrchestrator.hpp"
#include "evsim/io/WltpCsvLoader.hpp"
#include "evsim/models/SingleCellModels.hpp"
#include "evsim/solvers/EulerSolver.hpp"
#include "evsim/storage/ResultStore.hpp"

namespace {

struct CliOptions {
    std::filesystem::path wltp_csv;
    std::filesystem::path output_dat{"wltp_single_cell_results.dat"};
    double ambient_c{25.0};
};

void print_usage() {
    std::cout << "Usage: wltp_single_cell_cli --wltp <path> [--output <file>] [--ambient <degC>]" << std::endl;
}

bool parse_arguments(int argc, char** argv, CliOptions& options) {
    if (argc <= 1) {
        print_usage();
        return false;
    }
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg = argv[i];
        if (arg == "--wltp" && i + 1 < argc) {
            options.wltp_csv = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            options.output_dat = argv[++i];
        } else if (arg == "--ambient" && i + 1 < argc) {
            options.ambient_c = std::stod(argv[++i]);
        } else if (arg == "--help" || arg == "-h") {
            print_usage();
            return false;
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            print_usage();
            return false;
        }
    }
    if (options.wltp_csv.empty()) {
        std::cerr << "Missing required --wltp argument" << std::endl;
        print_usage();
        return false;
    }
    return true;
}

evsim::core::CellDefinition make_cell_definition(std::string id, std::string chemistry,
                                                  evsim::core::CellModelKind kind, double nominal_v,
                                                  double capacity_ah, double resistance_ohm) {
    evsim::core::CellDefinition cell{};
    cell.cell_id = std::move(id);
    cell.chemistry = std::move(chemistry);
    cell.model_kind = kind;
    cell.nominal_voltage = nominal_v;
    cell.capacity_ah = capacity_ah;
    cell.internal_resistance = resistance_ohm;
    return cell;
}

evsim::core::Scenario make_scenario(const evsim::core::DriveCycle& drive_cycle,
                                     const evsim::core::CellDefinition& cell,
                                     double ambient_c) {
    evsim::core::Scenario scenario{};
    scenario.id = cell.cell_id + "_WLTP";
    scenario.description = "WLTP single-cell simulation for " + cell.cell_id;
    scenario.time_step = drive_cycle.sample_interval;
    scenario.step_count = drive_cycle.samples.size();
    scenario.drive_cycle = drive_cycle;
    scenario.active_cell_id = cell.cell_id;
    scenario.cells = {cell};
    scenario.environment.ambient_temperature_c = ambient_c;
    scenario.environment.initial_cell_temperature_c = ambient_c;
    return scenario;
}

std::unique_ptr<evsim::models::SimulationModel> make_model(evsim::core::CellModelKind kind) {
    switch (kind) {
        case evsim::core::CellModelKind::Ohmic:
            return std::make_unique<evsim::models::SingleCellOhmicModel>();
        case evsim::core::CellModelKind::Rc:
            return std::make_unique<evsim::models::SingleCellRcModel>();
        case evsim::core::CellModelKind::Thermal:
            return std::make_unique<evsim::models::SingleCellThermalModel>();
    }
    throw std::invalid_argument("Unsupported cell model kind");
}

void apply_cell_specific_parameters(evsim::core::CellDefinition& cell) {
    if (cell.model_kind == evsim::core::CellModelKind::Ohmic) {
        cell.base_current_a = 2.0;
        cell.speed_current_gain = 0.55;
        cell.accel_current_gain = 3.0;
        cell.ocv_min = 3.0;
        cell.ocv_max = cell.nominal_voltage + 0.6;
    } else if (cell.model_kind == evsim::core::CellModelKind::Rc) {
        cell.base_current_a = 2.5;
        cell.speed_current_gain = 0.6;
        cell.accel_current_gain = 3.5;
        cell.rc_time_constant_s = 8.0;
        cell.rc_resistance = 0.0045;
        cell.ocv_min = 2.9;
        cell.ocv_max = cell.nominal_voltage + 0.5;
    } else if (cell.model_kind == evsim::core::CellModelKind::Thermal) {
        cell.base_current_a = 3.0;
        cell.speed_current_gain = 0.65;
        cell.accel_current_gain = 4.0;
        cell.mass_kg = 0.047;
        cell.surface_area_m2 = 0.013;
        cell.heat_capacity_j_per_kg_k = 910.0;
        cell.thermal_resistance_k_per_w = 1.2;
        cell.ocv_min = 3.1;
        cell.ocv_max = cell.nominal_voltage + 0.55;
    }
}

std::vector<evsim::core::CellDefinition> build_default_cells() {
    std::vector<evsim::core::CellDefinition> cells;
    auto nmc = make_cell_definition("NMC811", "NMC811", evsim::core::CellModelKind::Ohmic, 3.65, 5.0, 0.012);
    apply_cell_specific_parameters(nmc);
    auto lfp = make_cell_definition("LFP", "LFP", evsim::core::CellModelKind::Rc, 3.2, 4.8, 0.015);
    apply_cell_specific_parameters(lfp);
    auto nca = make_cell_definition("NCA", "NCA", evsim::core::CellModelKind::Thermal, 3.6, 4.5, 0.011);
    apply_cell_specific_parameters(nca);
    cells.push_back(nmc);
    cells.push_back(lfp);
    cells.push_back(nca);
    return cells;
}

std::vector<std::string> order_columns(const std::set<std::string>& names) {
    std::vector<std::string> ordered(names.begin(), names.end());
    std::sort(ordered.begin(), ordered.end(), [](const std::string& lhs, const std::string& rhs) {
        const bool lhs_drive = lhs.rfind("drive.", 0) == 0;
        const bool rhs_drive = rhs.rfind("drive.", 0) == 0;
        if (lhs_drive != rhs_drive) {
            return lhs_drive > rhs_drive;
        }
        return lhs < rhs;
    });
    return ordered;
}

void write_dat(const std::filesystem::path& path,
               const std::map<double, std::map<std::string, double>>& table,
               const std::vector<std::string>& columns, const CliOptions& options,
               const evsim::core::DriveCycle& cycle,
               const std::vector<evsim::core::CellDefinition>& cells) {
    std::ofstream out(path);
    if (!out.is_open()) {
        throw std::runtime_error("Unable to open output file " + path.string());
    }

    out << "# WLTP single-cell simulation export" << '\n';
    out << "# WLTP source: " << cycle.source << '\n';
    out << "# Ambient temperature [C]: " << options.ambient_c << '\n';
    out << "# Cells:" << '\n';
    for (const auto& cell : cells) {
        out << "#   - " << cell.cell_id << " (" << cell.chemistry << ", model: ";
        switch (cell.model_kind) {
            case evsim::core::CellModelKind::Ohmic:
                out << "ohmic";
                break;
            case evsim::core::CellModelKind::Rc:
                out << "rc";
                break;
            case evsim::core::CellModelKind::Thermal:
                out << "thermal";
                break;
        }
        out << ", capacity: " << cell.capacity_ah << " Ah)" << '\n';
    }

    out << "time_s";
    for (const auto& name : columns) {
        out << '\t' << name;
    }
    out << '\n';

    for (const auto& [time, signals] : table) {
        out << time;
        for (const auto& name : columns) {
            const auto iter = signals.find(name);
            if (iter != signals.end()) {
                out << '\t' << iter->second;
            } else {
                out << '\t' << "nan";
            }
        }
        out << '\n';
    }
}

}  // namespace

int main(int argc, char** argv) {
    CliOptions options;
    if (!parse_arguments(argc, argv, options)) {
        return 1;
    }

    try {
        const auto cycle = evsim::io::load_wltp_csv(options.wltp_csv);
        auto cells = build_default_cells();

        std::map<double, std::map<std::string, double>> table;
        std::set<std::string> columns;

        for (auto& cell : cells) {
            auto scenario = make_scenario(cycle, cell, options.ambient_c);
            auto orchestrator = evsim::SimulationOrchestrator();
            orchestrator.register_solver(std::make_unique<evsim::solvers::EulerSolver>());
            orchestrator.register_model(make_model(cell.model_kind));

            const auto record = orchestrator.run(scenario);
            const auto samples = orchestrator.result_store().samples(record.run_id);
            for (const auto& sample : samples) {
                auto& row = table[sample.timestamp];
                for (const auto& [name, value] : sample.signals) {
                    row[name] = value;
                    columns.insert(name);
                }
            }
        }

        const auto ordered_columns = order_columns(columns);
        write_dat(options.output_dat, table, ordered_columns, options, cycle, cells);
        std::cout << "Exported " << table.size() << " samples to " << options.output_dat << std::endl;
    } catch (const std::exception& ex) {
        std::cerr << "Simulation failed: " << ex.what() << std::endl;
        return 2;
    }

    return 0;
}
