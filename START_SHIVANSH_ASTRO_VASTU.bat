@echo off
title Shivansh Astro-Vastu Professional (PC Edition)
cd /d "%~dp0"

:: 1. Auto-unblock all downloaded files to prevent Windows Zone.Identifier restrictions
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File -ErrorAction SilentlyContinue" 2>nul

:: 2. Set Python.NET environment variables for target PC without Python installed
if exist "%~dp0ShivanshAstroVastu\_internal\python311.dll" (
    set "PYTHONNET_PYDLL=%~dp0ShivanshAstroVastu\_internal\python311.dll"
    set "PYTHONNET_RUNTIME_DIR=%~dp0ShivanshAstroVastu\_internal\pythonnet\runtime"
    set "PATH=%~dp0ShivanshAstroVastu;%~dp0ShivanshAstroVastu\_internal;%PATH%"
) else if exist "%~dp0_internal\python311.dll" (
    set "PYTHONNET_PYDLL=%~dp0_internal\python311.dll"
    set "PYTHONNET_RUNTIME_DIR=%~dp0_internal\pythonnet\runtime"
    set "PATH=%~dp0;%~dp0_internal;%PATH%"
)

:: 3. Launch the application
if exist "%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe" (
    cd /d "%~dp0ShivanshAstroVastu"
    start "" "%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe"
    exit
)

if exist "%~dp0ShivanshAstroVastu.exe" (
    start "" "%~dp0ShivanshAstroVastu.exe"
    exit
)

echo [ERROR] ShivanshAstroVastu.exe not found!
pause
