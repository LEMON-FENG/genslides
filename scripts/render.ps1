# genslides · thin wrapper — canonical cross-platform implementation is scripts/render.py
# Usage: pwsh scripts/render.ps1 <file.pptx> [outDir] [dpi]
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $here "render.py") @args
exit $LASTEXITCODE
