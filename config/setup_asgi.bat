@echo off
echo Installing ASGI servers...
pip install daphne uvicorn
echo Installation complete.
echo.
echo Stopping any existing server on port 8001...
powershell -Command "try { Stop-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess -Force -ErrorAction SilentlyContinue } catch { }"
echo.
echo Starting Daphne ASGI server in new terminal...
start "" cmd /c "cd /d ..\security_project && daphne -p 8001 monitoring.asgi:application"
