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

# Install pixi
RUN powershell -noexit "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://pixi.sh/install.ps1'))"

# Initialize pixi workspace
WORKDIR C:\pixi_ws
RUN powershell -noexit "pixi --color never init"

# Install dependencies
# TODO(clalancette): Missing:
# flake8-class-newline==1.6.0
# flake8-deprecated==2.2.1
# importlib-metadata==4.12.0 (we are getting 8.5.0 instead)
# pytest-repeat==0.9.3 (we are getting 0.9.2 instead)
# pytest-runner==2.11.1 (we are getting 6.0.0 instead)
# colcon-ros-domain-id-coordinator
RUN powershell -noexit "pixi --color never add python==3.12.3 pip==24.0 git==2.43.0 empy==3.3.4 catkin_pkg==1.0.0 cryptography==41.0.7 coverage==7.4.4 flake8==7.0.0 flake8-blind-except==0.2.1 flake8-builtins==2.1.0 flake8-comprehensions==3.14.0 flake8-docstrings==1.6.0 flake8-import-order==0.18.2 flake8-quotes==3.4.0 importlib-metadata==8.5.0 lark==1.1.9 mypy==1.9.0 pytest==7.4.4 pytest-cov==4.1.0 pytest-mock==3.12.0 pytest-repeat==0.9.2 pytest-rerunfailures==12.0 pytest-runner==6.0.0 pytest-timeout==2.2.0 pyyaml==6.0.1 vcstool==0.3.0 yamllint==1.33.0 colcon-core colcon-defaults colcon-library-path colcon-metadata colcon-mixin colcon-output colcon-package-information colcon-package-selection colcon-parallel-executor colcon-pkg-config colcon-powershell colcon-python-setup-py colcon-recursive-crawl colcon-test-result colcon-cmake colcon-ros lxml==5.2.1 numpy==1.26.4 setuptools==68.1.2"

# Invalidate daily to run updates
RUN echo "@todays_date"

# Note that this *must* be in shell form, not exec form, so Docker on Windows appropriately substitutes %CI_ARGS%
CMD "pixi run "cd C:\ci ; python run_ros2_batch.py %CI_ARGS%""
