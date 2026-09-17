@echo off
python "%~dp0scripts\check_environment.py"
if errorlevel 1 (
  echo Python 3.10+ with Tcl/Tk is required. Install Python and add it to PATH.
  pause
  exit /b 1
)
python -c "import pathlib,subprocess,sys; p=pathlib.Path(sys.executable).with_name('pythonw.exe'); subprocess.Popen([str(p),sys.argv[1]])" "%~dp0scripts\desktop.py"
if errorlevel 1 (
  echo Unable to start the garden. Check that pythonw.exe is installed with Python.
  pause
  exit /b 1
)
