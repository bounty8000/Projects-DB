@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: === CONFIG ===
set "Undo=0"
set "TranslationFile=__Translation.txt"
:: ==============

if "%Undo%"=="1" (
    echo [UNDO MODE] Restoring filenames using %TranslationFile%...
    if not exist "%TranslationFile%" (
        echo Error: Missing translation file: %TranslationFile%
        pause
        exit /b
    )
    for /f "skip=2 tokens=1* delims=|" %%A in (%TranslationFile%) do (
        echo Renaming "%%B" back to "%%A"
        ren "%%B" "%%A"
    )
    del /f /q "%TranslationFile%"
    echo Undo complete.
    pause
    exit /b
)

echo You are about to rename every file in the folder using last modified timestamp...
echo A translation file (%TranslationFile%) will be created to allow undo.
set /p Confirm=Type "OK" to continue: 
if /i not "%Confirm%"=="OK" (
    echo Aborting.
    exit /b
)

echo Original Name^|New Name > "%TranslationFile%"
echo ---------------------- >> "%TranslationFile%"

for %%F in (*.*) do (
    if /i not "%%~nxF"=="%~nx0" if /i not "%%~nxF"=="%TranslationFile%" (
        set "originalName=%%F"
        
        call :GetModifiedTimestamp "%%F" newname
        echo %%F^|!newname! >> "%TranslationFile%"
        ren "%%F" "!newname!"
    )
)

echo Rename complete.
pause
exit /b

:GetModifiedTimestamp
setlocal
set "filepath=%~1"

:: Get last modified date/time
for %%A in (%filepath%) do set "modified=%%~tA"

:: Split date and time
for /f "tokens=1,2" %%A in ("!modified!") do (
    set "date=%%A"
    set "time=%%B"
)

:: Parse MM/DD/YYYY
for /f "tokens=1-3 delims=/" %%A in ("!date!") do (
    set "mm=%%A"
    set "dd=%%B"
    set "yyyy=%%C"
)

:: Parse HH:MM
for /f "tokens=1,2 delims=:" %%A in ("!time!") do (
    set "hh=%%A"
    set "min=%%B"
)

:: Convert to 24-hr time if PM
echo !modified! | findstr /i "PM" >nul
if !errorlevel! == 0 (
    if "!hh!" NEQ "12" set /a hh=1!hh! - 100 + 12
) else (
    if "!hh!"=="12" set hh=00
)

:: Pad hour
if !hh! lss 10 set hh=0!hh!

:: Build name
set "ext=%~x1"
set "formatted=!yyyy!!mm!!dd!-!hh!!min!!ext!"
endlocal & set "%~2=%formatted%"
goto :eof
