# setup_c8run.ps1 - Automated Camunda 8 Run (c8run) Downloader & Configurator for Windows
[CmdletBinding()]
param (
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $TargetDir = $PSScriptRoot
    } else {
        $TargetDir = (Get-Location).Path
    }
}

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "       CAMUNDA 8 RUN (C8RUN) - AUTOMATIC WINDOWS INSTALLER & SETUP" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$destFolder = Join-Path $TargetDir "c8run"
$zipFile = Join-Path $TargetDir "c8run.zip"

try {
    Write-Host "[1/4] Checking latest Camunda 8 releases from GitHub API..." -ForegroundColor Yellow
    $apiUrl = "https://api.github.com/repos/camunda/camunda/releases/latest"
    $headers = @{ "User-Agent" = "PowerShell-CamundaInstaller" }
    
    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -TimeoutSec 30
    $asset = $release.assets | Where-Object { $_.name -like "camunda8-run*windows-x86_64.zip" -or ($_.name -like "*run*windows*.zip") } | Select-Object -First 1

    if (-not $asset) {
        throw "Could not find a Windows x86_64 zip asset in release $($release.tag_name)."
    }

    $downloadUrl = $asset.browser_download_url
    $fileSizeMB = [math]::Round($asset.size / 1MB, 2)
    Write-Host "[2/4] Found asset: $($asset.name) ($fileSizeMB MB)" -ForegroundColor Green
    Write-Host "      Download URL: $downloadUrl" -ForegroundColor Gray

    Write-Host "[3/4] Downloading Camunda 8 Run package (this may take a minute)..." -ForegroundColor Yellow
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("User-Agent", "PowerShell-CamundaInstaller")
    $webClient.DownloadFile($downloadUrl, $zipFile)
    Write-Host "      Download complete!" -ForegroundColor Green

    Write-Host "[4/4] Extracting archive into $destFolder..." -ForegroundColor Yellow
    if (Test-Path $destFolder) {
        Remove-Item -Path $destFolder -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
    Expand-Archive -Path $zipFile -DestinationPath $destFolder -Force

    # Clean up temporary zip
    if (Test-Path $zipFile) {
        Remove-Item -Path $zipFile -Force
    }

    # Locate c8run.exe (might be in subfolder after extraction)
    $foundExe = Get-ChildItem -Path $destFolder -Filter "c8run.exe" -Recurse | Select-Object -First 1
    if ($foundExe) {
        # Copy or link to root if desirable, or keep inside c8run/
        Write-Host ""
        Write-Host "SUCCESS: Camunda 8 Run is installed and ready at:" -ForegroundColor Green
        Write-Host "  $($foundExe.FullName)" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now start Camunda 8 by pressing 1 in run_c8_local.bat!" -ForegroundColor Cyan
    } else {
        Write-Warning "Archive extracted, but c8run.exe was not directly found. Please verify files inside $destFolder."
    }
}
catch {
    Write-Host ""
    Write-Host "Automatic download encountered an error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual Installation fallback instructions:" -ForegroundColor Yellow
    Write-Host " 1. Go to: https://github.com/camunda/camunda/releases/latest" -ForegroundColor White
    Write-Host " 2. Download: camunda8-run-*-windows-x86_64.zip" -ForegroundColor White
    Write-Host " 3. Extract the contents into a folder named 'c8run' inside this repository." -ForegroundColor White
    Write-Host " 4. Run run_c8_local.bat again." -ForegroundColor White
}
