$ErrorActionPreference = "Stop"

if (-not (Test-Path "models\hand_landmarker.task")) {
    throw "Missing models\hand_landmarker.task. Download the official model before building."
}

python -m pip install -e ".[build]"
python -m PyInstaller --clean --noconfirm GestureControl.spec
Write-Host "Built dist\GestureControl.exe"
