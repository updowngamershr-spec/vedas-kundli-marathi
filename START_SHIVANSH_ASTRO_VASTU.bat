@echo off
title Shivansh Astro-Vastu Professional (PC Edition)
cd /d "%~dp0"

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
