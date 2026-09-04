Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Starting Veritas AI Detector & Humanizer Studio" -ForegroundColor Green
Write-Host "Access at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "====================================================" -ForegroundColor Cyan

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
