# ---------------------------------------
# Cleanup Script for BJJ Project
# Removes old folders and loose scripts
# ---------------------------------------

# Step 1: Delete legacy folders
$leftovers = @(
  "scrapers",
  "data/archive",
  "data/test",
  "apps/__pycache__",
  "__pycache__",
  ".ipynb_checkpoints"
)

foreach ($folder in $leftovers) {
  if (Test-Path $folder) {
    Remove-Item -Path $folder -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Removed folder: $folder"
  }
}

# Step 2: Move any loose .py files into notebooks
$looseScripts = Get-ChildItem -Path . -Filter *.py -File

foreach ($script in $looseScripts) {
  Move-Item -Path $script.FullName -Destination ("notebooks\" + $script.Name) -Force
  Write-Host "Moved script to notebooks/: $($script.Name)"
}

# Step 3: Confirm completion
Write-Host ""
Write-Host "✅ Cleanup complete, Master Chiefe. Your repo is now sleek and structured." -ForegroundColor Green
