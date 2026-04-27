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
VERSION_ID_MAJOR=$(echo $VERSION_ID | sed 's/\..*//')

# Function to install Connext DDS.
install_connextdds() {
    # We only attempt to install Connext on Ubuntu
    if [ "${ID}" != "ubuntu" ]; then
        echo "Connext installation is only supported on Ubuntu. Skipping Connext installation."
        return 0
    fi

    # Check if the "ignore-rmw" CI argument contains "rmw_connextdds" and exit if it does.
    ignore_rwm_seen="false"
    for arg in ${CI_ARGS} ; do
        case $arg in
            ("--ignore-rmw") ignore_rmw_seen="true" ;;
            ("-"*) ignore_rmw_seen="false" ;;
            (*)
                if [ $ignore_rmw_seen = "true" ] && [ $arg = "rmw_connextdds" ]; then
                    echo "Ignoring installation of Connext."
                    return 0
                fi
                ;;
        esac
    done

    echo "Installing Connext..."
    # Set Connext version, OpenSSL version and base/target architecture variables:
    # - Lyrical/Rolling:
    #     - Version: Connext 7.7.0
    #     - OpenSSL version: 3.5.5
    #     - Base architecture: x64Linux4gcc8.5.0
    #     - Target architecture:
    #         - AMD64: x64Linux4gcc8.5.0
    #         - ARM64: armv8Linux4gcc8.5.0
    # - Kilted:
    #     - Version: Connext 7.3.0
    #     - OpenSSL version: 3.0.12
    #     - Base architecture: x64Linux3gcc4.8.2
    #     - Target architecture: 
    #         - AMD64: x64Linux4gcc7.3.0
    #         - ARM64: armv8Linux4gcc7.3.0
    # - Humble/Jazzy:
    #     - Version: Connext 6.0.1.25
    #     - OpenSSL version: 1.1.1k
    #     - Base architecture: x64Linux2.6gcc4.4.5
    #     - Target architecture: x64Linux4gcc7.3.0
    export CONNEXT_FULL_VERSION="7.7.0"
    export CONNEXT_DISPLAY_VERSION="$CONNEXT_FULL_VERSION"
    export OPENSSL_FULL_VERSION="3.5.5"
    export OPENSSL_DISPLAY_VERSION="${OPENSSL_FULL_VERSION%.*}"
    export CONNEXT_BASE_ARCH="x64Linux4gcc8.5.0"
    export CONNEXT_TARGET_ARCH="$CONNEXT_BASE_ARCH"
    case "${ROS_DISTRO}" in
        lyrical)
            export CONNEXT_FULL_VERSION="7.7.0"
            export CONNEXT_DISPLAY_VERSION="$CONNEXT_FULL_VERSION"
            export OPENSSL_FULL_VERSION="3.5.5"
            export OPENSSL_DISPLAY_VERSION="${OPENSSL_FULL_VERSION%.*}"
            export CONNEXT_BASE_ARCH="x64Linux4gcc8.5.0"
            if [ "${ARCH}" = "x86_64" ]; then
                export CONNEXT_TARGET_ARCH="x64Linux4gcc8.5.0"
            else
                export CONNEXT_TARGET_ARCH="armv8Linux4gcc8.5.0"
            fi
            ;;
        kilted)
            export CONNEXT_FULL_VERSION="7.3.0"
            export CONNEXT_DISPLAY_VERSION="$CONNEXT_FULL_VERSION"
            export OPENSSL_FULL_VERSION="3.0.12"
            export OPENSSL_DISPLAY_VERSION="${OPENSSL_FULL_VERSION%.*}"
            export CONNEXT_BASE_ARCH="x64Linux3gcc4.8.2"
            if [ "${ARCH}" = "x86_64" ]; then
                export CONNEXT_TARGET_ARCH="x64Linux4gcc7.3.0"
            else
                export CONNEXT_TARGET_ARCH="armv8Linux4gcc7.3.0"
            fi
            ;;
        humble|jazzy)
            export CONNEXT_FULL_VERSION="6.0.1.25"
            export CONNEXT_DISPLAY_VERSION="${CONNEXT_FULL_VERSION%.*}"
            export OPENSSL_FULL_VERSION="1.1.1k"
            export CONNEXT_BASE_ARCH="x64Linux2.6gcc4.4.5"
            export CONNEXT_TARGET_ARCH="x64Linux4gcc7.3.0"
            ;;
        *)
            # Rolling case. Nothing to do.
            ;;
    esac

    case "${CI_ARGS}" in
        *--connext-debs*)
            connext_root="/opt/rti.com/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}"
            connext_env_script="${connext_root}/resource/scripts/rtisetenv_${CONNEXT_TARGET_ARCH}.sh"

            # Installing Connext through Debian packages is supported on both x86_64 and aarch64 architectures. If we're on an unsupported architecture, skip the installation.
            echo "Using Debian package of Connext"
            if [ -f "${connext_env_script}" ] && [ -r "${connext_env_script}" ]; then
                echo "Sourcing RTI setenv script ${connext_env_script}"
                . ${connext_env_script}
            else
                echo "No Connext installation through Debian packages found. Skipping Connext installation."
                return 0
            fi
            ;;
        *)
            # Support for installing Connext through the RTI website installers is only supported on
            # x86_64 architecture. If we're on a different architecture, skip the installation.
            if [ "${ARCH}" != "x86_64" ]; then
                echo "Connext through RTI packages is only supported on amd64 architecture. Skipping Connext installation."
                return 0
            fi
            
            # Check if the Connext installer from the RTI website is present and executable. If not, exit with an error.
            if [ ! -x /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}-pro-host-x64Linux.run ]; then
                echo "No connext installation files found found." >&2
                return 1
            fi

            echo "Installing Connext binaries off RTI website..."
            rtipkg_list="\
            /tmp/rticonnextdds-src/openssl-${OPENSSL_FULL_VERSION}-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
            /tmp/rticonnextdds-src/openssl-${OPENSSL_FULL_VERSION}-${CONNEXT_FULL_VERSION}-target-${CONNEXT_TARGET_ARCH}.rtipkg \
            /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-host-openssl-${OPENSSL_DISPLAY_VERSION}-x64Linux.rtipkg \
            /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-target-openssl-${OPENSSL_DISPLAY_VERSION}-${CONNEXT_TARGET_ARCH}.rtipkg \
            "

            if [ "${ROS_DISTRO}" = "humble" ] || [ "${ROS_DISTRO}" = "jazzy" ]; then
                rtipkg_list="\
                /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_FULL_VERSION}-pro-host-x64Linux.rtipkg \
                /tmp/rticonnextdds-src/openssl-${OPENSSL_FULL_VERSION}-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
                /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-host-x64Linux.rtipkg \
                /tmp/rticonnextdds-src/rti_security_plugins-${CONNEXT_FULL_VERSION}-target-${CONNEXT_TARGET_ARCH}.rtipkg \
                "
            fi
            python3 -u /tmp/rti_web_binaries_install_script.py \
                /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}-pro-host-x64Linux.run \
                /home/rosbuild/rti_connext_dds-${CONNEXT_DISPLAY_VERSION} \
                --rtipkg_paths \
                    /tmp/rticonnextdds-src/rti_connext_dds-${CONNEXT_FULL_VERSION}-pro-target-${CONNEXT_TARGET_ARCH}.rtipkg \
                    $rtipkg_list
            if [ $? -ne 0 ]; then
                echo "Connext not installed correctly." >&2
                return 1
            fi
            export CONNEXTDDS_DIR=/home/rosbuild/rti_connext_dds-${CONNEXT_DISPLAY_VERSION}
            export RTI_OPENSSL_LIBS=$CONNEXTDDS_DIR/resource/app/lib/${CONNEXT_BASE_ARCH}
            mv /tmp/rti_license.dat /home/rosbuild/rti_license.dat
            export RTI_LICENSE_FILE=/home/rosbuild/rti_license.dat
            ;;
    esac
    return 0
}

if ! install_connextdds; then
    echo "Connext installation failed. Exiting." >&2
    exit 1
fi
echo "done."

echo "Fixing permissions..."
sed -i -e "s/:$ORIG_UID:$ORIG_GID:/:$UID:$GID:/" /etc/passwd
sed -i -e "s/rosbuild:x:$ORIG_GID:/rosbuild:x:$GID:/" /etc/group

chown -R ${UID}:${GID} "${ORIG_HOME}"
echo "done."

# Use Wayland on RHEL 10
if [ "${ID}" = "almalinux" -a "${VERSION_ID_MAJOR}" = "10" ]; then
    exec sudo -H -u rosbuild -E -- xwfb-run -n99 -s=-ac -s=-geometry -s=1280x1024 -- /bin/sh -c "$*"
else
    exec sudo -H -u rosbuild -E -- xvfb-run -s "-ac -screen 0 1280x1024x24" /bin/sh -c "$*"
fi
