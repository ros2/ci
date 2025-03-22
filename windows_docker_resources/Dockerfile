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
RUN powershell -noexit "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://pixi.sh/install.ps1'))"

# Install dependencies via pixi
ARG ROS_DISTRO=rolling
WORKDIR C:\pixi_ws
ADD https://github.com/ros2/ros2.git#${ROS_DISTRO} C:\TEMP\ros2
RUN powershell "(Get-Content C:\TEMP\ros2)"
RUN copy C:\TEMP\ros2\pixi.toml pixi.toml
RUN pixi --color never --no-progress -q install
RUN pixi --color never --no-progress -q list

# Setup environment variables needed for Connext
ENV RTI_LICENSE_FILE C:\connext\rti_license.dat
ENV CONNEXTDDS_DIR C:\connext\rti_connext_dds-6.0.1
ENV RTI_OPENSSL_BIN C:\connext\openssl-1.1.1k\x64Win64VS2017\bin
ENV RTI_OPENSSL_LIB C:\connext\openssl-1.1.1k\x64Win64VS2017\lib

# Copy over necessary Connext files into container
RUN IF NOT EXIST "C:\TEMP" mkdir C:\TEMP
COPY rticonnextdds-src\ C:\TEMP\rticonnextdds-src
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg
COPY rticonnextdds-license\rti_license.dat $RTI_LICENSE_FILE

# Install Connext
RUN pixi run 7z x -oC:\connext C:\TEMP\rticonnextdds-src\openssl-1.1.1k-target-x64Win64VS2017.zip
RUN C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe --mode unattended --unattendedmodeui minimalWithDialogs --prefix C:\connext
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\openssl-1.1.1k-6.0.1.25-host-x64Win64.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-host-x64Win64.rtipkg
RUN %CONNEXTDDS_DIR%\bin\rtipkginstall.bat -u C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-target-x64Win64VS2017.rtipkg

# Note that this *must* be in shell form, not exec form, so Docker on Windows appropriately substitutes %CI_ARGS%
WORKDIR C:\ci
CMD "pixi run --manifest-path C:\pixi_ws\pixi.toml python run_ros2_batch.py %CI_ARGS%"
