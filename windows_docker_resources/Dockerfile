# escape=`
# This Dockerfile needs to be built from the parent directory (ros2/ci) so the build context
# includes the python scripts

# To find this value run in powershell:
# $(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').ReleaseId
ARG WINDOWS_RELEASE_ID=1909

# Indicates that the windows image will be used as the base image. Must be same or older than host.
# --isolation=hyperv is needed for both build/run if the image id is older than the host id
# Use --isolation=process if you need to build in a mounted volume
# FROM mcr.microsoft.com/windows:$WINDOWS_RELEASE_ID
FROM mcr.microsoft.com/windows@sha256:27f1a2a1f2f784f3716c2400d7e1bf93074a75e15f2974861c00275f93487c88

# Install cinc-solo, a compiled binary of chef-solo
RUN powershell "iex  ((New-Object System.Net.WebClient).DownloadString('https://omnitruck.cinc.sh/install.ps1')); install"

# Install Chocolatey by powershell script
RUN powershell -noexit "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

# choco installs
RUN choco install -y git chefdk

# Copy over necessary files into container
RUN mkdir C:\TEMP
# COPY rticonnextdds-license C:\TEMP\
# COPY rticonnextdds-src C:\TEMP\
COPY install_ros2.json C:\TEMP\
COPY solo.rb C:\TEMP\
COPY ros2-cookbooks\ C:\TEMP\ros2-cookbooks
COPY qtaccount\qtaccount.ini C:\TEMP\ros2-cookbooks\cookbooks\ros2_windows\files\

# Download vendor cookbooks
WORKDIR C:\TEMP\ros2-cookbooks\cookbooks\ros2_windows
RUN C:\opscode\chefdk\bin\berks vendor C:\TEMP\ros2-cookbooks\cookbooks

# Initial run
RUN c:\cinc-project\cinc\bin\cinc-solo -c C:\TEMP\solo.rb -j C:\TEMP\install_ros2.json

# Invalidate daily to run updates
RUN echo "@todays_date"
RUN c:\cinc-project\cinc\bin\cinc-solo -c C:\TEMP\solo.rb -j C:\TEMP\install_ros2.json

WORKDIR C:\ci
CMD ["C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat", "x86_amd64", "&&", `
     "python", "run_ros2_batch.py", "%CI_ARGS%"]
