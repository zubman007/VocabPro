[CmdletBinding()]
param(
    [ValidateSet('Quick','Full')][string]$Mode = 'Full',
    [switch]$NoOpen,
    [switch]$RefreshTools,
    [switch]$FailOnFindings,
    [string]$Python = '',
    [ValidateRange(10,3600)][int]$TestTimeout = 180
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not $Python) {
    $candidate = Join-Path $root '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $candidate) { $Python = $candidate }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
$toolRoot = Join-Path $root '.quality-venv'
$toolPython = Join-Path $toolRoot 'Scripts\python.exe'
$requirements = Join-Path $root 'tools\quality\requirements.txt'
$fingerprint = (Get-FileHash -LiteralPath $requirements -Algorithm SHA256).Hash
$marker = Join-Path $toolRoot 'quality-tools.sha256'
if (-not (Test-Path -LiteralPath $toolPython)) {
    & $Python -B -m venv $toolRoot
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create the isolated quality environment.' }
}
if ($RefreshTools -or -not (Test-Path -LiteralPath $marker) -or (Get-Content -LiteralPath $marker -Raw).Trim() -ne $fingerprint) {
    & $toolPython -B -m pip install --disable-pip-version-check -r $requirements
    if ($LASTEXITCODE -eq 0) { Set-Content -LiteralPath $marker -Value $fingerprint -Encoding ASCII }
    else { Write-Warning 'Tool installation failed. Available checks will still run; missing tools will be reported.' }
}
$arguments = @('-X','utf8','-B',(Join-Path $root 'tools\quality\run.py'),
    '--root',$root,'--python',$Python,'--tools-python',$toolPython,'--mode',$Mode,'--timeout',"$TestTimeout")
if ($NoOpen) { $arguments += '--no-open' }
if ($FailOnFindings) { $arguments += '--fail-on-findings' }
& $Python @arguments
exit $LASTEXITCODE
