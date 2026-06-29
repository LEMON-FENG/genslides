# genslides · screenshot an HTML mockup with Chrome headless (1280x720 @2x)
# Usage: pwsh scripts/shoot.ps1 <page.html> [out.png]
param(
  [Parameter(Mandatory=$true)][string]$Html,
  [string]$Out
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$env  = Get-Content (Join-Path $here "..\config\env.json") -Raw | ConvertFrom-Json
$chrome = $env.chrome
if (-not (Test-Path $chrome)) { throw "chrome not found at $chrome (edit config/env.json)" }
if (-not $Out) { $Out = [System.IO.Path]::ChangeExtension((Resolve-Path $Html), ".png") }
$uri = ([System.Uri](Resolve-Path $Html).Path).AbsoluteUri
& $chrome --headless --disable-gpu --force-device-scale-factor=2 --window-size=1280,720 --hide-scrollbars --default-background-color=00000000 "--screenshot=$Out" $uri 2>$null | Out-Null
if (Test-Path $Out) { Write-Host "shot -> $Out" } else { throw "screenshot failed" }
