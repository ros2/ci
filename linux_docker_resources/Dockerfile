FROM ubuntu:jammy
ARG INSTALL_CONNEXT_DEBS=false
ARG PLATFORM=x86
ARG ROS_DISTRO=rolling
ARG UBUNTU_DISTRO=jammy
ARG COMPILE_WITH_CLANG=false

# Prevent errors from apt-get.
# See: http://askubuntu.com/questions/506158/unable-to-initialize-frontend-dialog-when-using-ssh
ENV DEBIAN_FRONTEND noninteractive

# In pip 23.0.1 and newer, trying to use pip in a non-venv doesn't work.  We can workaround this
# by using the PIP_BREAK_SYSTEM_PACKAGES environment variable, and we can unconditionally set it
# since older pip will just ignore it.
ENV PIP_BREAK_SYSTEM_PACKAGES 1

# Fresh installation will always pull in contents from updates repositories regardless of the phased update percentage.
# To maintain working installations, always include updates regardless of rollout phase and set a machine ID so that
# changes in rollout behavior will at least be consistent across image buildtime and runtime.
# https://wiki.ubuntu.com/PhasedUpdates
# The closest thing to a canonical source I can find for this behavior is:
# https://discourse.ubuntu.com/t/phased-updates-in-apt-in-21-04/20345
RUN echo 'ros2-ci-container' > /etc/machine-id
RUN echo 'APT::Get::Always-Include-Phased-Updates "true";' > /etc/apt/apt.conf.d/90-phased-updates

RUN apt-get update && apt-get install --no-install-recommends -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# net-tools is for ifconfig
# Get curl for fetching the repo keys.
# Get https transport for APT.
RUN apt-get update && apt-get install --no-install-recommends -y \
  lsb-release net-tools sudo \
  ca-certificates \
  curl \
  gnupg2 \
  apt-transport-https

# Add the ROS repositories to the apt sources list.
RUN echo "deb http://repo.ros2.org/ubuntu/testing/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list
RUN echo "Bust Cache for key update 2021-06-01" && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

# Add the OSRF repositories to the apt sources list.
RUN if test \( ${UBUNTU_DISTRO} != noble \); then echo "deb http://packages.osrfoundation.org/gazebo/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-latest.list; fi
RUN curl --silent http://packages.osrfoundation.org/gazebo.key | apt-key add -

# automatic invalidation once every day.
RUN echo "@today_str"

# Install some development tools.
RUN apt-get update && apt-get install --no-install-recommends -y build-essential ccache cmake pkg-config python3-empy python3-pip python3-setuptools python3-vcstool
RUN apt-get update && apt-get install --no-install-recommends -y python3-lark python3-opencv

# Install build and test dependencies of ROS 2 packages.
RUN apt-get update && apt-get install --no-install-recommends -y \
  $(if test ${ROS_DISTRO} != humble -a ${ROS_DISTRO} != jazzy; then echo cargo; fi) \
  clang-format \
  cppcheck \
  git \
  libbenchmark-dev \
  libbullet-dev \
  $(if test ${UBUNTU_DISTRO} != noble; then echo libignition-cmake2-dev; fi) \
  $(if test ${UBUNTU_DISTRO} != noble; then echo libignition-math6-dev; fi) \
  liblz4-dev \
  liborocos-kdl-dev \
  libspdlog-dev \
  libsqlite3-dev \
  libxml2-dev \
  libxml2-utils \
  libxslt-dev \
  libyaml-cpp-dev \
  libyaml-dev \
  libzstd-dev \
  $(if test ${ROS_DISTRO} != humble -a ${ROS_DISTRO} != jazzy; then echo nlohmann-json3-dev; fi) \
  pybind11-dev \
  pydocstyle \
  python3-argcomplete \
  python3-colcon-bash \
  python3-colcon-cmake \
  python3-colcon-core \
  python3-colcon-defaults \
  python3-colcon-library-path \
  python3-colcon-metadata \
  python3-colcon-mixin \
  python3-colcon-output \
  python3-colcon-package-information \
  python3-colcon-package-selection \
  python3-colcon-parallel-executor \
  python3-colcon-pkg-config \
  python3-colcon-powershell \
  python3-colcon-python-setup-py \
  python3-colcon-recursive-crawl \
  python3-colcon-ros \
  python3-colcon-ros-domain-id-coordinator \
  python3-colcon-test-result \
  python3-colcon-zsh \
  python3-coverage \
  python3-cryptography \
  python3-fastjsonschema \
  python3-flake8 \
  python3-flake8-blind-except \
  python3-flake8-builtins \
  python3-flake8-class-newline \
  python3-flake8-comprehensions \
  python3-flake8-deprecated \
  python3-flake8-docstrings \
  python3-flake8-import-order \
  python3-flake8-quotes \
  python3-importlib-metadata \
  python3-jsonschema \
  python3-lxml \
  python3-mock \
  python3-mypy \
  $(if test ${ROS_DISTRO} = humble; then echo python3-netifaces; fi) \
  python3-nose \
  python3-numpy \
  python3-osrf-pycommon \
  python3-psutil \
  python3-pyflakes \
  python3-pykdl \
  python3-pyparsing \
  python3-pytest-cov \
  python3-pytest-mock \
  python3-pytest-repeat \
  python3-pytest-rerunfailures \
  python3-pytest-runner \
  python3-pytest-timeout \
  python3-yaml \
  uncrustify \
  yamllint

# Install LTTng-related packages for tracing.
# For Humble, tracing is not enabled by default, so we do nothing.
# For Rolling and Jazzy and later we build our own python bindings so we need additional development libraries.
RUN if test \( ${ROS_DISTRO} = humble \); then \
      true \
    ; else \
      apt-get update && apt-get install --no-install-recommends -y liblttng-ust-dev lttng-tools python3-babeltrace liblttng-ctl-dev \
    ; fi

# Install clang if build arg is true
RUN if test ${COMPILE_WITH_CLANG} = true; then apt-get update && apt-get install --no-install-recommends -y clang libc++-dev libc++abi-dev; fi

# Install coverage build dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y lcov

# There is a bug in upstream lcov-to-cobertura-xml with newer versions of lcov.  There is an
# open PR for it in https://github.com/eriwen/lcov-to-cobertura-xml/pull/55, but until that is
# merged use the fork with the fix.
RUN pip3 install -U git+https://github.com/ahcorde/lcov-to-cobertura-xml@master

# Install the Connext binary from the OSRF repositories. if ROS_DISTRO is humble or jazzy
# install rti-connext-dds-6.0.1 else install rti-connext-dds-7.3.0-ros.
RUN if test \( ${PLATFORM} = x86 -a ${INSTALL_CONNEXT_DEBS} = true \); then \
  if test \( ${ROS_DISTRO} = humble -o ${ROS_DISTRO} = jazzy \); then \
    apt-get update && RTI_NC_LICENSE_ACCEPTED=yes apt-get install -y rti-connext-dds-6.0.1; \
  else \
    apt-get update && RTI_NC_LICENSE_ACCEPTED=yes apt-get install -y rti-connext-dds-7.3.0-ros; \
  fi; \
    fi

# Install the RTI dependencies.
RUN if test ${PLATFORM} = x86; then apt-get update && apt-get install --no-install-recommends -y default-jre-headless; fi

# Install dependencies for RTI web binaries install script.
RUN apt-get update && apt-get install --no-install-recommends -y python3-pexpect

# Get and install the RTI Connext web binaries.
# RTI Connext web binaries installation is only supported on x86_64.
COPY rticonnextdds-src/ /tmp/rticonnextdds-src

# Join the correct Connext version files based on the value of ROS_DISTRO.
RUN if test ${ROS_DISTRO} = jazzy -o ${ROS_DISTRO} = humble; then \
  for splitpkg in \
    /tmp/rticonnextdds-src/rti_connext_dds-6.0.1-pro-host-x64Linux.run \
    /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-host-x64Linux.rtipkg \
    /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-target-x64Linux4gcc7.3.0.rtipkg; do \
    cat $(echo ${splitpkg}.0?? | sort) > $splitpkg; \
  done; \
    else \
  for splitpkg in \
    /tmp/rticonnextdds-src/rti_connext_dds-7.3.0-pro-host-x64Linux.run \
    /tmp/rticonnextdds-src/rti_connext_dds-7.3.0-pro-target-x64Linux4gcc7.3.0.rtipkg; do \
    cat $(echo ${splitpkg}.0?? | sort) > $splitpkg; \
  done; \
    fi

# Make the RTI Connext installation script executable. For any version of Connext.
RUN chmod 755 /tmp/rticonnextdds-src/rti_connext_dds-*-pro-host-x64Linux.run

# Add the connextdds installation script used in entry_point.sh
ADD rti_web_binaries_install_script.py /tmp/rti_web_binaries_install_script.py

# Add the RTI license file.
ADD rticonnextdds-license/rti_license.dat /tmp/rti_license.dat

# Install the eProsima dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y libasio-dev libssl-dev libtinyxml2-dev valgrind

# Install the CycloneDDS dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y bison libcunit1-dev

# Install OpenCV.
RUN apt-get update && apt-get install --no-install-recommends -y libopencv-dev

# Install console_bridge for class_loader et al.
RUN apt-get update && apt-get install --no-install-recommends -y libconsole-bridge-dev

# Install build dependencies for rviz et al.
RUN apt-get update && apt-get install --no-install-recommends -y libassimp-dev libcurl4-openssl-dev libfreetype6-dev libgles2-mesa-dev libglu1-mesa-dev libxaw7-dev libxrandr-dev qtbase5-dev

# Install build dependencies for rqt et al.
RUN apt-get update && apt-get install --no-install-recommends -y pyqt5-dev python3-pyqt5 python3-pyqt5.qtsvg python3-sip-dev python3-pydot python3-pygraphviz

# Install dependencies for robot_model and robot_state_publisher
RUN apt-get update && apt-get install --no-install-recommends -y libeigen3-dev
RUN if test \( ${ROS_DISTRO} = humble \); then apt-get update && apt-get install --no-install-recommends -y libtinyxml-dev; fi

# Install Python3 development files.
RUN apt-get update && apt-get install --no-install-recommends -y python3-dev

# Install dependencies for RViz visual tests
RUN apt-get update && apt-get install --no-install-recommends -y \
    libgl1-mesa-dri \
    libglapi-mesa \
    libosmesa6 \
    mesa-utils \
    xvfb \
    matchbox-window-manager

# Install dependencies for iceoryx
RUN apt-get update && apt-get install -y \
    acl \
    libacl1-dev \
    libncurses5-dev

# After all packages are installed, update ccache symlinks (see ros2/ci#326).
# This command is supposed to be invoked whenever a new compiler is installed
# but that isn't happening. So we invoke it here to make sure all compilers are
# picked up.
RUN update-ccache-symlinks

ENV DISPLAY=:99
# Making the RTI Connext env variable to the entry_point.sh script so that it can be used to run
# the RTI Connext installation script.
ENV ROS_DISTRO=${ROS_DISTRO}

# Create a user to own the build output.
RUN useradd -u 1234 -m rosbuild
RUN sudo -H -u rosbuild -- git config --global user.email "jenkins@ci.ros2.org"
RUN sudo -H -u rosbuild -- git config --global user.name "Jenkins ROS 2"
RUN echo 'rosbuild ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Add an entry point which changes rosbuild's UID from 1234 to the UID of the invoking user.
# This means that the generated files will have the same ownership as the host OS user.
COPY entry_point.sh /entry_point.sh
RUN chmod 755 /entry_point.sh

ENTRYPOINT ["/entry_point.sh"]

CMD ["matchbox-window-manager > /dev/null 2>&1 & python3 -u run_ros2_batch.py $CI_ARGS"]
