param([Parameter(Mandatory=$true)][string]$WorkDir)
$ErrorActionPreference = 'Stop'
$expected = Get-Content -LiteralPath (Join-Path $WorkDir 'expected.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$application = $null
$document = $null
$report = @()

function Read-Shapes($shapes, [string]$prefix) {
    foreach ($shape in $shapes) {
        $text = ''
        if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
            $text = $shape.TextFrame.TextRange.Text
        }
        [pscustomobject]@{Id=$shape.Id; Type=[int]$shape.Type; Text=$text}
        if ([int]$shape.Type -in @(11,13,28,29)) {
            $shape.Export(($prefix + '-image-' + $shape.Id + '.png'), 2)
        }
        if ([int]$shape.Type -eq 6) { Read-Shapes $shape.GroupItems $prefix }
    }
}

try {
    $application = New-Object -ComObject PowerPoint.Application
    foreach ($pass in @('input','saved')) {
        # These unique temporary paths never name an already-open user document.
        $document = $application.Presentations.Open((Join-Path $WorkDir ($pass+'.pptx')), -1, 0, 0)
        if ($document.Slides.Count -ne $expected.Count) { throw 'Slide count changed on open' }
        $slides = @()
        for ($index = 1; $index -le $document.Slides.Count; $index++) {
            $slide = $document.Slides.Item($index)
            $prefix = Join-Path $WorkDir ($pass+'-slide-'+$index)
            $objects = @(Read-Shapes $slide.Shapes $prefix)
            $pictures = @($objects | Where-Object { $_.Type -in @(11,13,28,29) }).Count
            $want = $expected[$index-1]
            if ($objects.Count -ne $want.shapes -or $pictures -ne $want.pictures) {
                throw ('Slide '+$index+': shape or picture count differs from source XML')
            }
            if ($pass -eq 'input') {
                foreach ($expectedText in $want.texts) {
                    $object = @($objects | Where-Object { $_.Id -eq $expectedText.id })
                    if ($object.Count -ne 1 -or [regex]::Replace([string]$object[0].Text, '\s+', ' ').Trim() -cne $expectedText.text) {
                        throw ('Slide '+$index+': text differs from source XML, shape '+$expectedText.id)
                    }
                }
            }
            $height = [int][Math]::Round(1600 * $document.PageSetup.SlideHeight / $document.PageSetup.SlideWidth)
            $slide.Export(($prefix+'.png'), 'PNG', 1600, $height)
            $slides += [pscustomobject]@{Index=$index; Shapes=$objects.Count; Pictures=$pictures; Objects=$objects; Image=($prefix+'.png')}
        }
        if ($pass -eq 'input') {
            $document.SaveCopyAs((Join-Path $WorkDir 'saved.pptx'), 24)
        }
        $report += [pscustomobject]@{Pass=$pass; Version=$application.Version; Slides=$slides}
        $document.Close()
        $document = $null
    }
    $first = $report[0].Slides | ForEach-Object { $_.Objects | Select-Object Type,Text } | ConvertTo-Json -Depth 6 -Compress
    $second = $report[1].Slides | ForEach-Object { $_.Objects | Select-Object Type,Text } | ConvertTo-Json -Depth 6 -Compress
    if ($first -ne $second) { throw 'Shape types or text changed after save/reopen' }
    ConvertTo-Json -InputObject $report -Depth 12 | Set-Content -LiteralPath (Join-Path $WorkDir 'powerpoint.json') -Encoding UTF8
    Write-Output 'POWERPOINT PASS'
} catch {
    Write-Output ('POWERPOINT FAIL: '+$_.Exception.Message)
    exit 1
} finally {
    if ($null -ne $document) { try { $document.Close() } catch {} }
    # Do not quit PowerPoint, alter global alert settings, or close user files.
    if ($null -ne $application) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($application) }
}
