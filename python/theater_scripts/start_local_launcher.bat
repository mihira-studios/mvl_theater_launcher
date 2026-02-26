@echo off
REM Start the local launcher; MVL_DOMAIN is left unset so config defaults to localhost.

pushd "%~dp0..\"

REM clear any existing domain variable to use default
set "MVL_DOMAIN="

call "%~dp0start_launcher.bat"

popd
exit /b 0
