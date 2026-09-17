@echo off
python "%~dp0scripts\check_environment.py"
if errorlevel 1 (
  echo Install Python 3.10+ with Tcl/Tk and add Python to PATH, then retry.
  pause
  exit /b 1
)
pause
