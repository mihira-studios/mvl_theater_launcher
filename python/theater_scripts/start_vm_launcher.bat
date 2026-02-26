@echo off
REM Start the VM launcher by setting MVL_DOMAIN and invoking the standard launcher script.
REM Adjust the IP below to the desired VM address if necessary.

pushd "%~dp0..\"

REM configure domain for VM
set "MVL_DOMAIN=10.100.0.85"

REM delegate to the common launcher logic
call "%~dp0start_launcher.bat"

popd
exit /b 0
