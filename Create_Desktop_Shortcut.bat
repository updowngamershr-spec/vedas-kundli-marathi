@echo off
title Create Desktop Shortcut - Shivansh Astro-Vastu Professional
cd /d "%~dp0"
color 0A
cls
echo ===============================================================================
echo            CREATING SHIVANSH ASTRO-VASTU DESKTOP SHORTCUT
echo ===============================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnkPath = Join-Path $desktop 'Shivansh Astro-Vastu Professional.lnk';" ^
  "$s = $ws.CreateShortcut($lnkPath);" ^
  "if (Test-Path '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu\ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0ShivanshAstroVastu'; } elseif (Test-Path '%~dp0ShivanshAstroVastu.exe') { $s.TargetPath = '%~dp0ShivanshAstroVastu.exe'; $s.WorkingDirectory = '%~dp0'; } else { $s.TargetPath = '%~dp0START_SHIVANSH_ASTRO_VASTU.bat'; $s.WorkingDirectory = '%~dp0'; }" ^
  "if (Test-Path '%~dp0app_icon.ico') { $s.IconLocation = '%~dp0app_icon.ico,0'; } elseif (Test-Path '%~dp0ShivanshAstroVastu\app_icon.ico') { $s.IconLocation = '%~dp0ShivanshAstroVastu\app_icon.ico,0'; }" ^
  "$s.Description = 'Shivansh Astro-Vastu Professional — Offline Vedic & Lal Kitab Software';" ^
  "$s.Save();" ^
  "Write-Host '   SUCCESS: Desktop Shortcut Created!' -ForegroundColor Green;"

echo.
echo Shortcut created on your Windows Desktop!
echo You can now double click 'Shivansh Astro-Vastu Professional' on your desktop to start.
echo.
pause
