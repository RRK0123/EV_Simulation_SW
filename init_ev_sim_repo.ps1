# Usage: run from the root of EV_Simulation_SW repo in PowerShell
param(
  [switch]$Commit
)

$dirs = @(
  'app/ui_qt','app/resources',
  'core/orchestrator','core/models','core/solvers','core/plugins',
  'io/importers/mdf','io/importers/dat','io/exporters/mdf','io/exporters/dat',
  'storage','configs/schemas','tests','docs/architecture','scripts','.github/workflows'
)

foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$gitkeepDirs = @(
  'app/ui_qt','app/resources',
  'core/orchestrator','core/models','core/solvers','core/plugins',
  'io/importers/mdf','io/importers/dat','io/exporters/mdf','io/exporters/dat',
  'storage','configs/schemas','tests','scripts'
)
foreach ($d in $gitkeepDirs) { New-Item -ItemType File -Force -Path (Join-Path $d '.gitkeep') | Out-Null }

# Move docs if present
if (Test-Path 'system_software_architecture_safe.md') {
  Move-Item -Force 'system_software_architecture_safe.md' 'docs/architecture/system_software_architecture.md'
}
if (Test-Path 'system_software_architecture.pdf') {
  Move-Item -Force 'system_software_architecture.pdf' 'docs/architecture/system_software_architecture.pdf'
}
# Move workflow if present
if (Test-Path 'build-arch-pdf.yml') {
  Move-Item -Force 'build-arch-pdf.yml' '.github/workflows/build-arch-pdf.yml'
}

# README links
if (Test-Path 'README.md') {
  $content = Get-Content 'README.md' -Raw
  if ($content -notmatch 'System & Software Architecture \(Markdown\)') {
    Add-Content -Path 'README.md' -Value @'
## Documentation
- [System & Software Architecture (Markdown)](docs/architecture/system_software_architecture.md)
- [System & Software Architecture (PDF)](docs/architecture/system_software_architecture.pdf)
'@
  }
} else {
  Set-Content -Path 'README.md' -Value @'
# EV_Simulation_SW

## Documentation
- [System & Software Architecture (Markdown)](docs/architecture/system_software_architecture.md)
- [System & Software Architecture (PDF)](docs/architecture/system_software_architecture.pdf)
'@
}

if ($Commit) {
  git add .
  git commit -m "chore: initialize repo structure and docs"
  try { git push origin main } catch {}
}

Write-Host "✅ Repo structure created. Use -Commit to auto-commit and push."
