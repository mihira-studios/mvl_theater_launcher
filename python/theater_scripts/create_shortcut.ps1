# Creates a Desktop shortcut that runs the `start_launcher.bat` in this folder
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Target = Join-Path $ScriptDir "start_launcher.bat"
if (-not (Test-Path $Target)) { Write-Host "Target not found: $Target"; exit 1 }

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "MVL Theatre.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.WorkingDirectory = Split-Path $Target -Parent
$Shortcut.Description = "MVL Theatre Launcher"

# Try project icon first; fall back to the batch file itself
$PossibleIcon = Resolve-Path (Join-Path $ScriptDir "..\launcher\ui\resources\icons\app_icon.ico") -ErrorAction SilentlyContinue
if ($PossibleIcon) {
	$Shortcut.IconLocation = "$PossibleIcon,0"
} else {
	$Shortcut.IconLocation = $Target
}

$Shortcut.Save()
Write-Host "Created shortcut: $ShortcutPath"
