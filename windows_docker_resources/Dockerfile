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

# Indicates that the windows image will be used as the base image. Must be same or older than host.
# --isolation=hyperv is needed for both build/run if the image id is older than the host id
# Use --isolation=process if you need to build in a mounted volume
FROM mcr.microsoft.com/windows/server:$WINDOWS_RELEASE_VERSION

# Enable long paths on folders
RUN powershell -noexit "New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force"

# Download and install all versions of MSVC we support.
# While this makes the images larger, it also means that we are certain to
# reuse the Docker layer cache, which should speed everything up.
# run_ros2_batch.py will source the appropriate one.

# Install MSVC 2019
RUN powershell -noexit irm https://aka.ms/vs/16/release/vs_buildtools.exe -OutFile vs_buildtools_2019.exe
RUN vs_buildtools_2019.exe --quiet --wait --norestart --add Microsoft.Component.MSBuild --add Microsoft.Net.Component.4.6.1.TargetingPack --add Microsoft.Net.Component.4.8.SDK --add Microsoft.VisualStudio.Component.CoreBuildTools --add Microsoft.VisualStudio.Component.Roslyn.Compiler --add Microsoft.VisualStudio.Component.TextTemplating --add Microsoft.VisualStudio.Component.VC.CLI.Support --add Microsoft.VisualStudio.Component.VC.CoreBuildTools --add Microsoft.VisualStudio.Component.VC.CoreIde --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --add Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Workload.VCTools

# Install MSVC 2022
RUN powershell -noexit irm https://aka.ms/vs/17/release/vs_buildtools.exe -OutFile vs_buildtools_2022.exe
RUN vs_buildtools_2022.exe --quiet --wait --norestart --add Microsoft.Component.MSBuild --add Microsoft.Net.Component.4.6.1.TargetingPack --add Microsoft.Net.Component.4.8.SDK --add Microsoft.VisualStudio.Component.CoreBuildTools --add Microsoft.VisualStudio.Component.Roslyn.Compiler --add Microsoft.VisualStudio.Component.TextTemplating --add Microsoft.VisualStudio.Component.VC.CLI.Support --add Microsoft.VisualStudio.Component.VC.CoreBuildTools --add Microsoft.VisualStudio.Component.VC.CoreIde --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --add Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Workload.VCTools

# Install pixi
## Fetch a pinned version
RUN powershell -noexit irm https://github.com/prefix-dev/pixi/releases/download/v0.41.0/pixi-x86_64-pc-windows-msvc.zip -OutFile pixi-x86_64-pc-windows-msvc.zip
## Check that the checksum matches
RUN powershell -noexit "if ((get-filehash pixi-x86_64-pc-windows-msvc.zip -Algorithm SHA256).hash -ne '16b1b83f2d6f04a990ef7c6eea2bb45d2e846d122be312ca3f5f1b14be7cdc6d') { exit 1 }"
## Extract the binary
RUN powershell -noexit Expand-Archive -Path pixi-x86_64-pc-windows-msvc.zip -DestinationPath (Join-Path $Env:USERPROFILE\.pixi 'bin') -Force
## Add the binary to the PATH
RUN powershell -noexit "$bindir = Join-Path $Env:USERPROFILE\.pixi 'bin' ; $pathkey = (Get-Item -Path 'HKCU:').OpenSubKey('Environment', $true) ; $oldpath = $pathkey.GetValue('PATH', $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames) ; $pathkey.SetValue('PATH', \"$bindir;$oldpath\", [Microsoft.Win32.RegistryValueKind]::String)"

# Automatic invalidation once every day.
RUN echo "@today_str"

# Install dependencies via pixi
ARG ROS_DISTRO=rolling
WORKDIR C:\pixi_ws
RUN powershell -noexit irm https://raw.githubusercontent.com/ros2/ros2/refs/heads/claraberendsen/msvc2022-work/pixi.toml -OutFile pixi.toml
RUN pixi --color never --no-progress -q install
RUN pixi --color never --no-progress -q list

# Ensure required colcon-ros-domain-id-coordinator version
RUN pixi --color never --no-progress -q run "pip install 'colcon-ros-domain-id-coordinator >= 0.2.3'"

# Setup environment variables needed for Connext
ENV RTI_LICENSE_FILE C:\connext\rti_license.dat
ENV CONNEXTDDS_DIR C:\connext\rti_connext_dds-7.3.0
ENV RTI_OPENSSL_BIN C:\connext\openssl-3.0.12\x64Win64VS2017\bin
ENV RTI_OPENSSL_LIB C:\connext\openssl-3.0.12\x64Win64VS2017\lib

# Copy over necessary Connext files into container
RUN IF NOT EXIST "C:\TEMP" mkdir C:\TEMP
COPY rticonnextdds-src\ C:\TEMP\rticonnextdds-src
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-host-x64Win64.exe.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-host-x64Win64.exe
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg
COPY rticonnextdds-license\rti_license.dat $RTI_LICENSE_FILE

# Install Connext
RUN C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-host-x64Win64.exe --mode unattended --unattendedmodeui minimalWithDialogs --prefix C:\connext
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-host-x64Win64.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-target-x64Win64VS2017.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-host-x64Win64.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-target-x64Win64VS2017.rtipkg

WORKDIR C:\ci
# Note that this *must* be in shell form, not exec form, so Docker on Windows appropriately substitutes %CI_ARGS%
CMD "pixi run --manifest-path C:\pixi_ws\pixi.toml --frozen python run_ros2_batch.py %CI_ARGS%"