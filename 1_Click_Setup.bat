@echo off
title 1-Click Setup - Shivansh Astro-Vastu Professional
cd /d "%~dp0"
color 0E
cls
echo ===============================================================================
echo        SHIVANSH ASTRO-VASTU PROFESSIONAL - 1-CLICK SETUP FOR NEW PC
echo                  Mayur Mandhare (BE.E^&TC) - 9373058052
echo ===============================================================================
echo.

echo   [1/3] Setting up Shivansh Astro-Vastu Desktop Icon with Golden Logo...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnkPath = Join-Path $desktop 'Shivansh Astro-Vastu Professional.lnk';" ^
  "$s = $ws.CreateShortcut($lnkPath);" ^
  "if (Test-Path '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0ShivanshAstroVastu'; } elseif (Test-Path '%~dp0ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0'; } else { $s.TargetPath = '%~dp0START_SHIVANSH_ASTRO_VASTU.bat'; $s.WorkingDirectory = '%~dp0'; }" ^
  "if (Test-Path '%~dp0app_icon.ico') { $s.IconLocation = '%~dp0app_icon.ico,0'; } elseif (Test-Path '%~dp0ShivanshAstroVastu\app_icon.ico') { $s.IconLocation = '%~dp0ShivanshAstroVastu\app_icon.ico,0'; }" ^
  "$s.Description = 'Shivansh Astro-Vastu Professional — Offline Vedic & Lal Kitab Software';" ^
  "$s.Save();" ^
  "Write-Host '   Desktop Icon Created Successfully!' -ForegroundColor Green;"

echo   [2/3] Setting up Windows Start Menu Shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$startMenu = [Environment]::GetFolderPath([Environment+SpecialFolder]::Programs);" ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnkPath = Join-Path $startMenu 'Shivansh Astro-Vastu Professional.lnk';" ^
  "$s = $ws.CreateShortcut($lnkPath);" ^
  "if (Test-Path '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0ShivanshAstroVastu'; } elseif (Test-Path '%~dp0ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0'; } else { $s.TargetPath = '%~dp0START_SHIVANSH_ASTRO_VASTU.bat'; $s.WorkingDirectory = '%~dp0'; }" ^
  "if (Test-Path '%~dp0app_icon.ico') { $s.IconLocation = '%~dp0app_icon.ico,0'; } elseif (Test-Path '%~dp0ShivanshAstroVastu\app_icon.ico') { $s.IconLocation = '%~dp0ShivanshAstroVastu\app_icon.ico,0'; }" ^
  "$s.Description = 'Shivansh Astro-Vastu Professional — Offline Vedic & Lal Kitab Software';" ^
  "$s.Save();" ^
  "Write-Host '   Start Menu Shortcut Created Successfully!' -ForegroundColor Green;"

echo.
echo   [3/3] Setup Completed!
echo ===============================================================================
echo   Credentials:
echo     - Username: Admin
echo     - Password: Harman
echo.
echo   Launching Shivansh Astro-Vastu Professional now...
echo ===============================================================================
echo.

if exist "%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe" (
    cd /d "%~dp0ShivanshAstroVastu"
    start "" "%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe"
) else if exist "%~dp0ShivanshAstroVastu.exe" (
    start "" "%~dp0ShivanshAstroVastu.exe"
) else (
    call "%~dp0START_SHIVANSH_ASTRO_VASTU.bat"
)
exit
