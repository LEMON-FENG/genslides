# genslides · render a .pptx to per-slide JPGs (LibreOffice -> PDF -> pdftoppm)
# Usage: pwsh scripts/render.ps1 <file.pptx> [outDir] [dpi]
param(
  [Parameter(Mandatory=$true)][string]$Pptx,
  [string]$OutDir,
  [int]$Dpi = 150
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$env  = Get-Content (Join-Path $here "..\config\env.json") -Raw | ConvertFrom-Json
$soffice = $env.soffice; $pdftoppm = $env.pdftoppm
if (-not (Test-Path $soffice)) { throw "soffice not found at $soffice (edit config/env.json)" }
$Pptx = (Resolve-Path $Pptx).Path
if (-not $OutDir) { $OutDir = Split-Path -Parent $Pptx }
New-Item -ItemType Directory -Force $OutDir | Out-Null
# isolated profile so it won't clash with an open LibreOffice
$prof = Join-Path $env:TEMP ("lo_genslides_" + [guid]::NewGuid().ToString("N").Substring(0,8))
& $soffice "-env:UserInstallation=file:///$($prof -replace '\\','/')" --headless --convert-to pdf --outdir $OutDir $Pptx 2>$null | Out-Null
$pdf = Join-Path $OutDir ([System.IO.Path]::GetFileNameWithoutExtension($Pptx) + ".pdf")
if (-not (Test-Path $pdf)) { throw "PDF not produced (is LibreOffice busy?)" }
$base = Join-Path $OutDir ([System.IO.Path]::GetFileNameWithoutExtension($Pptx))
& $pdftoppm -jpeg -r $Dpi $pdf $base
Get-ChildItem "$base*.jpg" | ForEach-Object { Write-Host $_.FullName }
