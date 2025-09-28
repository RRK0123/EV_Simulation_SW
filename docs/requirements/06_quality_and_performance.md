# 06 — Quality, Performance, Security

> IDs: `Q-###`

## 6.1 Performance
- **Q-101 (MUST)** 10 Hz × 3600 s in < 5 min (reference hardware).
- **Q-102 (MUST)** Import 1 GB MDF4 < 60 s; export 500 MB MDF4 < 45 s.

## 6.2 Reliability & Observability
- **Q-110 (MUST)** Deterministic re-run under fixed seed/config.
- **Q-111 (MUST)** Structured logs with `run_id`, timings, and error codes.
- **Q-112 (SHOULD)** Crash-safe output with atomic moves/WAL.

## 6.3 Security
- **Q-120 (MUST)** No outbound network by default; opt-in cloud sync.
- **Q-121 (MUST)** SHA-256 for exported artifacts; optional signature.

## 6.4 Compatibility
- **Q-130 (MUST)** Windows/Linux parity; Mac best-effort.
