FROM ubuntu:xenial
ARG BRIDGE=false
ARG INSTALL_TURTLEBOT2_DEMO_DEPS=false
ARG PLATFORM=x86

# Prevent errors from apt-get.
# See: http://askubuntu.com/questions/506158/unable-to-initialize-frontend-dialog-when-using-ssh
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# net-tools is for ifconfig
RUN apt-get update && apt-get install --no-install-recommends -y lsb-release net-tools sudo

# Get curl for fetching the repo keys.
RUN apt-get update && apt-get install --no-install-recommends -y curl

# Get https transport for APT.
RUN apt-get update && apt-get install --no-install-recommends -y apt-transport-https

# Add the ROS repositories to the apt sources list.
RUN echo "deb http://repositories.ros.org/ubuntu/testing/ `lsb_release -cs` main" > /etc/apt/sources.list.d/ros-latest.list
RUN curl --silent http://repositories.ros.org/repos.key | apt-key add -

# Add the OSRF repositories to the apt sources list.
RUN echo "deb http://packages.osrfoundation.org/gazebo/ubuntu `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-latest.list
RUN curl --silent http://packages.osrfoundation.org/gazebo.key | apt-key add -

# Install some development tools.
RUN apt-get update && apt-get install --no-install-recommends -y build-essential ccache cmake pkg-config python3-empy python3-setuptools python3-vcstool

# Install build and test dependencies of ROS 2 packages.
RUN apt-get update && apt-get install --no-install-recommends -y clang-format-3.8 cppcheck git pydocstyle pyflakes python3-coverage python3-flake8 python3-mock python3-nose python3-pep8 python3-yaml uncrustify

# Install and self update pip/setuptools to the latest version.
RUN apt-get update && apt-get install --no-install-recommends -y python3-pip
RUN pip3 install -U setuptools pip virtualenv

# Install coverage build dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y gcovr

# Install the OpenSplice binary from the OSRF repositories.
RUN if test \( ${PLATFORM} = aarch64 -o ${PLATFORM} = x86 \) ; then apt-get update && apt-get install --no-install-recommends -y libopensplice67=6.7.0+osrf2-2~xenial; fi
# Update default domain id.
RUN if test \( ${PLATFORM} = aarch64 -o ${PLATFORM} = x86 \) ; then sed -i "s/<Id>0<\/Id>/<Id>108<\/Id>/" /usr/etc/opensplice/config/ospl.xml; fi

# Install the RTI dependencies.
RUN if test ${PLATFORM} = x86; then apt-get update && apt-get install --no-install-recommends -y default-jre-headless; fi

# Install dependencies for RTI web binaries install script.
RUN pip3 install pexpect

# Get and install the RTI web binaries.
RUN curl --silent http://s3.amazonaws.com/RTI/Bundles/5.2.3/Evaluation/rti_connext_dds-5.2.3-eval-x64Linux3gcc4.8.2.run -o /tmp/rti-installer.run && chmod +x /tmp/rti-installer.run
ADD rti_web_binaries_install_script.py /tmp/rti_web_binaries_install_script.py

# Add the RTI license file.
ADD rticonnextdds-license/rti_license.dat /tmp/rti_license.dat

# Add the RTI binaries we made.
ADD rticonnextdds-src/librticonnextdds52_5.2.3-1_amd64.deb /tmp/librticonnextdds52_5.2.3-1_amd64.deb
ADD rticonnextdds-src/librticonnextdds52-dev_5.2.3-1_amd64.deb /tmp/librticonnextdds52-dev_5.2.3-1_amd64.deb
ADD rticonnextdds-src/rticonnextdds-tools_5.2.3-1_amd64.deb /tmp/rticonnextdds-tools_5.2.3-1_amd64.deb

# Install the eProsima dependencies.
RUN apt-get update && apt-get install --no-install-recommends -y libasio-dev libssl-dev libtinyxml2-dev valgrind

# Install OpenCV.
RUN apt-get update && apt-get install --no-install-recommends -y libopencv-dev

# Install build dependencies for class loader.
RUN apt-get update && apt-get install --no-install-recommends -y libpoco-dev libpocofoundation9v5 libpocofoundation9v5-dbg

# Install dependencies for robot_model and robot_state_publisher
RUN apt-get update && apt-get install --no-install-recommends -y libtinyxml-dev libeigen3-dev

# Install Python3 development files.
RUN apt-get update && apt-get install --no-install-recommends -y python3-dev

# automatic invalidation once every day.
RUN echo "@today_str"

# Install build and test dependencies of ros1_bridge.
RUN if test ${BRIDGE} = true; then apt-get update && apt-get install --no-install-recommends -y python-rospkg ros-kinetic-catkin ros-kinetic-common-msgs ros-kinetic-rosbash ros-kinetic-roscpp ros-kinetic-roslaunch ros-kinetic-rosmsg ros-kinetic-roscpp-tutorials ros-kinetic-rospy-tutorials ros-kinetic-tf2-msgs; fi

# Install build dependencies for turtlebot demo.
RUN if test ${INSTALL_TURTLEBOT2_DEMO_DEPS} = true; then apt-get update && apt-get install --no-install-recommends -y libatlas-base-dev libboost-iostreams-dev libboost-regex-dev libboost-system-dev libboost-thread-dev libceres-dev libgoogle-glog-dev liblua5.2-dev libpcl-dev libprotobuf-dev libsdl1.2-dev libsdl-image1.2-dev libsuitesparse-dev libudev-dev libusb-1.0.0-dev libyaml-cpp-dev protobuf-compiler python-sphinx ros-kinetic-kobuki-driver ros-kinetic-kobuki-ftdi; fi

# Workaround bugs in the Ubuntu 16.04 packaging of libpcl.  Reports:
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=819741
# https://bugs.launchpad.net/ubuntu/+source/vtk6/+bug/1573234
# https://github.com/PointCloudLibrary/pcl/issues/1594
# TODO(clalancette): for some reason, if these two workarounds are listed in
# different RUN statements, it causes the docker image to fail to build on
# aarch64 (see https://github.com/ros2/ci/pull/73).  As a workaround, do them
# in one statement.
RUN if test ${INSTALL_TURTLEBOT2_DEMO_DEPS} = true; then sed -i -e '/vtkproj4;/d' /usr/lib/$(uname -m)-linux-gnu/cmake/pcl/PCLConfig.cmake && ln -s /usr/lib/$(uname -m)-linux-gnu/libproj.so.9.1.0 /usr/lib/$(uname -m)-linux-gnu/libproj.so; fi

# Create a user to own the build output.
RUN useradd -u 1234 -m rosbuild
RUN sudo -H -u rosbuild -- git config --global user.email "jenkins@ci.ros2.org"
RUN sudo -H -u rosbuild -- git config --global user.name "Jenkins ROS 2"
RUN echo 'rosbuild ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
WORKDIR /home/rosbuild

# Add an entry point which changes rosbuild's UID from 1234 to the UID of the invoking user.
# This means that the generated files will have the same ownership as the host OS user.
ADD entry_point.sh /entry_point.sh
RUN chmod 755 /entry_point.sh

ENTRYPOINT ["/entry_point.sh"]

CMD ["python3 -u run_ros2_batch.py $CI_ARGS"]
