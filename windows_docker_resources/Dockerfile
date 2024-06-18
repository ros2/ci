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

# Install cinc-solo, a compiled binary of chef-solo
RUN powershell "iex  ((New-Object System.Net.WebClient).DownloadString('https://omnitruck.cinc.sh/install.ps1')); install -version 16.15.22"
# Update certificate bundle to work Let's Encrypt root certificate expiration
# https://www.openssl.org/blog/blog/2021/09/13/LetsEncryptRootCertExpire/
# (in the parlance of the above post we're using workaround 1)
# This workaround is being incorporated directly in future releases of Cinc 16 and 17.
# Our application of the work around should be removed when updating to such a version.
COPY cacert.pem c:\cinc-project\cinc\embedded\ssl\certs\cacert.pem
COPY cacert.pem c:\cinc-project\cinc\embedded\lib\ruby\gems\2.7.0\gems\httpclient-2.8.3\lib\httpclient\cacert.pem

# Install Chocolatey by powershell script

# Pining chocolatey version to 1.4.0 previous one to major bump to 2.0.0 due to issues with chocolatey_package chef resource 
# See https://github.com/chef/chef/issues/13751 for more detail of the issue
# This should be solved for chef version 18; see https://github.com/chef/chef/pull/13833
RUN powershell -noexit "$env:chocolateyDownloadUrl = 'https://community.chocolatey.org/api/v2/package/chocolatey/1.4.0'; Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

# choco installs. chef-workstation is being installed to get berks and download cookbook dependencies
RUN choco install -y git chef-workstation

# Copy over necessary files into container
RUN IF NOT EXIST "C:\TEMP" mkdir C:\TEMP
COPY rticonnextdds-license\ C:\TEMP\rticonnextdds-license
COPY rticonnextdds-src\ C:\TEMP\rticonnextdds-src
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe
RUN copy /b C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg.??? C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg

# ROS_DISTRO argument should be set to install dependencies for the target ROS version.
ARG ROS_DISTRO


COPY install_ros2_${ROS_DISTRO}.json C:\TEMP\
COPY solo.rb C:\TEMP\
COPY ros2-cookbooks\ C:\TEMP\ros2-cookbooks
RUN IF NOT EXIST "C:\TEMP" mkdir C:\TEMP\environments
COPY qtaccount\ros2ci.rb C:\TEMP\environments\ros2ci.rb

# REMOVE ME: Debug
RUN echo %VS_VERSION%

# Dinamically set VS_VERSION from CI options
RUN powershell "(Get-Content  C:\TEMP\install_ros2_%ROS_DISTRO%.json).replace('VS_VERSION', $(%VS_VERSION%)) | Set-Content  C:\TEMP\install_ros2_%ROS_DISTRO%.json"

# REMOVE ME: Debug 
RUN type C:\TEMP\install_ros2_%ROS_DISTRO%.json
# Download vendor cookbooks
WORKDIR C:\TEMP\ros2-cookbooks\cookbooks\ros2_windows
RUN C:\opscode\chef-workstation\bin\berks vendor C:\TEMP\ros2-cookbooks\cookbooks

# Initial run
RUN c:\cinc-project\cinc\bin\cinc-solo.bat -c C:\TEMP\solo.rb -Eros2ci -j C:\TEMP\install_ros2_%ROS_DISTRO%.json

# Invalidate daily to run updates
RUN echo "@todays_date"
RUN c:\cinc-project\cinc\bin\cinc-solo.bat -c C:\TEMP\solo.rb -Eros2ci -j C:\TEMP\install_ros2_%ROS_DISTRO%.json

WORKDIR C:\ci
CMD ["C:\\Program Files (x86)\\Microsoft Visual Studio\\%VS_VERSION%\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat", "x86_amd64", "&&", `
     "python", "run_ros2_batch.py", "%CI_ARGS%"]
