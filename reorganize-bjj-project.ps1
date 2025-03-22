# -----------------------------------------
# BJJ Database Reorganizer Script
# Author: Master Chiefe’s AI Architect
# -----------------------------------------

# Step 1: Create new folder structure
$folders = @(
  "apps/scraper_smoothcomp/utils",
  "apps/scraper_smoothcomp/archive",
  "apps/data_cleaning/archive",
  "data/raw",
  "data/processed",
  "data/final",
  "infra/backend",
  "infra/database",
  "infra/pipelines",
  "reporting/powerbi",
  "reporting/dashboards",
  "reporting/documentation",
  "web/frontend",
  "web/assets",
  "notebooks",
  "docs"
)

foreach ($folder in $folders) {
  New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

# Step 2: Move scrapers
Move-Item -Path "scrapers/Smooth_Comp/SC_*.py" -Destination "apps/scraper_smoothcomp/" -Force

# Step 3: Move utils
Move-Item -Path "scrapers/Smooth_Comp/utils/*.py" -Destination "apps/scraper_smoothcomp/utils/" -Force

# Step 4: Move archive
Move-Item -Path "scrapers/Smooth_Comp/archive/*.py" -Destination "apps/scraper_smoothcomp/archive/" -Force
Move-Item -Path "data/archive/*.py" -Destination "apps/data_cleaning/archive/" -Force

# Step 5: Move test data
if (Test-Path "data/test") {
  Move-Item -Path "data/test" -Destination "data/raw/test" -Force
}

# Step 6: Move notes
if (Test-Path "Some Text about the BJJ Data base worksp.txt") {
  Move-Item -Path "Some Text about the BJJ Data base worksp.txt" -Destination "docs/notes.txt" -Force
}

# Step 7: Clean up old folders
if (Test-Path "scrapers") {
  Remove-Item -Path "scrapers" -Recurse -Force
}
if (Test-Path "data/archive") {
  Remove-Item -Path "data/archive" -Recurse -Force
}

# Step 8: Create sample README files
$readmes = @(
  "apps/scraper_smoothcomp/README.md",
  "apps/data_cleaning/README.md",
  "data/README.md",
  "reporting/documentation/metrics_dictionary.md"
)

foreach ($readme in $readmes) {
  New-Item -ItemType File -Path $readme -Force | Out-Null
}

# Step 9: Write .gitignore
@"
# Byte-compiled
__pycache__/
*.pyc

# Virtual Environment
.venv/
.env

# Data
data/raw/*
!data/raw/sample_*.json
data/processed/*
!data/processed/sample_*.csv
data/final/

# Reporting
*.pbix
reporting/dashboards/
reporting/powerbi/*

# System
.DS_Store
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8 -Force

Write-Host "`n✅ Project structure reorganized successfully, Master Chiefe.`n" -ForegroundColor Green
