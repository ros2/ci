#!/bin/sh

# This file fixes the permissions of the home directory so that it matches the host user's ID.
# It also enables multicast and changes directories before executing the input from docker run.

# Adapted from: http://chapeau.freevariable.com/2014/08/docker-uid.html

set -ex

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

. /etc/os-release

# We only attempt to install Connext on Ubuntu amd64
if [ "${ARCH}" = "x86_64" -a "${ID}" = "ubuntu" ]; then
    IGNORE_CONNEXTDDS=""
    ignore_rwm_seen="false"
    for arg in ${CI_ARGS} ; do
        case $arg in
            ("--ignore-rmw") ignore_rmw_seen="true" ;;
            ("-"*) ignore_rmw_seen="false" ;;
            (*) if [ $ignore_rmw_seen = "true" ] ; then [ $arg = "rmw_connextdds" ] && IGNORE_CONNEXTDDS="true" && break ; fi
        esac
    done

    # Install RTI Connext DDS if we didn't find 'rmw_connextdds' within the "ignore-rmw" option strings.
    if [ -z "${IGNORE_CONNEXTDDS}" ]; then
        echo "Installing Connext..."

        export CONNEXT_FULL_VERSION="7.3.0"
        export CONNEXT_DISPLAY_VERSION="$CONNEXT_FULL_VERSION"
        if [ "${ROS_DISTRO}" = "jazzy" ] || [ "${ROS_DISTRO}" = "humble" ]; then
            export CONNEXT_FULL_VERSION="6.0.1.25"
            export CONNEXT_DISPLAY_VERSION="${CONNEXT_FULL_VERSION%.*}"
        fi

        case "${CI_ARGS}" in
          *--connext-debs*)
            echo "Using Debian package of Connext"
            if test -r /opt/rti.com/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh; then
                echo "Sourcing RTI setenv script /opt/rti.com/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh"
                . /opt/rti.com/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}/resource/scripts/rtisetenv_x64Linux4gcc7.3.0.sh
            fi
            ;;
          *)
            echo "Installing Connext binaries off RTI website..."
            if test -x /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}-pro-host-x64Linux.run; then
                rtipkg_list="\
                /tmp/rticonnextdds-src/openssl-3.0.12-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
                /tmp/rticonnextdds-src/openssl-3.0.12-${CONNEXT_FULL_VERSION}-target-x64Linux4gcc7.3.0.rtipkg \
                /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-host-openssl-3.0-x64Linux.rtipkg \
                /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-target-openssl-3.0-x64Linux4gcc7.3.0.rtipkg \
                "
                connext_base_architecture="x64Linux3gcc4.8.2"
                if [ "${CONNEXT_FULL_VERSION}" = "6.0.1.25" ]; then
                    rtipkg_list="\
                    /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_FULL_VERSION}-pro-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/openssl-1.1.1k-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
                    /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-target-x64Linux4gcc7.3.0.rtipkg \
                    "
                    connext_base_architecture="x64Linux2.6gcc4.4.5"
                fi
                python3 -u /tmp/rti_web_binaries_install_script.py /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}-pro-host-x64Linux.run \
                    /home/rosbuild/rti_connext_dds-${CONNEXT_DISPLAY_VERSION} --rtipkg_paths \
                    /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_FULL_VERSION}-pro-target-x64Linux4gcc7.3.0.rtipkg \
                    $rtipkg_list
                if [ $? -ne 0 ]; then
                    echo "Connext not installed correctly (maybe you're on an ARM machine?)." >&2
                    exit 1
                fi
                export CONNEXTDDS_DIR=/home/rosbuild/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}
                export RTI_OPENSSL_LIBS=$CONNEXTDDS_DIR/resource/app/lib/${connext_base_architecture}
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
