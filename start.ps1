# ============================================================
#  Intelligent Study Planner — One-Click Start Script
#  Run from project root: .\start.ps1
# ============================================================

$ROOT = $PSScriptRoot
$BACKEND  = "$ROOT\backend"
$FRONTEND = "$ROOT\frontend"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Intelligent Study Planner — Starting Up  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Activate Python virtual environment ──────────────────
Write-Host "[1/4] Activating Python virtual environment..." -ForegroundColor Yellow
$VENV_ACTIVATE = "$BACKEND\.venv\Scripts\Activate.ps1"
if (-Not (Test-Path $VENV_ACTIVATE)) {
    Write-Host "      venv not found. Creating one..." -ForegroundColor Gray
    python -m venv "$BACKEND\.venv"
}
& $VENV_ACTIVATE

# ── 2. Install Python dependencies ─────────────────────────
Write-Host "[2/4] Installing backend dependencies..." -ForegroundColor Yellow
pip install -r "$BACKEND\requirements.txt" --quiet

# ── Stop any lingering previous instances to prevent [WinError 10013] ──
Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

# ── 3. Launch Backend (FastAPI) in a new terminal window ────
Write-Host "[3/4] Starting FastAPI backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& '$BACKEND\.venv\Scripts\Activate.ps1'; Set-Location '$BACKEND'; Write-Host 'Backend running at http://127.0.0.1:8000' -ForegroundColor Green; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
) -WindowStyle Normal

# Give the backend a moment to start
Start-Sleep -Seconds 3

# ── 4. Launch Frontend (Vite) in a new terminal window ──────
Write-Host "[4/4] Starting Vite frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$FRONTEND'; Write-Host 'Frontend running at http://localhost:5173' -ForegroundColor Green; npm run dev"
) -WindowStyle Normal

# Give Vite a moment to start
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services are starting up!             " -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend  -> http://localhost:5173        " -ForegroundColor White
Write-Host "  Backend   -> http://localhost:8000        " -ForegroundColor White
Write-Host "  API Docs  -> http://localhost:8000/docs   " -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Open browser automatically
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"
