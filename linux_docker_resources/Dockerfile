FROM ubuntu:focal
ARG BRIDGE=false
ARG INSTALL_CONNEXT_DEBS=false
ARG PLATFORM=x86
ARG ROS1_DISTRO=noetic
ARG ROS_DISTRO=rolling
ARG UBUNTU_DISTRO=focal
ARG COMPILE_WITH_CLANG=false

# Prevent errors from apt-get.
# See: http://askubuntu.com/questions/506158/unable-to-initialize-frontend-dialog-when-using-ssh
ENV DEBIAN_FRONTEND noninteractive

# Opt-out of phased updates, which can create inconsistencies between installed package versions as different containers end up on different phases.
# https://wiki.ubuntu.com/PhasedUpdates
RUN echo 'APT::Get::Never-Include-Phased-Updates "true";' > /etc/apt/apt.conf.d/90-phased-updates

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
RUN if test ${UBUNTU_DISTRO} != jammy; then echo "deb http://repositories.ros.org/ubuntu/testing/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list; fi
RUN if test ${UBUNTU_DISTRO} = jammy; then echo "deb http://repo.ros2.org/ubuntu/testing/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list; fi
RUN echo "Bust Cache for key update 2021-06-01" && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add -

# Add the OSRF repositories to the apt sources list.
RUN echo "deb http://packages.osrfoundation.org/gazebo/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-latest.list
RUN curl --silent http://packages.osrfoundation.org/gazebo.key | apt-key add -

# Install some development tools.
RUN apt-get update && apt-get install --no-install-recommends -y build-essential ccache cmake pkg-config python3-empy python3-pip python3-setuptools python3-vcstool python3-venv
RUN apt-get update && apt-get install --no-install-recommends -y python3-lark python3-opencv
# Install virtualenv 16.7.9 needed for Foxy builds on Focal. https://github.com/ros2/ci/issues/400
RUN if test ${UBUNTU_DISTRO} = focal; then python3 -m pip install virtualenv==16.7.9; fi

# Install build and test dependencies of ROS 2 packages.
RUN apt-get update && apt-get install --no-install-recommends -y \
  clang-format \
  cppcheck \
  git \
  libbenchmark-dev \
  libbullet-dev \
  liblog4cxx-dev \
  liborocos-kdl-dev \
  libspdlog-dev \
  libxml2-dev \
  libxml2-utils \
  libxslt-dev \
  libyaml-cpp-dev \
  pydocstyle \
  python3-pyflakes \
  python3-coverage \
  python3-cryptography \
  python3-flake8 \
  python3-lxml \
  python3-mock \
  python3-mypy \
  python3-netifaces \
  python3-nose \
  python3-numpy \
  python3-pep8 \
  python3-psutil \
  python3-pykdl \
  python3-pyparsing \
  python3-pytest-mock \
  python3-pytest-timeout \
  python3-yaml \
  uncrustify \
  yamllint

# Install clang if build arg is true
RUN if test ${COMPILE_WITH_CLANG} = true; then apt-get update && apt-get install --no-install-recommends -y clang libc++-dev libc++abi-dev; fi

# Install coverage build dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y lcov
RUN pip3 install -U lcov_cobertura_fix

# Install the Connext binary from the OSRF repositories.
RUN if test \( ${PLATFORM} = x86 -a ${INSTALL_CONNEXT_DEBS} = true -a ${UBUNTU_DISTRO} != jammy \); then apt-get update && RTI_NC_LICENSE_ACCEPTED=yes apt-get install -y rti-connext-dds-5.3.1; fi
RUN if test \( ${PLATFORM} = x86 -a ${INSTALL_CONNEXT_DEBS} = true -a ${UBUNTU_DISTRO} = jammy \); then apt-get update && RTI_NC_LICENSE_ACCEPTED=yes apt-get install -y rti-connext-dds-6.0.1; fi

# Install the RTI dependencies.
RUN if test ${PLATFORM} = x86; then apt-get update && apt-get install --no-install-recommends -y default-jre-headless; fi

# Install dependencies for RTI web binaries install script.
RUN apt-get update && apt-get install --no-install-recommends -y python3-pexpect

# Get and install the RTI web binaries.
# Connext 5.3.1 for focal and earlier.
RUN if test ${UBUNTU_DISTRO} != jammy; then cd /tmp && curl --silent https://s3.amazonaws.com/RTI/Bundles/5.3.1/Evaluation/rti_connext_dds_secure-5.3.1-eval-x64Linux3gcc5.4.0.tar.gz | tar -xz; fi
RUN if test ${UBUNTU_DISTRO} != jammy; then cd /tmp && tar -xvf /tmp/openssl-1.0.2n-target-x64Linux3gcc5.4.0.tar.gz; fi
# Connext 6.0.1 for jammy, the evaluation bundles don't contain security extensions so we need to distribute the pro binaries to ourselves.
COPY rticonnextdds-src/ /tmp/rticonnextdds-src
RUN for splitpkg in \
  /tmp/rticonnextdds-src/rti_connext_dds-6.0.1-pro-host-x64Linux.run \
  /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-host-x64Linux.rtipkg \
  /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-target-x64Linux4gcc7.3.0.rtipkg; do \
    cat $(echo ${splitpkg}.0?? | sort) > $splitpkg; \
  done
RUN chmod 755 /tmp/rticonnextdds-src/rti_connext_dds-6.0.1-pro-host-x64Linux.run

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
RUN apt-get update && apt-get install --no-install-recommends -y libassimp-dev libcurl4-openssl-dev libfreetype6-dev libgles2-mesa-dev libglu1-mesa-dev libqt5core5a libqt5gui5 libqt5opengl5 libqt5widgets5 libxaw7-dev libxrandr-dev qtbase5-dev

# Install build dependencies for rqt et al.
RUN apt-get update && apt-get install --no-install-recommends -y pyqt5-dev python3-pyqt5 python3-pyqt5.qtsvg python3-sip-dev python3-pydot python3-pygraphviz

# Install dependencies for robot_model and robot_state_publisher
RUN apt-get update && apt-get install --no-install-recommends -y libtinyxml-dev libeigen3-dev

# Install Python3 development files.
RUN apt-get update && apt-get install --no-install-recommends -y python3-dev

# automatic invalidation once every day.
RUN echo "@today_str"

# Install build and test dependencies of ros1_bridge if there is a valid ROS 1 distro.
RUN if test ${BRIDGE} = true -a -n "${ROS1_DISTRO}"; then apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS1_DISTRO}-catkin \
    ros-${ROS1_DISTRO}-common-msgs \
    ros-${ROS1_DISTRO}-rosbash \
    ros-${ROS1_DISTRO}-roscpp \
    ros-${ROS1_DISTRO}-roslaunch \
    ros-${ROS1_DISTRO}-rosmsg \
    ros-${ROS1_DISTRO}-roscpp-tutorials \
    ros-${ROS1_DISTRO}-rospy-tutorials \
    ros-${ROS1_DISTRO}-tf2-msgs; fi

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
