# genslides · self-test: runs the whole chain on the template and reports PASS/FAIL.
# Verifies the skill is wired up correctly on THIS machine (paths, node modules, soffice, chrome, validate).
# Usage: pwsh scripts/selftest.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$env:PYTHONIOENCODING = "utf-8"
$envc = Get-Content (Join-Path $root "config\env.json") -Raw | ConvertFrom-Json
$env:NODE_PATH = $envc.nodeModules

$work = Join-Path $env:TEMP ("genslides_selftest_" + [guid]::NewGuid().ToString("N").Substring(0,6))
New-Item -ItemType Directory -Force $work | Out-Null
$pptx = Join-Path $work "selftest.pptx"
$ok = $true
function Step($name, $cond, $detail) {
  $mark = if ($cond) { "PASS" } else { $script:ok = $false; "FAIL" }
  "{0,-26} [{1}] {2}" -f $name, $mark, $detail
}

# 1 generate
$g = & node (Join-Path $root "templates\gen_template.js") $pptx 2>&1 | Out-String
Step "1 generate (gen_template)" (Test-Path $pptx) ($g.Trim() -split "`n" | Select-Object -Last 1)

# 2 postprocess
$pp = & python (Join-Path $here "postprocess.py") $pptx 2>&1 | Out-String
Step "2 postprocess" ($pp -match "DONE") (($pp -split "`n" | Where-Object {$_ -match "gradients|fonts"}) -join " | ")

# 3 validate (the real gate) — use configured validator, else bundled self-contained check_pptx.py
$validator = $envc.validatePy
if (-not $validator -or -not (Test-Path $validator)) { $validator = Join-Path $here "check_pptx.py" }
$v = & python $validator $pptx 2>&1 | Out-String
Step "3 validate (gate)" ($v -match "All validations PASSED") ("via " + (Split-Path $validator -Leaf))

# 4 render pptx -> jpg
$img = Join-Path $work "selftest-1.jpg"
& pwsh -NoProfile -File (Join-Path $here "render.ps1") $pptx $work 150 *> $null
Step "4 render (LibreOffice)" (Test-Path $img) $img

# 5 shoot the HTML mockup
$png = Join-Path $work "viz.png"
& pwsh -NoProfile -File (Join-Path $here "shoot.ps1") (Join-Path $root "templates\visualizer.html") $png *> $null
Step "5 shoot (Chrome headless)" (Test-Path $png) $png

Write-Host ""
if ($ok) {
  Write-Host "RESULT: ALL PASS  ✓   eyeball -> $img  and  $png" -ForegroundColor Green
} else {
  Write-Host "RESULT: SOME FAIL ✗   check config/env.json paths" -ForegroundColor Red
}
Remove-Item $pptx -ErrorAction SilentlyContinue
