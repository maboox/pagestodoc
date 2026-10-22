@echo off
setlocal
cd /d "%~dp0"
title Pages Converter
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py %*
  goto finished
)
where python >nul 2>nul
if not errorlevel 1 (
  python bootstrap.py %*
  goto finished
)
echo Python 3.10 or newer was not found.
echo Install Python from https://www.python.org/downloads/windows/
echo Enable "Add Python to PATH" during installation.
pause
exit /b 1
:finished
if errorlevel 1 (
  echo.
  echo Pages Converter could not start. See the message above.
  pause
  exit /b 1
)
