# genslides · thin wrapper — canonical cross-platform implementation is scripts/setup.py
# Run once after cloning/installing on a new machine:  pwsh -NoProfile -File scripts/setup.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $here "setup.py") @args
exit $LASTEXITCODE
