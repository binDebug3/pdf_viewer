param(
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Building PDF Viewer with PyInstaller..."

if ($OneFile) {
    python -m PyInstaller --noconfirm --clean --windowed --onefile --name PDFViewer --collect-all PySide6 --hidden-import fitz app/main.py
}
else {
    python -m PyInstaller --noconfirm --clean --windowed --name PDFViewer --collect-all PySide6 --hidden-import fitz app/main.py
}

Write-Host "Build complete. Output directory: dist/PDFViewer"