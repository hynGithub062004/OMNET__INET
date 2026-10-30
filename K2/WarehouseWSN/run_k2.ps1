param(
    [Parameter(Mandatory = $true)][string]$OmnetRoot,
    [Parameter(Mandatory = $true)][string]$InetRoot,
    [ValidateSet('K2_Final', 'K2_Visual')][string]$Configuration = 'K2_Final',
    [string]$Runs = '0..4',
    [ValidateSet('Cmdenv', 'Qtenv')][string]$Ui = 'Cmdenv'
)
$ErrorActionPreference = 'Stop'
$runner = Join-Path $OmnetRoot 'bin\opp_run.exe'
if (-not (Test-Path -LiteralPath $runner)) { throw "Missing $runner" }
if (-not (Test-Path -LiteralPath (Join-Path $InetRoot 'src\libINET.dll'))) {
    throw 'Build INET 4.7.0 in release mode first (src/libINET.dll is required).'
}
$exclusionFile = Join-Path $InetRoot '.nedexclusions'
$exclusions = if (Test-Path -LiteralPath $exclusionFile) {
    (Get-Content -LiteralPath $exclusionFile | Where-Object { $_.Trim() -and -not $_.StartsWith('#') }) -join ';'
} else { '' }
$previousPath = $env:PATH
try {
    $env:PATH = "$OmnetRoot\bin;$OmnetRoot\tools\win32.x86_64\clang64\bin;$OmnetRoot\tools\win32.x86_64\usr\bin;$previousPath"
    Push-Location (Join-Path $PSScriptRoot 'simulations')
    try {
        $options = @('-u', $Ui, '-n', ".;$InetRoot/src", '-l', "$InetRoot/src/INET", '-c', $Configuration)
        if ($exclusions) { $options += @('-x', $exclusions) }
        if ($Configuration -eq 'K2_Visual') { $Runs = '0' }
        $options += @('-r', $Runs)
        if ($Ui -eq 'Cmdenv') {
            $options += @('--cmdenv-express-mode=true', '--cmdenv-event-banners=false', '--cmdenv-log-level=warn')
        }
        & $runner @options
        if ($LASTEXITCODE -ne 0) { throw "OMNeT++ failed with exit code $LASTEXITCODE" }
    } finally { Pop-Location }
} finally { $env:PATH = $previousPath }
