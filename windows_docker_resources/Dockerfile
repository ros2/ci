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

# Copy over necessary Connext files into container
RUN IF NOT EXIST "C:\TEMP" mkdir C:\TEMP
COPY rticonnextdds-license\ C:\TEMP\rticonnextdds-license
COPY rticonnextdds-src\ C:\TEMP\rticonnextdds-src
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg
# TODO(clalancette): Actually install Connext

# Download and install MSVC
RUN powershell -noexit irm https://aka.ms/vs/16/release/vs_buildtools.exe -OutFile vs_buildtools.exe
RUN vs_buildtools.exe --quiet --wait --norestart --add Microsoft.Component.MSBuild --add Microsoft.Net.Component.4.6.1.TargetingPack --add Microsoft.Net.Component.4.8.SDK --add Microsoft.VisualStudio.Component.CoreBuildTools --add Microsoft.VisualStudio.Component.Roslyn.Compiler --add Microsoft.VisualStudio.Component.TextTemplating --add Microsoft.VisualStudio.Component.VC.CLI.Support --add Microsoft.VisualStudio.Component.VC.CoreBuildTools --add Microsoft.VisualStudio.Component.VC.CoreIde --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --add Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Workload.VCTools

# Install pixi
RUN powershell -noexit "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://pixi.sh/install.ps1'))"

# Initialize pixi workspace
WORKDIR C:\pixi_ws
RUN powershell -noexit "pixi --color never init"

COPY pixi.toml pixi.toml

# Install dependencies via pixi
# RUN powershell -noexit "pixi --color never install"

# Invalidate daily to run updates
RUN echo "@todays_date"

# Note that this *must* be in shell form, not exec form, so Docker on Windows appropriately substitutes %CI_ARGS%
CMD "pixi run "cd C:\ci ; python run_ros2_batch.py %CI_ARGS%""
