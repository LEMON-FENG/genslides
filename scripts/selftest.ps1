# genslides · thin wrapper — canonical cross-platform implementation is scripts/selftest.py
# Usage: pwsh scripts/selftest.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $here "selftest.py") @args
exit $LASTEXITCODE
