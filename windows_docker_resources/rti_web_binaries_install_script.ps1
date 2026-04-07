param(
    [Parameter(Mandatory = $true)]
    [string]$RosDistro
)

$ErrorActionPreference = "Stop"

function Invoke-CmdChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    Write-Host $Description
    cmd /c $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE. Command: $Command"
    }
}

Write-Host "Installing Connext for ROS distro: $RosDistro"

$connextRoot = "C:\connext"
$tempRoot = "C:\TEMP\rticonnextdds-src"
$licenseFile = "C:\connext\rti_license.dat"

if ($RosDistro -eq "kilted") {
    $ConnextVersion = "7.3.0"
    $OpenSslVersion = "3.0.12"
    $ConnextDir = "C:\connext\rti_connext_dds-7.3.0"
    $OpenSslBin = "C:\connext\openssl-3.0.12\x64Win64VS2017\bin"
    $OpenSslLib = "C:\connext\openssl-3.0.12\x64Win64VS2017\lib"

    $HostInstaller = "rti_connext_dds-7.3.0-pro-host-x64Win64.exe"
    $TargetInstaller = "rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg"
    $OpenSslHostInstaller = "openssl-3.0.12-7.3.0-host-x64Win64.rtipkg"
    $OpenSslTargetInstaller = "openssl-3.0.12-7.3.0-target-x64Win64VS2017.rtipkg"
    $SecurityHostInstaller = "rti_security_plugins-7.3.0-host-openssl-3.0-x64Win64.rtipkg"
    $SecurityTargetInstaller = "rti_security_plugins-7.3.0-target-openssl-3.0-x64Win64VS2017.rtipkg"
}
else {
    $ConnextVersion = "7.7.0"
    $OpenSslVersion = "3.5.5"
    $ConnextDir = "C:\connext\rti_connext_dds-7.7.0"
    $OpenSslBin = "C:\connext\openssl-3.5.5\x64Win64VS2017\bin"
    $OpenSslLib = "C:\connext\openssl-3.5.5\x64Win64VS2017\lib"

    $HostInstaller = "rti_connext_dds-7.7.0-pro-host-x64Win64.exe"
    $TargetInstaller = "rti_connext_dds-7.7.0-pro-target-x64Win64VS2017.rtipkg"
    $OpenSslHostInstaller = "openssl-3.5.5-7.7.0-host-x64Win64.rtipkg"
    $OpenSslTargetInstaller = "openssl-3.5.5-7.7.0-target-x64Win64VS2017.rtipkg"
    $SecurityHostInstaller = "rti_security_plugins-7.7.0-host-openssl-3.5-x64Win64.rtipkg"
    $SecurityTargetInstaller = "rti_security_plugins-7.7.0-target-openssl-3.5-x64Win64VS2017.rtipkg"
}

Write-Host "Selected Connext version: $ConnextVersion"
Write-Host "Selected OpenSSL version: $OpenSslVersion"

[Environment]::SetEnvironmentVariable("RTI_LICENSE_FILE", $licenseFile, "Machine")
[Environment]::SetEnvironmentVariable("CONNEXTDDS_DIR", $ConnextDir, "Machine")
[Environment]::SetEnvironmentVariable("RTI_OPENSSL_BIN", $OpenSslBin, "Machine")
[Environment]::SetEnvironmentVariable("RTI_OPENSSL_LIB", $OpenSslLib, "Machine")

$env:RTI_LICENSE_FILE = $licenseFile
$env:CONNEXTDDS_DIR = $ConnextDir
$env:RTI_OPENSSL_BIN = $OpenSslBin
$env:RTI_OPENSSL_LIB = $OpenSslLib

if (-not (Test-Path $connextRoot)) {
    New-Item -ItemType Directory -Path $connextRoot | Out-Null
}

if (-not (Test-Path "C:\TEMP")) {
    New-Item -ItemType Directory -Path "C:\TEMP" | Out-Null
}

$hostInstallerBase = Join-Path $tempRoot $HostInstaller
$targetInstallerBase = Join-Path $tempRoot $TargetInstaller

Write-Host "Reassembling split installer files..."
Invoke-CmdChecked -Description "Reassembling split Connext host installer files..." -Command "copy /b ${hostInstallerBase}.??? ${hostInstallerBase}"
Invoke-CmdChecked -Description "Reassembling split Connext target installer files..." -Command "copy /b ${targetInstallerBase}.??? ${targetInstallerBase}"

Write-Host "Installing Connext host package..."
$hostInstallerProcess = Start-Process -FilePath $hostInstallerBase `
    -ArgumentList "--mode unattended --unattendedmodeui minimalWithDialogs --prefix $connextRoot" `
    -Wait `
    -NoNewWindow `
    -PassThru

if ($hostInstallerProcess.ExitCode -ne 0) {
    throw "Installing Connext host package failed with exit code $($hostInstallerProcess.ExitCode)."
}

$rtipkginstall = Join-Path $ConnextDir "bin\rtipkginstall.bat"

Invoke-CmdChecked -Description "Installing OpenSSL host package..." -Command """$rtipkginstall"" -u ""$(Join-Path $tempRoot $OpenSslHostInstaller)"""
Invoke-CmdChecked -Description "Installing OpenSSL target package..." -Command """$rtipkginstall"" -u ""$(Join-Path $tempRoot $OpenSslTargetInstaller)"""
Invoke-CmdChecked -Description "Installing Connext target package..." -Command """$rtipkginstall"" -u ""$(Join-Path $tempRoot $TargetInstaller)"""
Invoke-CmdChecked -Description "Installing Security Plugins host package..." -Command """$rtipkginstall"" -u ""$(Join-Path $tempRoot $SecurityHostInstaller)"""
Invoke-CmdChecked -Description "Installing Security Plugins target package..." -Command """$rtipkginstall"" -u ""$(Join-Path $tempRoot $SecurityTargetInstaller)"""

Write-Host "Connext installation completed successfully."
Write-Host "CONNEXTDDS_DIR=$ConnextDir"
