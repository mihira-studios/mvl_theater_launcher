@echo off
setlocal enabledelayedexpansion
title MVL Theater Launcher — EXE Builder

echo.
echo =========================================
echo   MVL Theater Launcher — EXE Builder
echo =========================================
echo.

REM ── Locate Python ────────────────────────────────────────────────────────────
if exist "venv\Scripts\python.exe" (
    set "PY=venv\Scripts\python.exe"
    echo [OK] Using venv Python
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python not found. Run start_vm_launcher.bat first.
        pause
        exit /b 1
    )
    set "PY=python"
    echo [OK] Using system Python
)

REM ── Check / Install PyInstaller ───────────────────────────────────────────────
echo.
echo Checking for PyInstaller...
"%PY%" -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    "%PY%" -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
    echo [OK] PyInstaller installed.
) else (
    echo [OK] PyInstaller already installed.
)

REM ── Build from spec file ──────────────────────────────────────────────────────
echo.
echo Building EXE from spec file, please wait...
echo.

"%PY%" -m PyInstaller ^
    --distpath "release\dist" ^
    --workpath "release\build" ^
    MVL_Theater_Launcher.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed. Check the logs above.
    pause
    exit /b 1
)

REM ── Done ─────────────────────────────────────────────────────────────────────
echo.
echo =========================================
echo   Build complete!
echo   Output: release\dist\MVL_Theater_Launcher.exe
echo   Hand testers the entire release\dist\ folder.
echo =========================================
echo.
pause
exit /b 0