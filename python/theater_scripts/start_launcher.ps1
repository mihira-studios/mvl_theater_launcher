# PowerShell starter for MVL launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LauncherDir = Resolve-Path (Join-Path $ScriptDir "..") | Select-Object -ExpandProperty Path

# Paths inside a typical venv (if present)
$venvPython = Join-Path $LauncherDir "venv\Scripts\python.exe"
$venvPythonw = Join-Path $LauncherDir "venv\Scripts\pythonw.exe"

# Prefer console python so startup errors are visible; fall back to pythonw
if (Test-Path $venvPython) { $python = $venvPython }
elseif (Test-Path $venvPythonw) { $python = $venvPythonw }
else {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) { $python = $cmd.Source }
  else {
    $cmd2 = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($cmd2) { $python = $cmd2.Source }
  }
}

if (-not $python -or -not (Test-Path $python)) {
  Write-Host "Python not found. Install Python or create a virtualenv at $LauncherDir\venv"
  Read-Host -Prompt "Press Enter to exit"
  exit 1
}

# Launch with console python when available so exceptions show in this window.
if ($python -match "python.exe$") {
  Write-Host "Launching launcher with console python (errors will appear here)..."
  & $python (Join-Path $LauncherDir "main.py")
} else {
  # pythonw: run detached and hidden
  Start-Process -FilePath $python -ArgumentList (Join-Path $LauncherDir "main.py") -WorkingDirectory $LauncherDir -WindowStyle Hidden
}
