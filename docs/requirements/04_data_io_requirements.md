# 04 — Data I/O Requirements (MDF/MDF4/DAT)

> IDs: `IO-###`

## 4.1 Canonical Schema (excerpt)
- **Index**: `timestamp` (ns), `sample_id` (int)
- **Channels**: `pack.V [V]`, `pack.I [A]`, `pack.T_mean [°C]`, `soc [%]`, `soh [%]`, `veh_speed [m/s]`, `ambient.T [°C]`
- **Metadata**: `run_id`, `scenario_id`, `git_sha`, `seed`, `sim_version`

### IO-001 (MUST)
Importers SHALL provide a **mapping UI** (auto + manual) to map external channels → canonical names and units.

### IO-002 (MUST)
Exporters SHALL include units, sampling rate, channel metadata, and lossless time base.

### IO-003 (MUST)
Large-file strategy: streaming parse, chunk size configurable, memory cap with back-pressure.

### IO-004 (SHOULD)
Unit registry: conversions (km/h ↔ m/s, °C ↔ K) applied consistently; mismatches flagged.

### IO-005 (MUST)
Checksum artifacts (SHA-256) and store alongside exported files.

## 4.2 File Format Specifics
- **MDF4**: Hierarchical groups; channel groups per subsystem; compression optional.
- **MDF**: Legacy handling; warn on lossy mappings.
- **DAT**: Define project DAT spec (header + CSV-like body or binary), including required columns and units.

## 4.3 Example Mapping Table
| Canonical | Example MDF | Unit | Note |
|---|---|---|---|
| `pack.V` | `BATT_Pack_V` | V | Avg pack voltage |
| `pack.I` | `BATT_Pack_I` | A | Positive=discharge |
| `soc` | `BATT_SOC` | % | 0–100 |
| `veh_speed` | `Vehicle_Speed` | km/h | Convert to m/s |
