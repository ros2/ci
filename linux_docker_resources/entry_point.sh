#!/bin/sh

# This file fixes the permissions of the home directory so that it matches the host user's ID.
# It also enables multicast and changes directories before executing the input from docker run.

# Adapted from: http://chapeau.freevariable.com/2014/08/docker-uid.html

export ORIGPASSWD=$(cat /etc/passwd | grep rosbuild)
export ORIG_UID=$(echo $ORIGPASSWD | cut -f3 -d:)
export ORIG_GID=$(echo $ORIGPASSWD | cut -f4 -d:)

export UID=${UID:=$ORIG_UID}
export GID=${GID:=$ORIG_GID}

ARCH=`uname -i`

ORIG_HOME=$(echo $ORIGPASSWD | cut -f6 -d:)

echo "Enabling multicast..."
ifconfig eth0 multicast
echo "done."

# We only attempt to install Connext on amd64
if [ "${ARCH}" != "aarch64" ]; then
    # extract all ignored rmws
    # extract args between --ignore-rmw until the first appearance of '-'
    IGNORE_CONNEXTDDS=`echo ${CI_ARGS} | sed -e 's/.*ignore-rmw \([^-]*\).*/\1/' | sed -e 's/-.*//' | grep rmw_connextdds`
    IGNORE_CONNEXTCPP=`echo ${CI_ARGS} | sed -e 's/.*ignore-rmw \([^-]*\).*/\1/' | sed -e 's/-.*//' | grep rmw_connext_cpp`
    # Install RTI Connext DDS if we didn't find both `rmw_connextdds` and `rmw_connext_cpp`
    # within the "ignored RMWs" option string.
    if [ -z "${IGNORE_CONNEXTDDS}" -o -z "${IGNORE_CONNEXTCPP}" ]; then
        echo "Installing Connext..."
        case "${CI_ARGS}" in
          *--connext-debs*)
            echo "Using Debian package of Connext"
            if test -r /opt/rti.com/rti_connext_dds-6.0.1/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh; then
                echo "Sourcing RTI setenv script /opt/rti.com/rti_connext_dds-6.0.1/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh"
                . /opt/rti.com/rti_connext_dds-6.0.1/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh
            elif test -r /opt/rti.com/rti_connext_dds-5.3.1/resource/scripts/rtisetenv_x64Linux3gcc5.4.0.bash; then
                echo "rti_connextdds_cmake_module will guess the location of Connext 5.3.1 so don't source anything."
            fi
            ;;
          *)
            echo "Installing Connext binaries off RTI website..."
            if test -x /tmp/rti_connext_dds-5.3.1-eval-x64Linux3gcc5.4.0.run -a -r /tmp/rti_security_plugins-5.3.1-eval-x64Linux3gcc5.4.0.rtipkg -a -r /tmp/openssl-1.0.2n-5.3.1-host-x64Linux.rtipkg; then
                python3 -u /tmp/rti_web_binaries_install_script.py /tmp/rti_connext_dds-5.3.1-eval-x64Linux3gcc5.4.0.run /home/rosbuild/rti_connext_dds-5.3.1 --rtipkg_paths /tmp/rti_security_plugins-5.3.1-eval-x64Linux3gcc5.4.0.rtipkg /tmp/openssl-1.0.2n-5.3.1-host-x64Linux.rtipkg
                if [ $? -ne 0 ]; then
                    echo "Connext not installed correctly (maybe you're on an ARM machine?)." >&2
                    exit 1
                fi
                mv /tmp/openssl-1.0.2n /home/rosbuild/openssl-1.0.2n
                export RTI_OPENSSL_BIN=/home/rosbuild/openssl-1.0.2n/x64Linux3gcc5.4.0/release/bin
                export RTI_OPENSSL_LIBS=/home/rosbuild/openssl-1.0.2n/x64Linux3gcc5.4.0/release/lib
            elif test -x /tmp/rticonnextdds-src/rti_connext_dds-6.0.1-pro-host-x64Linux.run; then
                python3 -u /tmp/rti_web_binaries_install_script.py /tmp/rticonnextdds-src/rti_connext_dds-6.0.1-pro-host-x64Linux.run \
                    /home/rosbuild/rti_connext_dds-6.0.1 --rtipkg_paths \
                    /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/rti_connext_dds-6.0.1.25-pro-target-x64Linux4gcc7.3.0.rtipkg \
                    /tmp/rticonnextdds-src/openssl-1.1.1k-6.0.1.25-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/rti_security_plugins-6.0.1.25-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/rti_security_plugins-6.0.1.25-target-x64Linux4gcc7.3.0.rtipkg
                if [ $? -ne 0 ]; then
                    echo "Connext not installed correctly (maybe you're on an ARM machine?)." >&2
                    exit 1
                fi
                export CONNEXTDDS_DIR=/home/rosbuild/rti_connext_dds-6.0.1
                export RTI_OPENSSL_LIBS=$CONNEXTDDS_DIR/resource/app/lib/x64Linux2.6gcc4.4.5
            else
                echo "No connext installation files found found." >&2
                exit 1
            fi
            mv /tmp/rti_license.dat /home/rosbuild/rti_license.dat
            export RTI_LICENSE_FILE=/home/rosbuild/rti_license.dat
            ;;
        esac
        echo "done."
    else
        echo "NOT installing Connext."
    fi
fi

echo "Fixing permissions..."
sed -i -e "s/:$ORIG_UID:$ORIG_GID:/:$UID:$GID:/" /etc/passwd
sed -i -e "s/rosbuild:x:$ORIG_GID:/rosbuild:x:$GID:/" /etc/group

chown -R ${UID}:${GID} "${ORIG_HOME}"
echo "done."

exec sudo -H -u rosbuild -E -- xvfb-run -s "-ac -screen 0 1280x1024x24" /bin/sh -c "$*"
