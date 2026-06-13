$installBin = Join-Path $HOME "rayskills\bin"
$installApp = Join-Path $installBin "rayskills.exe"

Remove-Item -Force -ErrorAction SilentlyContinue $installApp

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = @($userPath -split ";" | Where-Object { $_ -and $_ -ne $installBin })
[Environment]::SetEnvironmentVariable("Path", ($entries -join ";"), "User")

Write-Host "Uninstalled rayskills. Open a new terminal to refresh PATH."
