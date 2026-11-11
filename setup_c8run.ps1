# setup_c8run.ps1 - Automated Camunda 8 Run (c8run) Downloader & Configurator for Windows
[CmdletBinding()]
param (
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
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

# Known direct stable release fallback URL (bypasses GitHub API rate limits)
$fallbackUrl = "https://github.com/camunda/camunda/releases/download/8.10.9/camunda8-run-8.10.9-windows-x86_64.zip"
$downloadUrl = $fallbackUrl
$versionName = "8.10.9"

try {
    Write-Host "[1/4] Resolving Camunda 8 Run Windows distribution..." -ForegroundColor Yellow
    try {
        $apiUrl = "https://api.github.com/repos/camunda/camunda/releases/latest"
        $headers = @{ "User-Agent" = "PowerShell-CamundaInstaller" }
        $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $asset = $release.assets | Where-Object { $_.name -like "camunda8-run*windows-x86_64.zip" } | Select-Object -First 1
        if ($asset) {
            $downloadUrl = $asset.browser_download_url
            $versionName = $release.tag_name
            Write-Host "      Found latest release: $versionName" -ForegroundColor Green
        }
    } catch {
        Write-Host "      GitHub API rate-limited or unavailable; using direct release: $versionName" -ForegroundColor Cyan
    }

    Write-Host "[2/4] Target asset: camunda8-run-$versionName-windows-x86_64.zip" -ForegroundColor Green
    Write-Host "      Source: $downloadUrl" -ForegroundColor Gray

    # Clean existing partial files
    if (Test-Path $zipFile) {
        Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $destFolder) {
        Remove-Item -Path $destFolder -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $destFolder -Force | Out-Null

    Write-Host "[3/4] Downloading Camunda 8 Run package (~885 MB)..." -ForegroundColor Yellow
    Write-Host "      (Please wait a moment while the package downloads)" -ForegroundColor Gray

    $hasCurl = (Get-Command curl.exe -ErrorAction SilentlyContinue)
    if ($hasCurl) {
        Write-Host "      Downloading via curl.exe..." -ForegroundColor Cyan
        & curl.exe -# -fSL "$downloadUrl" -o "$zipFile"
        if ($LASTEXITCODE -ne 0) {
            throw "curl.exe exited with code $LASTEXITCODE"
        }
    } else {
        Write-Host "      Downloading via WebClient..." -ForegroundColor Cyan
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "PowerShell-CamundaInstaller")
        $webClient.DownloadFile($downloadUrl, $zipFile)
    }

    if (-not (Test-Path $zipFile) -or (Get-Item $zipFile).Length -lt 10000000) {
        throw "Downloaded package is missing or smaller than 10MB."
    }

    $downloadedMB = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
    Write-Host "      Downloaded $downloadedMB MB successfully!" -ForegroundColor Green

    Write-Host "[4/4] Extracting package into $destFolder..." -ForegroundColor Yellow

    # Extract using Expand-Archive with SilentlyContinue
    $extracted = $false
    try {
        Write-Host "      Extracting files (this takes approx. 1-2 minutes)..." -ForegroundColor Cyan
        Expand-Archive -Path "$zipFile" -DestinationPath "$destFolder" -Force
        $extracted = $true
    } catch {
        Write-Warning "Expand-Archive failed: $($_.Exception.Message). Trying tar.exe..."
        & tar.exe -xf "$zipFile" -C "$destFolder"
        if ($LASTEXITCODE -eq 0) { $extracted = $true }
    }

    # Locate c8run.exe
    $foundExe = Get-ChildItem -Path $destFolder -Filter "c8run.exe" -Recurse | Select-Object -First 1

    if ($foundExe) {
        # Clean up temporary zip
        Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue

        Write-Host ""
        Write-Host "===============================================================================" -ForegroundColor Green
        Write-Host " SUCCESS: Camunda 8 Run is installed and ready at:" -ForegroundColor Green
        Write-Host "   $($foundExe.FullName)" -ForegroundColor White
        Write-Host "===============================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host " You can now start Camunda 8 locally by pressing [1] in run_c8_local.bat!" -ForegroundColor Cyan
    } else {
        Write-Warning "Archive extracted, but c8run.exe was not found. Check contents of $destFolder."
    }
}
catch {
    Write-Host ""
    Write-Host "Automatic setup encountered an error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual Installation fallback instructions:" -ForegroundColor Yellow
    Write-Host " 1. Go to: $fallbackUrl" -ForegroundColor White
    Write-Host " 2. Save the zip file to: $TargetDir\c8run.zip" -ForegroundColor White
    Write-Host " 3. Extract the contents into a folder named 'c8run' inside this repository." -ForegroundColor White
    Write-Host " 4. Run run_c8_local.bat again." -ForegroundColor White
}
