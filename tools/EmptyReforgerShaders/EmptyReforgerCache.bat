@echo off
setlocal
title Empty NVIDIA DXCache (ARMA: Reforger workaround)
set "FOLDER=%LOCALAPPDATA%\NVIDIA\DXCache"
if not exist "%FOLDER%" (
  echo DXCache folder not found: "%FOLDER%"
  echo Nothing to do.
  goto :EOF
)
echo Emptying: "%FOLDER%"
del /f /q "%FOLDER%\*.*" 2>nul
for /d %%p in ("%FOLDER%\*") do rmdir /s /q "%%p" 2>nul
echo Done. Cache cleared.
timeout /t 2 >nul
endlocal