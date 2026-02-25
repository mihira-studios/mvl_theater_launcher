@echo off
REM Start the launcher by invoking Python directly so no PowerShell window appears.
pushd "%~dp0..\"

REM prefer venv python.exe then venv pythonw, else system python/pythonw
if exist "venv\Scripts\python.exe" (
	set "PY=%CD%\venv\Scripts\python.exe"
) else if exist "venv\Scripts\pythonw.exe" (
	set "PY=%CD%\venv\Scripts\pythonw.exe"
) else (
	where python >nul 2>&1
	if %ERRORLEVEL%==0 for /f "delims=" %%P in ('where python') do set "PY=%%P" & goto :gotpy
	where pythonw >nul 2>&1
	if %ERRORLEVEL%==0 for /f "delims=" %%P in ('where pythonw') do set "PY=%%P" & goto :gotpy
)

:gotpy
if not defined PY (
	echo Python not found. Install Python or create a virtualenv at %CD%\venv
	pause
	popd
	exit /b 1
)

REM Start the python process (this will create its own console window)
start "MVL Theatre" "%PY%" "%CD%\main.py"

popd
exit /b 0
