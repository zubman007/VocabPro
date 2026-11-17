[CmdletBinding()]
param(
    [ValidateSet('Quick','Full')][string]$QualityMode = 'Quick',
    [switch]$Rollback
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$tools = Join-Path $root '.build-tools'
$python = Join-Path $root '.build-venv\Scripts\python.exe'
$basePython = Join-Path $tools 'Python313\python.exe'
function Invoke-Checked([string]$Program,[string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Program" }
}
function Get-VerifiedInstaller([string]$Uri,[string]$Name,[string]$Publisher) {
    $folder = Join-Path $tools 'downloads'
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    $installer = Join-Path $folder $Name
    if (-not (Test-Path -LiteralPath $installer)) {
        Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $installer
    }
    $signature = Get-AuthenticodeSignature -LiteralPath $installer
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch $Publisher) {
        throw "Installer signature verification failed: $Name"
    }
    return $installer
}
Push-Location -LiteralPath $root
try {
    if (-not (Test-Path -LiteralPath $basePython)) {
        Write-Host 'Installing isolated build Python (no PATH changes).'
        $installer = Get-VerifiedInstaller 'https://www.python.org/ftp/python/3.13.14/python-3.13.14-amd64.exe' 'python-3.13.14-amd64.exe' 'Python Software Foundation'
        $target = Split-Path -Parent $basePython
        $install = Start-Process -FilePath $installer -ArgumentList @('/quiet','InstallAllUsers=0',('TargetDir="'+$target+'"'),'Include_launcher=0','PrependPath=0','Include_test=0','Shortcuts=0') -WindowStyle Hidden -Wait -PassThru
        if ($install.ExitCode -ne 0) { throw "Build Python installation failed: $($install.ExitCode)" }
    }
    if (-not (Test-Path -LiteralPath $python)) { Invoke-Checked $basePython @('-m','venv',(Join-Path $root '.build-venv')) }
    $requirements = Join-Path $root 'tools\release-requirements.txt'
    $lock = Join-Path $root 'requirements.lock.txt'
    $fingerprint = (Get-FileHash $requirements -Algorithm SHA256).Hash+(Get-FileHash $lock -Algorithm SHA256).Hash
    $marker = Join-Path $root '.build-venv\release-tools.sha256'
    if (-not (Test-Path -LiteralPath $marker) -or (Get-Content $marker -Raw).Trim() -ne $fingerprint) {
        Invoke-Checked $python @('-m','pip','install','--disable-pip-version-check','-r',$lock,'-r',$requirements)
        Set-Content -LiteralPath $marker -Value $fingerprint -Encoding ASCII
    }
    Invoke-Checked $python @('-B','-m','unittest','tools.test_release')
    $arguments = @('-X','utf8','-B',(Join-Path $root 'tools\release.py'),'--python',$python,'--quality-mode',$QualityMode)
    if ($Rollback) { $arguments += '--rollback' }
    Invoke-Checked $python $arguments
    exit 0
} catch {
    Write-Error "Release stopped. Previous distribution and user data were preserved. $($_.Exception.Message)" -ErrorAction Continue
    exit 1
} finally {
    Pop-Location
}
