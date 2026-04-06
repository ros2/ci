param(
    [Parameter(Mandatory = $true)]
    [string]$RosDistro
)

$ErrorActionPreference = "Stop"

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
    $SecurityHostInstaller = "rti_security_plugins-7.3.0-host-x64Win64.rtipkg"
    $SecurityTargetInstaller = "rti_security_plugins-7.3.0-target-x64Win64VS2017.rtipkg"
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
cmd /c "copy /b ${hostInstallerBase}.??? ${hostInstallerBase}"
cmd /c "copy /b ${targetInstallerBase}.??? ${targetInstallerBase}"

Write-Host "Installing Connext host package..."
Start-Process -FilePath $hostInstallerBase `
    -ArgumentList "--mode unattended --unattendedmodeui minimalWithDialogs --prefix $connextRoot" `
    -Wait `
    -NoNewWindow

$rtipkginstall = Join-Path $ConnextDir "bin\rtipkginstall.bat"

Write-Host "Installing OpenSSL host package..."
cmd /c """$rtipkginstall"" -u ""$(Join-Path $tempRoot $OpenSslHostInstaller)"""

Write-Host "Installing OpenSSL target package..."
cmd /c """$rtipkginstall"" -u ""$(Join-Path $tempRoot $OpenSslTargetInstaller)"""

Write-Host "Installing Connext target package..."
cmd /c """$rtipkginstall"" -u ""$(Join-Path $tempRoot $TargetInstaller)"""

Write-Host "Installing Security Plugins host package..."
cmd /c """$rtipkginstall"" -u ""$(Join-Path $tempRoot $SecurityHostInstaller)"""

Write-Host "Installing Security Plugins target package..."
cmd /c """$rtipkginstall"" -u ""$(Join-Path $tempRoot $SecurityTargetInstaller)"""

Write-Host "Connext installation completed successfully."
Write-Host "CONNEXTDDS_DIR=$ConnextDir"
