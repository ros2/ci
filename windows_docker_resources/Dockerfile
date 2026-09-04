# escape=`
# This Dockerfile needs to be built from the parent directory (ros2/ci) so the build context
# includes the python scripts

# To find this value run in powershell:
# $(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').ReleaseId
ARG WINDOWS_RELEASE_ID=2009

# In order to ensure the image is correctly compatible with the host system a
# more precise version than the release id is required. To find this value run
# the following in powershell.
# $(Get-ItemProperty -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\Update\TargetingInfo\Installed\Server.OS.amd64' -Name Version).Version"
# Fall back to the Release ID
ARG WINDOWS_RELEASE_VERSION=$WINDOWS_RELEASE_ID

# Set ROS distro default value
ARG ROS_DISTRO=rolling

# Indicates that the windows image will be used as the base image. Must be same or older than host.
# --isolation=hyperv is needed for both build/run if the image id is older than the host id
# Use --isolation=process if you need to build in a mounted volume
FROM mcr.microsoft.com/windows/server:$WINDOWS_RELEASE_VERSION

# Get ROS distro value and set pixi.toml url
ARG ROS_DISTRO
ARG PIXI_TOML_URL=https://raw.githubusercontent.com/ros2/ros2/refs/heads/${ROS_DISTRO}/pixi.toml

# Enable long paths on folders
RUN powershell -noexit "New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force"

# Download and install all versions of MSVC we support.
# While this makes the images larger, it also means that we are certain to
# reuse the Docker layer cache, which should speed everything up.
# run_ros2_batch.py will source the appropriate one.

# Install MSVC 2022
RUN powershell -Command " `
    Invoke-WebRequest https://aka.ms/vs/17/release/vs_buildtools.exe -OutFile vs_buildtools_2022.exe; `
    Start-Process vs_buildtools_2022.exe -ArgumentList '--quiet --wait --norestart --add Microsoft.Component.MSBuild --add Microsoft.Net.Component.4.6.1.TargetingPack --add Microsoft.Net.Component.4.8.SDK --add Microsoft.VisualStudio.Component.CoreBuildTools --add Microsoft.VisualStudio.Component.Roslyn.Compiler --add Microsoft.VisualStudio.Component.TextTemplating --add Microsoft.VisualStudio.Component.VC.CLI.Support --add Microsoft.VisualStudio.Component.VC.CoreBuildTools --add Microsoft.VisualStudio.Component.VC.CoreIde --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --add Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Workload.VCTools' -Wait; `
    Remove-Item vs_buildtools_2022.exe -Force"

# Install pixi
## Fetch a pinned version
RUN powershell -Command " `
    Invoke-WebRequest https://github.com/prefix-dev/pixi/releases/download/v0.78.0/pixi-x86_64-pc-windows-msvc.zip -OutFile pixi.zip; `
    if ((Get-FileHash pixi.zip -Algorithm SHA256).Hash -ne '0655d6e11aa1dae56067f266d48b3c5815c02ed0031d5f3e96a1b0b81e1555b4') { exit 1 }; `
    Expand-Archive -Path pixi.zip -DestinationPath (Join-Path $Env:USERPROFILE '.pixi\bin') -Force; `
    $bindir = Join-Path $Env:USERPROFILE '.pixi\bin'; `
    $pathkey = (Get-Item -Path 'HKCU:').OpenSubKey('Environment', $true); `
    $oldpath = $pathkey.GetValue('PATH', $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames); `
    $pathkey.SetValue('PATH', \"$bindir;$oldpath\", [Microsoft.Win32.RegistryValueKind]::String); `
    Remove-Item pixi.zip -Force"

# Setup environment variables needed for Connext
ENV ROS_DISTRO=${ROS_DISTRO}
ENV RTI_LICENSE_FILE C:\connext\rti_license.dat

RUN --mount=type=bind,source=rticonnextdds-src,target=C:\TEMP\rticonnextdds-src `
    --mount=type=bind,source=rti_web_binaries_install_script.ps1,target=C:\TEMP\rti_web_binaries_install_script.ps1 `
    --mount=type=bind,source=rticonnextdds-license\rti_license.dat,target=C:\connext\rti_license.dat `
    powershell -ExecutionPolicy Bypass -Command "& C:\TEMP\rti_web_binaries_install_script.ps1 -RosDistro $env:ROS_DISTRO"

# Automatic invalidation once every day.
RUN echo "@today_str"

# Install dependencies via pixi
WORKDIR C:\pixi_ws
RUN powershell -Command "if (-not $env:PIXI_TOML_URL.StartsWith('https://')) { Write-Error 'PIXI_TOML_URL must use HTTPS protocol'; exit 1 }"
ADD ${PIXI_TOML_URL} pixi.toml
RUN powershell -Command "(Get-Item pixi.toml).LastWriteTime = Get-Date"

RUN --mount=type=cache,target=C:\pixi_cache pixi --color never --no-progress -q install

RUN pixi --color never --no-progress -q list

WORKDIR C:\ci
# Note that this *must* be in shell form, not exec form, so Docker on Windows appropriately substitutes %CI_ARGS%
CMD "pixi run --manifest-path C:\pixi_ws\pixi.toml --frozen python run_ros2_batch.py %CI_ARGS%"
