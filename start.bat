@echo off
setlocal
cd /d "%~dp0"
title Pages Converter

where python >nul 2>nul
if errorlevel 1 (
  echo [Pages Converter] Python was not found.
  echo Install Python 3 from https://www.python.org/downloads/windows/
  echo Enable "Add Python to PATH" during installation.
  pause
  exit /b 1
)

set "SOFFICE=%ProgramFiles%\LibreOffice\program\soffice.exe"
if not exist "%SOFFICE%" set "SOFFICE=%ProgramFiles(x86)%\LibreOffice\program\soffice.exe"
if not exist "%SOFFICE%" (
  where soffice >nul 2>nul
  if errorlevel 1 (
    echo [Pages Converter] LibreOffice was not found.
    echo Install it from https://www.libreoffice.org/download/download-libreoffice/
    pause
    exit /b 1
  )
)

start "" /b cmd /c "ping 127.0.0.1 -n 3 ^>nul ^& start http://127.0.0.1:8765"
python app.py

if errorlevel 1 (
  echo.
  echo Pages Converter stopped with an error.
  pause
)
