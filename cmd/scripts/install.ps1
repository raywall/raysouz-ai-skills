param(
    [Parameter(Mandatory = $true)]
    [string]$Source
)

$installBin = Join-Path $HOME "rayskills\bin"
$installApp = Join-Path $installBin "rayskills.exe"

New-Item -ItemType Directory -Force -Path $installBin | Out-Null
Copy-Item -Force $Source $installApp

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = @($userPath -split ";" | Where-Object { $_ })
if ($entries -notcontains $installBin) {
    [Environment]::SetEnvironmentVariable("Path", (($entries + $installBin) -join ";"), "User")
}

Write-Host "Installed rayskills at $installApp"
Write-Host "Open a new terminal to use rayskills from anywhere."
