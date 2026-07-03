# genslides · thin wrapper — canonical cross-platform implementation is scripts/shoot.py
# Usage: pwsh scripts/shoot.ps1 <page.html> [out.png]
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $here "shoot.py") @args
exit $LASTEXITCODE
